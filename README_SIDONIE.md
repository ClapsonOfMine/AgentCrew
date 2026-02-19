# AgentCrew Fork Integration (Sidonie)

Ce dossier contient le fork demandé d'AgentCrew: `saigontechnology/AgentCrew`.

## Objectif
- Exécuter AgentCrew en mode A2A server pour une migration progressive.
- Garder le runtime existant stable pendant la bascule.

## Démarrage local
```bash
cd backend/agentcrew
uv sync
uv run agentcrew a2a-server --host 0.0.0.0 --port 41241
```

## Démarrage Docker (recommandé)
Le service `agentcrew-a2a` est défini dans `docker-compose.yml` sous le profile `agentcrew`.
Il exécute l'adaptateur `sidonie_agentcrew_adapter.py` (LangGraph + endpoint `/chat`).

```bash
docker compose --profile agentcrew up -d agentcrew-a2a
```

## Notes sécurité
- Le template `agents.toml.j2` est prêt pour injection tenant.
- Le endpoint A2A est interne (`127.0.0.1:41241`) pour limiter l’exposition.
- Le backend applicatif peut être migré progressivement vers ce runtime.
