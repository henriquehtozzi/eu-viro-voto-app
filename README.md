# 🗳️ Eu Viro Voto App

> **Copiloto tático de inteligência artificial via Web App / PWA para voluntários e ativistas dialogarem com eleitores indecisos e moderados no 2º turno.**

Aplicativo web progressivo (PWA) de alta performance, pronto para deploy na **Vercel** com domínio customizado, sem dependência de chips de WhatsApp ou risco de bloqueio da Meta.

---

## 🧠 Núcleo Cognitivo e Créditos

O motor de reenquadramento cognitivo (`app/cognitive_engine.py`) foi desenvolvido com base na Linguística Cognitiva de George Lakoff (*Não pense num elefante!*) e nas pesquisas de comunicação política do guia *"Como vencer o 2º turno"* (Calma Urgente), estruturado por **Isabela Amorim**.

Sua lógica é 100% preservada:
1. **🚫 O que evitar falar** (desarmar as palavras-armadilha da narrativa adversária).
2. **💬 Opção 1 (Pergunta Suave / Família)**: Abordagem socrática e empática.
3. **💬 Opção 2 (Resposta Firme / Colega ou Grupo)**: Focada nos pontos fracos táticos (nepo baby, subserviência a Trump, falta de confiabilidade).
4. **🎙️ Roteiro de Áudio Curto (10s)**: Mensagem espontânea e rápida para mandar por áudio.

---

## 🚀 Arquitetura Serverless na Vercel

- **Frontend**: HTML5 + CSS3 + Vanilla JS moderno em formato **PWA (Progressive Web App)**, responsivo para celular, com suporte a "Adicionar à Tela de Início" e cópia rápida de mensagens com 1 toque.
- **Backend**: FastAPI assíncrono rodando como Serverless Function no endpoint `/api`.
- **IA**: Google Gemini via REST API com fallback automático.

---

## ⚙️ Variáveis de Ambiente na Vercel

No painel do projeto na Vercel (**Settings > Environment Variables**), adicione:

| Variável | Descrição |
| :--- | :--- |
| `GEMINI_API_KEY` | Chave de API do Google Gemini (obtida gratuitamente em [Google AI Studio](https://aistudio.google.com/)) |

---

## 🌐 Configuração do Domínio Personalizado

1. No painel da Vercel, acesse **Settings > Domains**.
2. Adicione seu domínio (ex: `euvirovoto.com.br` ou `app.euvirovoto.com.br`).
3. No painel DNS do seu registrador de domínio, insira as entradas apontadas pela Vercel:
   - Para subdomínio (ex: `app.euvirovoto.com.br`): CNAME apontando para `cname.vercel-dns.com`
   - Para domínio raiz (ex: `euvirovoto.com.br`): Registro A apontando para `76.76.21.21`
4. A Vercel provisionará o certificado SSL (HTTPS) automaticamente em poucos minutos.
