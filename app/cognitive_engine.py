import os
import json
import requests
from typing import Dict, Any, Optional

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_INSTRUCTION = """Você é o Eu Viro Voto, um copiloto tático de WhatsApp para virada de votos no 2º turno.
Sua missão é gerar respostas PRONTAS, CURTAS e DIRETAS para o voluntário copiar e colar.

DIRETRIZES TÁTICAS (NÃO EXPLIQUE TEORIA, VÁ DIRETO AO PONTO):
1. Se a pessoa diz "odeio o PT", "não voto no PT" ou é eleitor de 3ª via:
   - NUNCA defenda o PT nem tente fazer a pessoa gostar do Lula.
   - Fale do Flávio Bolsonaro usando PERGUNTAS desarmadoras (pesquisas comprovam que perguntas desarmam e acusações fecham ouvidos).
   - Use os 3 pontos fracos comprovados dele:
     * Quase 30 anos na política sem aprovar nada relevante pelo país (nepo baby / filho do pai).
     * Capacho do Trump (vai taxar produtos brasileiros e prejudicar o agronegócio que exporta pro mundo todo).
     * Não é confiável (negou conhecer o banqueiro Vorcaro e dias depois vazou áudio chamando de 'irmãozão' e pedindo dinheiro).
2. Se a pessoa falar em "salvar o Brasil":
   - Mostre que salvar o Brasil é ter comida barata no prato, paz para trabalhar e não entregar riquezas nacionais para os EUA.
3. Se for idoso (70+) ou desanimado:
   - Fale com afeto sobre Farmácia Popular, aumento real da aposentadoria, o descaso da pandemia e ofereça ajuda prática (carona no domingo).
4. Se for beneficiário de programas sociais:
   - Pergunte se acham que o Flávio entende a realidade deles e se vai manter os programas.

REGRAS DE ESTILO (CRÍTICO):
- MENSAGENS CURTAS: no máximo 2 ou 3 frases cada opção.
- Linguagem 100% natural de WhatsApp brasileiro (ex: "cara", "super te entendo", "ó", "olha só", "me diz uma coisa").
- NUNCA cite teorias, autores, enquadramentos ou jargões acadêmicos.
- Opção 1 e Opção 2 devem ser o texto PURO para ser enviado ao eleitor, sem aspas e sem cabeçalhos.

Você DEVE responder ESTRITAMENTE em formato JSON com as 4 chaves abaixo:
{
  "evite": "1 frase curta com o que NÃO responder de jeito nenhum",
  "opcao_1": "Texto puro da primeira resposta (pergunta suave / família)",
  "opcao_2": "Texto puro da segunda resposta (mais firme / colega ou grupo)",
  "audio": "1 frase rápida e espontânea para mandar em áudio de 10 segundos"
}
"""

MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.5-flash"]

async def analyze_and_reframe(user_input: str, audio_base64: Optional[str] = None) -> Dict[str, str]:
    """
    Analisa o texto ou áudio recebido e devolve um dicionário com os campos fracionados.
    """
    apiKey = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
    if not apiKey:
        return {
            "evite": "Servidor sem chave de IA configurada.",
            "opcao_1": "Erro de configuração no servidor.",
            "opcao_2": "",
            "audio": ""
        }

    # Monta o conteúdo (texto ou áudio multimodal)
    parts = []
    if audio_base64:
        clean_b64 = audio_base64.split(",")[-1] if "," in audio_base64 else audio_base64
        parts.append({
            "inline_data": {
                "mime_type": "audio/ogg",
                "data": clean_b64
            }
        })
        parts.append({
            "text": "O voluntário encaminhou esse áudio recebido de um contato indeciso ou resistente. Transcreva mentalmente a mensagem dele e gere as melhores respostas no formato JSON padrão."
        })
    else:
        parts.append({
            "text": f"O voluntário recebeu a seguinte mensagem de um contato indeciso ou resistente:\n\n\"{user_input}\"\n\nGere as melhores respostas no formato JSON padrão."
        })

    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "contents": [
            {"parts": parts}
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.4
        }
    }

    for model_name in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={apiKey}"
        try:
            res = requests.post(url, json=payload, timeout=20)
            if res.status_code == 200:
                data = res.json()
                raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(raw_json)
            else:
                print(f"[Gemini {model_name}] Erro {res.status_code}: {res.text[:120]}")
        except Exception as e:
            print(f"[Gemini {model_name}] Exceção: {e}")

    return {
        "evite": "Servidores ocupados no momento.",
        "opcao_1": "Poderia reenviar a mensagem em alguns instantes? Tive uma oscilação rápida.",
        "opcao_2": "",
        "audio": ""
    }
