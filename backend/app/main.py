from fastapi import FastAPI
from app.API.routes.archon import router as archon_router

app = FastAPI(
    title="Archon AI Engineering Architect",
    description="AI-powered software architecture design system",
    version="1.0.0",
)

app.include_router(archon_router)