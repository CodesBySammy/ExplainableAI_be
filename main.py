from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from api.webhook_receiver import router as webhook_router
from api.repo_manager import router as repo_router
from api.auth import router as auth_router
from core.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown events."""
    logger.info("🚀 PReview server starting up...")
    yield
    logger.info("🛑 PReview server shutting down.")

app = FastAPI(
    title="PReview",
    description="AI-powered pull request reviews with explainable risk analysis",
    version="2.0.0",
    lifespan=lifespan,
)

# Allow the Vercel frontend to make authenticated API requests
from core.config import settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)
app.include_router(repo_router)
app.include_router(auth_router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0", "message": "PReview server is running."}

# Mount the frontend directory to serve static files at the root
# IMPORTANT: This must be at the bottom so it doesn't override API endpoints
import os
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
