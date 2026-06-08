from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.approvals import router as approvals_router
from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.tickets import router as tickets_router
from app.api.routes.workspaces import router as workspaces_router
from app.core.config import settings

app = FastAPI(
    title="AgentDesk API",
    description="Production-style AI support agent platform backend.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "agentdesk-api",
        "environment": settings.app_env,
    }


app.include_router(workspaces_router)
app.include_router(documents_router)
app.include_router(tickets_router)
app.include_router(chat_router)
app.include_router(approvals_router)
