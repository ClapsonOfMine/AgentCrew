"""AgentCrew-based chat runtime adapter for Sidonie.

- Multi-agent orchestration with LangGraph
- LLM-powered intent classification with keyword fallback
- Internal-token protected /chat endpoint
- SSE streaming via /chat/stream
- Tenant-scoped prompts for isolation
- CrewAI judge integration for handoff validation
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Literal, Optional, TypedDict

import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

logger = logging.getLogger("agentcrew-adapter")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")

INTERNAL_TOKEN = os.getenv("AGENTCREW_INTERNAL_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
BIND_HOST = os.getenv("AGENTCREW_BIND_HOST", "0.0.0.0")
BIND_PORT = int(os.getenv("AGENTCREW_PORT", "41241"))
CREWAI_JUDGE_URL = os.getenv("CREWAI_SERVICE_URL", "http://127.0.0.1:8000")
CREWAI_INTERNAL_TOKEN = os.getenv("CREWAI_INTERNAL_TOKEN", "")
USE_CREW_JUDGE = os.getenv("USE_CREW_JUDGE", "true").lower() == "true"
USE_LLM_ROUTER = os.getenv("USE_LLM_ROUTER", "true").lower() == "true"

app = FastAPI(title="Sidonie AgentCrew Adapter", version="1.2.0")


# ─────────── Models ───────────

class ChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    agentId: Optional[str] = None


class ChatRequest(BaseModel):
    tenantId: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    history: Optional[List[ChatHistoryItem]] = None
    userRole: Optional[str] = "anonymous"
    userId: Optional[str] = None
    previousAgent: Optional[str] = None


class AgentProfile(BaseModel):
    id: str
    firstName: str
    icon: str
    color: str
    tone: str


class ChatResponse(BaseModel):
    tenantId: str
    agent: AgentProfile
    handoff: Optional[str] = None
    text: str


# ─────────── Agent profiles ───────────

AGENTS: Dict[str, AgentProfile] = {
    "Accueil": AgentProfile(id="Accueil", firstName="Chloé", icon="\U0001f496", color="#FFB6C1", tone="accueil"),
    "CoursExpert": AgentProfile(id="CoursExpert", firstName="Sophie", icon="\U0001f393", color="#9370DB", tone="formations"),
    "RDVBooker": AgentProfile(id="RDVBooker", firstName="Emma", icon="\U0001f4f1", color="#32CD32", tone="rdv"),
    "BlogLover": AgentProfile(id="BlogLover", firstName="Léa", icon="\U0001f4dd", color="#FF69B4", tone="blog"),
    "SupportHero": AgentProfile(id="SupportHero", firstName="Marie", icon="\U0001f6e0\ufe0f", color="#FFA500", tone="support"),
}

AGENT_FALLBACK_TEXT: Dict[str, str] = {
    "Accueil": "Bienvenue chez Sidonie Nail Academy \U0001f496 Dis-moi ton besoin (formation, RDV, blog ou support) et je t'oriente.",
    "CoursExpert": "Je peux t'expliquer les parcours, tarifs et niveaux de formation \U0001f393 Dis-moi ton objectif.",
    "RDVBooker": "Je peux t'aider à préparer un RDV \U0001f4f1 Donne-moi le service souhaité et tes disponibilités.",
    "BlogLover": "Je peux te proposer des idées et conseils nail art \U0001f4dd Dis-moi le style qui t'intéresse.",
    "SupportHero": "Je prends ton sujet en charge \U0001f6e0\ufe0f Donne-moi les détails pour qu'on le résolve rapidement.",
}

AGENT_EXPERTISE: Dict[str, str] = {
    "Accueil": (
        "Tu es l'hôtesse d'accueil. Identifie le besoin du client et oriente-le vers "
        "le bon service : formations (Sophie), rendez-vous (Emma), blog (Léa) ou support (Marie). "
        "Si le besoin est clair, précise vers qui tu le diriges."
    ),
    "CoursExpert": (
        "Tu es experte en formations onglerie. Tu présentes les parcours, niveaux, tarifs, "
        "calendrier et certifications de Sidonie Nail Academy."
    ),
    "RDVBooker": (
        "Tu gères la prise de rendez-vous. Demande le type de soin/service souhaité, "
        "la date/heure préférée, et guide le client pour finaliser son créneau. "
        "Tu peux proposer les créneaux disponibles."
    ),
    "BlogLover": (
        "Tu es passionnée de nail art et contenu. Tu proposes des articles, tutos, "
        "tendances et conseils beauté du blog Sidonie."
    ),
    "SupportHero": (
        "Tu gères le support client. Tu traites les réclamations, litiges, "
        "remboursements et problèmes techniques avec empathie et efficacité."
    ),
}


# ─────────── Intent routing ───────────

INTENT_TO_AGENT: Dict[str, str] = {
    "support": "SupportHero",
    "rdv": "RDVBooker",
    "blog": "BlogLover",
    "cours": "CoursExpert",
    "accueil": "Accueil",
}

ROUTER_SYSTEM_PROMPT = """Tu es un routeur d'intentions pour le chatbot Sidonie Nail Academy.
Classe chaque message utilisateur dans UNE seule catégorie :

- support : litiges, remboursements, plaintes, mécontentement, problèmes de paiement, réclamations, insatisfaction implicite, problèmes techniques.
- rdv : prise / modification / annulation de rendez-vous, disponibilités, créneaux, booking.
- blog : demandes d'articles, tutos, inspirations, nail art, tendances beauté.
- cours : formations, programmes, tarifs de formation, inscriptions, niveaux, certifications, diplômes.
- accueil : tout le reste, small talk, questions générales, salutations.

Si tu n'es pas sûr, renvoie "accueil".
Réponds UNIQUEMENT par un JSON de la forme : {"intent": "xxx"}
N'ajoute aucun autre texte."""

ROUTER_FEW_SHOTS: List[Dict[str, str]] = [
    {"role": "user", "content": "Bonjour, comment ça va ?"},
    {"role": "assistant", "content": '{"intent": "accueil"}'},
    {"role": "user", "content": "Je veux prendre rendez-vous pour une manucure jeudi"},
    {"role": "assistant", "content": '{"intent": "rdv"}'},
    {"role": "user", "content": "Mon paiement a été prélevé deux fois, c'est inadmissible !"},
    {"role": "assistant", "content": '{"intent": "support"}'},
    {"role": "user", "content": "Quelles formations proposez-vous en nail art ?"},
    {"role": "assistant", "content": '{"intent": "cours"}'},
    {"role": "user", "content": "Tu as des tutos pour faire du nail art marbré ?"},
    {"role": "assistant", "content": '{"intent": "blog"}'},
    {"role": "user", "content": "J'en ai marre de vos services, je veux être remboursée"},
    {"role": "assistant", "content": '{"intent": "support"}'},
    {"role": "user", "content": "Est-ce que je peux modifier mon créneau de samedi ?"},
    {"role": "assistant", "content": '{"intent": "rdv"}'},
    {"role": "user", "content": "Quel est le prix de la formation débutant ?"},
    {"role": "assistant", "content": '{"intent": "cours"}'},
]


def route_intent(message: str) -> str:
    """Keyword-based intent router (fallback). Returns agent name."""
    lowered = message.lower()
    if any(kw in lowered for kw in [
        "litige", "rembours", "plainte", "problème", "probleme",
        "urgent", "réclamation", "reclamation", "arnaque", "inadmissible",
        "inacceptable", "prélevé", "preleve", "prélèvement", "prelevement",
        "facture", "paiement", "payé", "paye", "trop perçu", "erreur de",
        "double", "surcharge", "contestation", "mécontente", "mecontent",
        "scandale", "vol", "escroquer",
    ]):
        return "SupportHero"
    if any(kw in lowered for kw in [
        "rendez-vous", "rdv", "book", "créneau", "creneau",
        "disponibilit", "horaire", "réserv", "reserv", "planning",
        "prendre un", "calendrier",
    ]):
        return "RDVBooker"
    if any(kw in lowered for kw in [
        "blog", "article", "tuto", "conseil", "astuce",
        "tendance", "inspiration", "nail art",
    ]):
        return "BlogLover"
    if any(kw in lowered for kw in [
        "formation", "cours", "programme", "certif", "prix",
        "tarif", "galerie", "niveau", "diplôme", "diplome",
        "apprentissage", "inscription",
    ]):
        return "CoursExpert"
    return "Accueil"


def classify_intent_llm(message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
    """Classify user intent via OpenAI LLM. Returns: support|rdv|blog|cours|accueil."""
    if not OPENAI_API_KEY:
        return "accueil"

    messages: List[Dict[str, str]] = [{"role": "system", "content": ROUTER_SYSTEM_PROMPT}]
    messages.extend(ROUTER_FEW_SHOTS)

    # Include last 3 history messages for context
    if history:
        for h in history[-3:]:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})

    messages.append({"role": "user", "content": message})

    start = time.monotonic()
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENAI_MODEL,
                    "temperature": 0,
                    "max_tokens": 30,
                    "messages": messages,
                },
            )
        elapsed_ms = int((time.monotonic() - start) * 1000)

        if resp.status_code != 200:
            logger.warning("[llm-router] OpenAI HTTP %d — fallback keywords", resp.status_code)
            return "accueil"

        data = resp.json()
        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        logger.info(
            "[llm-router] intent_raw=%r tokens=%d+%d elapsed=%dms",
            content, prompt_tokens, completion_tokens, elapsed_ms,
        )

        parsed = json.loads(content)
        intent = parsed.get("intent", "accueil").lower().strip()

        if intent in INTENT_TO_AGENT:
            return intent

        logger.warning("[llm-router] unknown intent=%r — fallback accueil", intent)
        return "accueil"

    except (json.JSONDecodeError, KeyError, IndexError) as exc:
        logger.warning("[llm-router] parse error: %s — fallback keywords", exc)
        return "accueil"
    except Exception as exc:
        logger.warning("[llm-router] LLM error: %s — fallback keywords", exc)
        return "accueil"


async def classify_intent_llm_async(message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
    """Async version of classify_intent_llm for streaming endpoints."""
    if not OPENAI_API_KEY:
        return "accueil"

    messages: List[Dict[str, str]] = [{"role": "system", "content": ROUTER_SYSTEM_PROMPT}]
    messages.extend(ROUTER_FEW_SHOTS)

    if history:
        for h in history[-3:]:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})

    messages.append({"role": "user", "content": message})

    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENAI_MODEL,
                    "temperature": 0,
                    "max_tokens": 30,
                    "messages": messages,
                },
            )
        elapsed_ms = int((time.monotonic() - start) * 1000)

        if resp.status_code != 200:
            logger.warning("[llm-router-async] OpenAI HTTP %d — fallback keywords", resp.status_code)
            return "accueil"

        data = resp.json()
        usage = data.get("usage", {})
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        logger.info(
            "[llm-router-async] intent_raw=%r tokens=%d+%d elapsed=%dms",
            content, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0), elapsed_ms,
        )

        parsed = json.loads(content)
        intent = parsed.get("intent", "accueil").lower().strip()
        return intent if intent in INTENT_TO_AGENT else "accueil"

    except Exception as exc:
        logger.warning("[llm-router-async] error: %s — fallback keywords", exc)
        return "accueil"


def route_message(message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
    """Hybrid router: LLM classification first, keyword fallback.

    Returns agent name: SupportHero, RDVBooker, BlogLover, CoursExpert, Accueil.
    """
    keyword_result = route_intent(message)

    if not USE_LLM_ROUTER:
        logger.info("[router] LLM disabled → keywords=%s", keyword_result)
        return keyword_result

    llm_intent = classify_intent_llm(message, history)
    llm_agent = INTENT_TO_AGENT.get(llm_intent, "Accueil")

    # Safety net: if LLM says accueil but keywords found specific agent, trust keywords
    if llm_agent == "Accueil" and keyword_result != "Accueil":
        logger.info("[router] LLM=accueil keywords=%s → promoting keywords", keyword_result)
        return keyword_result

    if llm_agent == keyword_result:
        logger.info("[router] LLM+keywords agree → %s", llm_agent)
    else:
        logger.info("[router] LLM=%s keywords=%s → using LLM", llm_agent, keyword_result)

    return llm_agent


async def route_message_async(message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
    """Async version of route_message for streaming endpoints."""
    keyword_result = route_intent(message)

    if not USE_LLM_ROUTER:
        return keyword_result

    llm_intent = await classify_intent_llm_async(message, history)
    llm_agent = INTENT_TO_AGENT.get(llm_intent, "Accueil")

    if llm_agent == "Accueil" and keyword_result != "Accueil":
        logger.info("[router-async] LLM=accueil keywords=%s → promoting keywords", keyword_result)
        return keyword_result

    if llm_agent != keyword_result:
        logger.info("[router-async] LLM=%s keywords=%s → using LLM", llm_agent, keyword_result)

    return llm_agent


# ─────────── LangGraph state & nodes ───────────

class AgentState(TypedDict):
    tenant_id: str
    user_role: str
    message: str
    history: List[Dict[str, str]]
    previous_agent: str
    routed_agent: str
    handoff_summary: str
    response_text: str


def _build_handoff(previous_agent: str, routed_agent: str, message: str) -> str:
    if previous_agent == routed_agent:
        return ""
    return f"Résumé transmis de {AGENTS[previous_agent].firstName} vers {AGENTS[routed_agent].firstName}: {message.strip()}"


def _llm() -> ChatOpenAI:
    return ChatOpenAI(model=OPENAI_MODEL, temperature=0.7, openai_api_key=OPENAI_API_KEY)


def _agent_node(agent_id: str):
    def run(state: AgentState) -> AgentState:
        profile = AGENTS[agent_id]
        history_text = "\n".join([f"{h['role']}: {h['content']}" for h in state["history"][-8:]])
        is_guest = state["user_role"] == "anonymous"

        expertise = AGENT_EXPERTISE.get(agent_id, "")
        system_prompt = (
            f"Tu es {profile.firstName} ({profile.id}) pour Sidonie Nail Academy. "
            f"{expertise} "
            f"Contrainte de sécurité: tu réponds uniquement pour tenant_id={state['tenant_id']}. "
            "Aucune donnée cross-tenant. "
            + ("Mode invité: pas de RAG, pas d'action externe, mais tu peux répondre et orienter. " if is_guest else "")
            + "Réponds en français, concis (max 120 mots), utile, naturel."
        )

        try:
            llm = _llm()
            response = llm.invoke(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Contexte: {history_text}\nMessage: {state['message']}"},
                ]
            )
            text = str(response.content).strip() if response and response.content else "Je suis là pour t'aider."
        except Exception as exc:
            logger.error("[agent_node:%s] LLM error: %s", agent_id, exc)
            text = AGENT_FALLBACK_TEXT.get(agent_id, "Je suis là pour t'aider.")

        state["response_text"] = text
        return state

    return run


def _router_node(state: AgentState) -> AgentState:
    """Route using hybrid LLM + keyword intent detection."""
    routed = route_message(state["message"], state["history"])
    state["routed_agent"] = routed
    state["handoff_summary"] = _build_handoff(state["previous_agent"], routed, state["message"])
    logger.info(
        "[router] user_role=%s message=%r → routed=%s (prev=%s)",
        state["user_role"], state["message"][:80], routed, state["previous_agent"],
    )
    return state


def _next_agent(state: AgentState) -> str:
    return state["routed_agent"]


def _build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("router", _router_node)
    graph.add_node("Accueil", _agent_node("Accueil"))
    graph.add_node("CoursExpert", _agent_node("CoursExpert"))
    graph.add_node("RDVBooker", _agent_node("RDVBooker"))
    graph.add_node("BlogLover", _agent_node("BlogLover"))
    graph.add_node("SupportHero", _agent_node("SupportHero"))

    graph.set_entry_point("router")
    graph.add_conditional_edges(
        "router",
        _next_agent,
        {
            "Accueil": "Accueil",
            "CoursExpert": "CoursExpert",
            "RDVBooker": "RDVBooker",
            "BlogLover": "BlogLover",
            "SupportHero": "SupportHero",
        },
    )
    graph.add_edge("Accueil", END)
    graph.add_edge("CoursExpert", END)
    graph.add_edge("RDVBooker", END)
    graph.add_edge("BlogLover", END)
    graph.add_edge("SupportHero", END)
    return graph.compile()


CHAT_GRAPH = _build_graph()


@app.middleware("http")
async def verify_internal_token(request: Request, call_next):
    if INTERNAL_TOKEN and (
        request.url.path.startswith("/chat")
    ):
        token = request.headers.get("X-Internal-Token", "")
        if token != INTERNAL_TOKEN:
            return JSONResponse(status_code=401, content={"detail": "Invalid internal token"})
    return await call_next(request)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "agentcrew-adapter"}


# ─────────── Judge integration ───────────

async def _invoke_judge(
    tenant_id: str,
    from_agent: str,
    to_agent: str,
    user_message: str,
    handoff_summary: str,
) -> Dict[str, Any]:
    """Call CrewAI judge to validate handoff. Returns judge result or auto-approve on failure."""
    if not USE_CREW_JUDGE:
        return {"approved": True, "score": 1.0, "feedback": "judge disabled"}

    headers: Dict[str, str] = {"Content-Type": "application/json"}
    if CREWAI_INTERNAL_TOKEN:
        headers["X-Internal-Token"] = CREWAI_INTERNAL_TOKEN
    headers["X-Tenant-Id"] = tenant_id

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{CREWAI_JUDGE_URL.rstrip('/')}/judge",
                json={
                    "tenantId": tenant_id,
                    "fromAgent": from_agent,
                    "toAgent": to_agent,
                    "userMessage": user_message,
                    "fallbackSummary": handoff_summary,
                },
                headers=headers,
            )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    return {"approved": True, "score": 0.8, "feedback": "judge fallback (unreachable)"}


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, x_tenant_id: Optional[str] = Header(None)):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")

    if x_tenant_id and x_tenant_id != payload.tenantId:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")

    if payload.previousAgent and payload.previousAgent in AGENTS:
        previous_agent = payload.previousAgent
    else:
        previous_agent = "Accueil"

    history = [
        {"role": h.role, "content": h.content, "agentId": h.agentId or ""}
        for h in (payload.history or [])
    ]

    initial_state: AgentState = {
        "tenant_id": payload.tenantId,
        "user_role": payload.userRole or "anonymous",
        "message": payload.message,
        "history": history,
        "previous_agent": previous_agent,
        "routed_agent": "Accueil",
        "handoff_summary": "",
        "response_text": "",
    }

    try:
        result = CHAT_GRAPH.invoke(initial_state)
        routed_agent = result["routed_agent"]

        # Judge validation on handoff
        if routed_agent != previous_agent and USE_CREW_JUDGE:
            judge_result = await _invoke_judge(
                payload.tenantId,
                previous_agent,
                routed_agent,
                payload.message,
                result.get("handoff_summary", ""),
            )
            if not judge_result.get("approved", True):
                routed_agent = previous_agent

        return ChatResponse(
            tenantId=payload.tenantId,
            agent=AGENTS[routed_agent],
            handoff=result.get("handoff_summary") or None,
            text=result.get("response_text") or "Je suis là pour t'aider.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AgentCrew adapter error: {exc}")


# ─────────── SSE Streaming endpoint ───────────

@app.post("/chat/stream")
async def chat_stream(payload: ChatRequest, x_tenant_id: Optional[str] = Header(None)):
    """SSE streaming version of /chat. Uses async LLM router for intent detection."""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")

    if x_tenant_id and x_tenant_id != payload.tenantId:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")

    if payload.previousAgent and payload.previousAgent in AGENTS:
        previous_agent = payload.previousAgent
    else:
        previous_agent = "Accueil"

    history = [
        {"role": h.role, "content": h.content, "agentId": h.agentId or ""}
        for h in (payload.history or [])
    ]

    routed = await route_message_async(payload.message, history)
    agent_profile = AGENTS.get(routed, AGENTS["Accueil"])
    logger.info("[stream] user_role=%s routed=%s", payload.userRole, routed)

    async def generate():
        yield f"data: {json.dumps({'type': 'meta', 'agent': agent_profile.model_dump(), 'handoff': None})}\n\n"

        is_guest = (payload.userRole or "anonymous") == "anonymous"
        expertise = AGENT_EXPERTISE.get(routed, "")
        system_prompt = (
            f"Tu es {agent_profile.firstName} ({agent_profile.id}) pour Sidonie Nail Academy. "
            f"{expertise} "
            f"Contrainte de sécurité: tu réponds uniquement pour tenant_id={payload.tenantId}. "
            "Aucune donnée cross-tenant. "
            + ("Mode invité: pas de RAG, pas d'action externe, mais tu peux répondre et orienter. " if is_guest else "")
            + "Réponds en français, concis (max 120 mots), naturel et utile."
        )

        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-8:]:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": payload.message})

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": OPENAI_MODEL,
                        "temperature": 0.7,
                        "stream": True,
                        "messages": messages,
                    },
                ) as resp:
                    if resp.status_code != 200:
                        yield f"data: {json.dumps({'type': 'chunk', 'content': 'Désolée, une erreur est survenue \U0001f64f'})}\n\n"
                    else:
                        async for line in resp.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data_str)
                                delta = chunk.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content")
                                if content:
                                    yield f"data: {json.dumps({'type': 'chunk', 'content': content})}\n\n"
                            except (json.JSONDecodeError, IndexError, KeyError):
                                continue
        except Exception:
            yield f"data: {json.dumps({'type': 'chunk', 'content': 'Désolée, une erreur est survenue \U0001f64f'})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=BIND_HOST, port=BIND_PORT, log_level="info")
