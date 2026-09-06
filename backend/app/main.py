from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.API.routes.archon import router as archon_router
from app.graph import initialize_database, close_database


@asynccontextmanager
async def lifespan(app: FastAPI):

    
    await initialize_database()

    yield

    
    await close_database()


app = FastAPI(
    title="Archon AI Engineering Architect",
    description="AI-powered software architecture design system",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(archon_router)