"""AgentCrew-based chat runtime adapter for Sidonie.

- Multi-agent orchestration with LangGraph
- Internal-token protected /chat endpoint
- Tenant-scoped prompts for isolation
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Literal, Optional, TypedDict

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

INTERNAL_TOKEN = os.getenv("AGENTCREW_INTERNAL_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
BIND_HOST = os.getenv("AGENTCREW_BIND_HOST", "0.0.0.0")
BIND_PORT = int(os.getenv("AGENTCREW_PORT", "41241"))

app = FastAPI(title="Sidonie AgentCrew Adapter", version="1.0.0")


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
    if INTERNAL_TOKEN and request.url.path.startswith("/chat"):
        token = request.headers.get("X-Internal-Token", "")
        if token != INTERNAL_TOKEN:
            return JSONResponse(status_code=401, content={"detail": "Invalid internal token"})
    return await call_next(request)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "agentcrew-adapter"}


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
        return ChatResponse(
            tenantId=payload.tenantId,
            agent=AGENTS[routed_agent],
            handoff=result.get("handoff_summary") or None,
            text=result.get("response_text") or "Je suis là pour t'aider.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AgentCrew adapter error: {exc}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=BIND_HOST, port=BIND_PORT, log_level="info")
