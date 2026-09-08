from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from api.routes import router as api_router

app = FastAPI(
    title="Autonomous Research Agent API",
    description="Backend API for managing multi-agent LangGraph research workflows.",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus /metrics ASGI endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def health_check():
    return {"status": "ok", "service": "research-agent-api"}
