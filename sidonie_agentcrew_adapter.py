"""AgentCrew-based chat runtime adapter for Sidonie.

- Multi-agent orchestration with LangGraph
- Internal-token protected /chat endpoint
- SSE streaming via /chat/stream
- Tenant-scoped prompts for isolation
- CrewAI judge integration for handoff validation
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Any, Dict, List, Literal, Optional, TypedDict

import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

INTERNAL_TOKEN = os.getenv("AGENTCREW_INTERNAL_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
BIND_HOST = os.getenv("AGENTCREW_BIND_HOST", "0.0.0.0")
BIND_PORT = int(os.getenv("AGENTCREW_PORT", "41241"))
CREWAI_JUDGE_URL = os.getenv("CREWAI_SERVICE_URL", "http://127.0.0.1:8000")
CREWAI_INTERNAL_TOKEN = os.getenv("CREWAI_INTERNAL_TOKEN", "")
USE_CREW_JUDGE = os.getenv("USE_CREW_JUDGE", "true").lower() == "true"

app = FastAPI(title="Sidonie AgentCrew Adapter", version="1.1.0")


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


AGENTS: Dict[str, AgentProfile] = {
    "Accueil": AgentProfile(id="Accueil", firstName="Chloé", icon="💖", color="#FFB6C1", tone="accueil"),
    "CoursExpert": AgentProfile(id="CoursExpert", firstName="Sophie", icon="🎓", color="#9370DB", tone="formations"),
    "RDVBooker": AgentProfile(id="RDVBooker", firstName="Emma", icon="📱", color="#32CD32", tone="rdv"),
    "BlogLover": AgentProfile(id="BlogLover", firstName="Léa", icon="📝", color="#FF69B4", tone="blog"),
    "SupportHero": AgentProfile(id="SupportHero", firstName="Marie", icon="🛠️", color="#FFA500", tone="support"),
}

AGENT_FALLBACK_TEXT: Dict[str, str] = {
    "Accueil": "Bienvenue chez Sidonie Nail Academy 💖 Dis-moi ton besoin (formation, RDV, blog ou support) et je t'oriente.",
    "CoursExpert": "Je peux t'expliquer les parcours, tarifs et niveaux de formation 🎓 Dis-moi ton objectif.",
    "RDVBooker": "Je peux t'aider à préparer un RDV 📱 Donne-moi le service souhaité et tes disponibilités.",
    "BlogLover": "Je peux te proposer des idées et conseils nail art 📝 Dis-moi le style qui t'intéresse.",
    "SupportHero": "Je prends ton sujet en charge 🛠️ Donne-moi les détails pour qu'on le résolve rapidement.",
}


def route_intent(message: str) -> str:
    lowered = message.lower()
    if any(kw in lowered for kw in ["litige", "remboursement", "plainte", "problème", "urgent", "réclamation"]):
        return "SupportHero"
    if any(kw in lowered for kw in ["rendez-vous", "rdv", "book", "créneau", "disponibilit", "horaire"]):
        return "RDVBooker"
    if any(kw in lowered for kw in ["blog", "article", "tuto", "conseil", "astuce"]):
        return "BlogLover"
    if any(kw in lowered for kw in ["formation", "cours", "programme", "certif", "prix", "tarif", "galerie"]):
        return "CoursExpert"
    return "Accueil"


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

        system_prompt = (
            f"Tu es {profile.firstName} ({profile.id}) pour Sidonie Nail Academy. "
            f"Contrainte de sécurité: tu réponds uniquement pour tenant_id={state['tenant_id']}. "
            "Aucune donnée cross-tenant. "
            + ("Mode invité: triage uniquement, pas de RAG, pas d'action externe. " if is_guest else "")
            + "Réponds en français, concis, utile, naturel."
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
        except Exception:
            text = AGENT_FALLBACK_TEXT.get(agent_id, "Je suis là pour t'aider.")

        state["response_text"] = text
        return state

    return run


def _router_node(state: AgentState) -> AgentState:
    routed = route_intent(state["message"])
    if state["user_role"] == "anonymous":
        routed = "Accueil"
    state["routed_agent"] = routed
    state["handoff_summary"] = _build_handoff(state["previous_agent"], routed, state["message"])
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

    # Auto-approve on failure
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
                routed_agent = previous_agent  # Keep current agent

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
    """SSE streaming version of /chat. Emits meta → chunk* → done events.

    Uses LangGraph routing + CrewAI judge validation before streaming the LLM response.
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")

    if x_tenant_id and x_tenant_id != payload.tenantId:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")

    if payload.previousAgent and payload.previousAgent in AGENTS:
        previous_agent = payload.previousAgent
    else:
        previous_agent = "Accueil"

    # --- Routing via LangGraph (same as /chat) ---
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

    # Run only the router node to determine the agent (don't run the LLM node — we'll stream it)
    routed = route_intent(payload.message)
    if (payload.userRole or "anonymous") == "anonymous":
        routed = "Accueil"
    handoff_summary = _build_handoff(previous_agent, routed, payload.message)

    # --- Judge validation on handoff ---
    if routed != previous_agent and USE_CREW_JUDGE:
        judge_result = await _invoke_judge(
            payload.tenantId,
            previous_agent,
            routed,
            payload.message,
            handoff_summary,
        )
        if not judge_result.get("approved", True):
            routed = previous_agent  # Judge rejected handoff, keep current agent
            handoff_summary = ""

    agent_profile = AGENTS.get(routed, AGENTS["Accueil"])

    async def generate():
        # 1. Meta event (includes agent + handoff info)
        meta = {"type": "meta", "agent": agent_profile.model_dump()}
        if handoff_summary:
            meta["handoff"] = handoff_summary
        else:
            meta["handoff"] = None
        yield f"data: {json.dumps(meta)}\n\n"

        # 2. LLM streaming via OpenAI
        is_guest = (payload.userRole or "anonymous") == "anonymous"
        system_prompt = (
            f"Tu es {agent_profile.firstName} ({agent_profile.id}) pour Sidonie Nail Academy. "
            f"Contrainte de sécurité: tu réponds uniquement pour tenant_id={payload.tenantId}. "
            "Aucune donnée cross-tenant. "
            + ("Mode invité: triage uniquement, pas d'action externe. " if is_guest else "")
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
                        err_msg = "Désolée, une erreur est survenue"
                        yield f"data: {json.dumps({'type': 'chunk', 'content': err_msg + ' 🙏'})}\n\n"
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
            err_msg = "Désolée, une erreur est survenue"
            yield f"data: {json.dumps({'type': 'chunk', 'content': err_msg + ' 🙏'})}\n\n"

        # 3. Done event
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
