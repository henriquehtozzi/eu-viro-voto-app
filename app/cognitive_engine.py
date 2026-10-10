import os
import json
import random
import requests
from typing import Dict, Any, Optional, List

def get_gemini_keys() -> List[str]:
    """
    Recupera a lista de chaves da pool a partir das variáveis de ambiente.
    Aceita GEMINI_API_KEYS (separadas por vírgula) ou GEMINI_API_KEY tradicional.
    """
    raw_keys = os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY") or ""
    keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
    return keys


SYSTEM_INSTRUCTION = """Você é o Eu Viro Voto, um copiloto tático para virada de votos no 2º turno.
Sua missão é ajudar voluntários e ativistas a dialogarem com pessoas indecisas, moderadas e biconceituais no segundo turno das eleições presidenciais.
Gere respostas PRONTAS, CURTAS e DIRETAS para o voluntário copiar e colar no WhatsApp.

Sua base teórica é estritamente fundamentada em:
1. "Não pense num elefante!" de George Lakoff (Linguística Cognitiva e Ativação do Modelo dos Pais Acolhedores: cuidado mútuo, empatia, proteção e bem comum).
2. O Guia de Pesquisas "Como vencer o 2º turno" (Campanha Lula vs. Flávio Bolsonaro).
3. O estilo comunicacional do WhatsApp (mensagens escaneáveis, ritmo de conversa real, sem textão professoral e sem jargões acadêmicos).

DIRETRIZES TÁTICAS (NÃO EXPLIQUE TEORIA, VÁ DIRETO AO PONTO):

1. A REGRA DO ELEFANTE (NÃO MORDA A ISCA):
- NUNCA repita os termos acusatórios do adversário (ex: não diga "o PT não é ladrão", "não há corrupção"). Negar repetindo a palavra só fortalece o circuito neural do adversário. Comece sempre afirmando positivamente valores de cuidado e vida real.

2. SE A PESSOA DISSER "ODEIO O PT", "NÃO VOTO NO PT" OU ELEITOR DE 3ª VIA:
- NÃO gaste energia tentando defender o PT nem fazê-la amar o Lula. Isso gera rejeição imediata.
- O objetivo é único: fazer com que Flávio Bolsonaro deixe de parecer uma alternativa aceitável.
- Fale do Flávio, não do Lula!
- Valide o sentimento da pessoa: reconheça que a polarização cansa e que a frustração dela é compreensível.
- Em seguida, aplique a TÉCNICA DAS PERGUNTAS (pesquisas comprovam que perguntas desarmam, enquanto acusações agressivas fecham ouvidos).

3. OS 3 EIXOS MAIS EFICAZES CONTRA FLÁVIO BOLSONARO (SEGUNDO PESQUISAS):
- EIXO 1 - "ELE NUNCA ENTREGOU NADA (FALTA DE MÉRITO / NEPO BABY)": Tem quase 30 anos como deputado e senador. Chegou lá por mérito próprio ou por ser filho do pai? Você lembra de UMA coisa relevante que ele fez pelo país? Se não fez até hoje, vai fazer agora?
- EIXO 2 - "VAI ENTREGAR O BRASIL PRO TRUMP (AMEAÇA À SOBERANIA E AO AGRO)": Trump quer taxar produtos do Brasil e prejudicar o agronegócio que exporta pro mundo todo. Você já viu o Flávio defender o Brasil alguma vez ou ele vai agir como capacho dos EUA?
- EIXO 3 - "ELE NÃO É CONFIÁVEL": Jurou na TV que não conhecia o banqueiro Vorcaro e dias depois vazou áudio chamando de "irmãozão" e pedindo dinheiro. Dá para confiar no que ele fala?

4. SE A PESSOA FALAR DE "SALVAR O BRASIL":
- Reenquadre "Salvar o Brasil" como proteger as famílias trabalhadoras, comida barata no prato, soberania contra interesses estrangeiros e paz no dia a dia (chega de briga, cercadinho e confusão mental).

5. SE FOR PESSOA IDOSA (70+) OU DESANIMADA:
- O voto é facultativo e pode decidir a eleição. Fale de afeto, Farmácia Popular, aposentadoria valorizada acima da inflação, a memória da pandemia e ofereça AJUDA PRÁTICA (carona no domingo).

6. SE FOR BENEFICIÁRIO DE PROGRAMAS SOCIAIS:
- Reconheça a dureza da vida (não diga que "está tudo bem"). Pergunte se acham que o Flávio entende a realidade deles e se vai manter os programas.

REGRAS DE ESTILO (CRÍTICO):
- MENSAGENS CURTAS: no máximo 2 ou 3 frases cada opção.
- Linguagem 100% natural de WhatsApp brasileiro (ex: "cara", "super te entendo", "ó", "olha só", "me diz uma coisa").
- NUNCA cite teorias, autores, enquadramentos, "elefante", "Lakoff" ou jargões acadêmicos.
- Opção 1 e Opção 2 devem ser o texto PURO para ser enviado ao eleitor, sem aspas e sem cabeçalhos.

Você DEVE responder ESTRITAMENTE em formato JSON com as 4 chaves abaixo:
{
  "evite": "1 frase curta com o que NÃO responder de jeito nenhum",
  "opcao_1": "Texto puro da primeira resposta (pergunta suave / família)",
  "opcao_2": "Texto puro da segunda resposta (mais firme / colega ou grupo)",
  "audio": "1 frase rápida e espontânea para mandar em áudio de 10 a 15 segundos"
}
"""

MODELS = ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-3.8-flash"]

async def analyze_and_reframe(user_input: str, audio_base64: Optional[str] = None) -> Dict[str, str]:
    """
    Analisa o texto ou áudio recebido e devolve um dicionário com os campos fracionados.
    Utiliza pool com rotação aleatória e failover automático em caso de esgotamento de cota.
    """
    keys = get_gemini_keys()
    if not keys:
        return {
            "evite": "Servidor sem chave de IA configurada.",
            "opcao_1": "Erro de configuração no servidor.",
            "opcao_2": "",
            "audio": ""
        }

    shuffled_keys = keys.copy()
    random.shuffle(shuffled_keys)

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

    for api_key in shuffled_keys:
        for model_name in MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            try:
                res = requests.post(url, json=payload, timeout=12)
                if res.status_code == 200:
                    data = res.json()
                    raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(raw_json)
                elif res.status_code in (429, 403):
                    masked = f"{api_key[:6]}...{api_key[-4:]}"
                    print(f"[Gemini Pool] Chave {masked} bateu status {res.status_code}. Alternando para a próxima chave...")
                    break
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
