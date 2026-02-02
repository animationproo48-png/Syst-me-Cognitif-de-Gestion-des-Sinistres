import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure backend modules are importable
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from backend.database import init_db, get_db_connection
from backend.routers import clients, conversation, audio, advisor, emotions
from backend.routers import operations
from backend.seeds.seed_data import seed_all

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Créer répertoires
Path("data/audio_responses").mkdir(parents=True, exist_ok=True)
Path("data/uploads").mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown events"""
    logger.info("[*] Server starting...")
    
    if get_db_connection():
        logger.info("[OK] Database connection OK")
        init_db()
    else:
        logger.warning("[!] Database connection failed")
    
    try:
        seed_all()
    except Exception as e:
        logger.info(f"[!] Seed: {e}")
    
    yield
    
    logger.info("[*] Server shutting down...")


app = FastAPI(
    title="Insurance CRM API",
    description="API Production CRM assurance avec conversation IA",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Audio serving - use absolute path to project root
project_root = Path(__file__).parent.parent
audio_dir = project_root / "data" / "audio_responses"
audio_dir.mkdir(parents=True, exist_ok=True)


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Servir fichiers audio"""
    file_path = audio_dir / filename
    if file_path.exists():
        return FileResponse(file_path, media_type="audio/mpeg")
    return JSONResponse({"error": f"Not found: {file_path}"}, status_code=404)


@app.get("/health")
async def health():
    """Health check"""
    db_ok = get_db_connection()
    return {
        "status": "✅ Online" if db_ok else "⚠️ Degraded",
        "version": "1.0.0",
        "database": "✅ OK" if db_ok else "❌ Error"
    }


# Routes
app.include_router(clients.router)
app.include_router(conversation.router)
app.include_router(audio.router)
app.include_router(advisor.router)
app.include_router(emotions.router)
app.include_router(operations.router)


@app.get("/")
async def root():
    """API info"""
    return {
        "name": "Insurance CRM API v1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "clients": "/api/v1/clients",
            "conversation": "/ws/conversation/{session_id}"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global error handler"""
    logger.error(f"❌ Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
# ===== ENDPOINTS DÉCLARATION SINISTRE =====

