import os
import sys
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Garante que o diretório raiz esteja no sys.path para importar app.cognitive_engine
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.cognitive_engine import analyze_and_reframe

app = FastAPI(
    title="Eu Viro Voto App API",
    description="API Serverless para reenquadramento cognitivo de conversas no 2º turno.",
    version="1.0.0"
)

# Configuração de CORS para permitir acesso web e PWA seguro
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    message: str = ""
    audio_base64: Optional[str] = None

@app.get("/api/health")
@app.get("/api")
@app.get("/health")
async def health_check():
    has_gemini_key = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "status": "online",
        "app": "Eu Viro Voto App",
        "gemini_configured": has_gemini_key
    }

@app.post("/api/analyze")
@app.post("/analyze")
async def analyze_endpoint(payload: AnalyzeRequest):
    if not payload.message and not payload.audio_base64:
        raise HTTPException(status_code=400, detail="Envie uma mensagem de texto ou áudio.")
    
    try:
        result = await analyze_and_reframe(
            user_input=payload.message.strip(),
            audio_base64=payload.audio_base64
        )
        return {
            "status": "success",
            "data": result
        }
    except Exception as exc:
        return {
            "status": "error",
            "detail": str(exc),
            "data": {
                "evite": "Instabilidade momentânea no processamento.",
                "opcao_1": "Poderia tentar novamente em instantes?",
                "opcao_2": "",
                "audio": ""
            }
        }
