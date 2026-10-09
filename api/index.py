import os
import sys
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Garante caminhos no sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for p in [current_dir, parent_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Importação defensiva e resiliente do motor cognitivo
analyze_and_reframe = None
engine_load_error = None

try:
    from api.cognitive_engine import analyze_and_reframe
except Exception as e1:
    try:
        from cognitive_engine import analyze_and_reframe
    except Exception as e2:
        try:
            from app.cognitive_engine import analyze_and_reframe
        except Exception as e3:
            engine_load_error = f"Falha ao carregar motor cognitivo: e1={e1}, e2={e2}, e3={e3}"

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
        "gemini_configured": has_gemini_key,
        "engine_ready": analyze_and_reframe is not None,
        "engine_error": engine_load_error
    }

@app.post("/api/analyze")
@app.post("/analyze")
async def analyze_endpoint(payload: AnalyzeRequest):
    if not payload.message and not payload.audio_base64:
        raise HTTPException(status_code=400, detail="Envie uma mensagem de texto ou áudio.")

    if analyze_and_reframe is None:
        return {
            "status": "error",
            "detail": engine_load_error or "Motor cognitivo indisponível.",
            "data": {
                "evite": "Instabilidade no carregamento do motor de IA.",
                "opcao_1": "O servidor está inicializando os módulos cognitivos. Tente novamente em instantes.",
                "opcao_2": "",
                "audio": ""
            }
        }

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return {
            "status": "error",
            "detail": "GEMINI_API_KEY não configurada nas variáveis de ambiente da Vercel.",
            "data": {
                "evite": "Chave GEMINI_API_KEY ausente na Vercel.",
                "opcao_1": "Por favor, cadastre a GEMINI_API_KEY no painel da Vercel (Settings > Environment Variables).",
                "opcao_2": "",
                "audio": ""
            }
        }

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
                "opcao_1": "Poderia tentar novamente em instantes? Tive uma oscilação rápida.",
                "opcao_2": "",
                "audio": ""
            }
        }
