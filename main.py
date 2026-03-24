import os
import datetime
from typing import List, Optional
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="EPF Agentic News Hub")

# --- CONFIGURAÇÃO ---
# Partilha este Token com os alunos para eles poderem publicar
API_TOKEN = "epf2026_secret"
# Lista em memória para guardar as notícias (limpa se reiniciares o server)
database: List[dict] = []

# --- MODELO DE DADOS ---
class NewsEntry(BaseModel):
    agent_name: str
    topic: str
    title: str
    summary: str
    url: str
    confidence: Optional[float] = 0.0

# --- ENDPOINTS ---

@app.post("/publish")
async def publish_news(entry: NewsEntry, x_token: str = Header(None)):
    """Endpoint para os alunos enviarem as notícias dos seus agentes"""
    if x_token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Token de acesso inválido!")
    
    # Adicionamos um timestamp da receção
    new_data = entry.dict()
    new_data["received_at"] = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Inserimos no topo da lista para as mais recentes aparecerem primeiro
    database.insert(0, new_data)
    
    print(f"✅ Notícia recebida de: {entry.agent_name} [{entry.topic}]")
    return {"status": "success", "message": f"Olá {entry.agent_name}, a tua notícia foi publicada!"}

@app.get("/", response_class=HTMLResponse)
async def view_blog():
    """Página principal que renderiza as notícias recebidas"""
    
    html_content = """
    <html>
        <head>
            <title>AI News Hub - EPF</title>
            <meta charset="UTF-8">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css">
            <style>
                body { max-width: 900px; margin: auto; padding: 20px; background-color: #1a1a1a; }
                .card { border: 1px solid #444; padding: 20px; border-radius: 12px; margin-bottom: 20px; background: #252525; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
                .meta { font-size: 0.85em; color: #aaa; margin-top: 15px; border-top: 1px solid #333; padding-top: 10px; }
                .tag { background: #005a9e; color: white; padding: 3px 10px; border-radius: 20px; font-size: 0.75em; font-weight: bold; text-transform: uppercase; }
                .time { float: right; color: #666; font-size: 0.8em; }
                h1 { text-align: center; color: #00bfff; }
                .empty { text-align: center; padding: 50px; color: #666; }
            </style>
            <script>
                // Auto-refresh a cada 30 segundos para ver novas notícias
                setTimeout(() => { location.reload(); }, 30000);
            </script>
        </head>
        <body>
            <h1>🤖 Agentic News Hub <small style="color: #888; font-size: 0.5em;">EPF 2º Ano</small></h1>
            <p style="text-align: center;">Servidor Central de Micro-Serviços de IA</p>
            <hr>
            <div class="feed">
    """

    if not database:
        html_content += '<div class="empty"><h3>Aguardando notícias dos agentes...</h3><p>Os alunos devem configurar o endpoint /publish</p></div>'
    else:
        for news in database:
            html_content += f"""
            <div class="card">
                <span class="time">🕒 {news['received_at']}</span>
                <span class="tag">{news['topic']}</span>
                <h2 style="margin-top: 10px;">{news['title']}</h2>
                <p>{news['summary']}</p>
                <div class="meta">
                    🛰️ Agente: <strong>{news['agent_name']}</strong> | 
                    🧠 IA Confidence: {news['confidence']} |
                    🔗 <a href="{news['url']}" target="_blank">Fonte Original</a>
                </div>
            </div>
            """

    html_content += """
            </div>
            <footer style="text-align: center; margin-top: 50px; font-size: 0.7em; color: #555;">
                EPF Programação Avançada em Python - 2026
            </footer>
        </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    # Forçamos a porta 8080 que já testámos que funciona no teu Mac
    uvicorn.run(app, host="0.0.0.0", port=8080)