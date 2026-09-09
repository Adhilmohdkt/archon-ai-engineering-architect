from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(archon_router)