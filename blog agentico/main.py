import importlib
import os
from fastapi import FastAPI
from news_framework import BaseNewsAgent
import asyncio

app = FastAPI(title="Agentic News Portal")

def discover_agents():
    """Lê a pasta /agents e carrega as classes dos alunos"""
    agents = []
    for file in os.listdir("./agents"):
        if file.endswith(".py") and file != "__init__.py":
            module_name = f"agents.{file[:-3]}"
            module = importlib.import_module(module_name)
            # Procura por classes que herdam de BaseNewsAgent
            for name, obj in vars(module).items():
                if isinstance(obj, type) and issubclass(obj, BaseNewsAgent) and obj is not BaseNewsAgent:
                    agents.append(obj(agent_name=name, topic=name.replace("Agent", "")))
    return agents

@app.get("/")
async def get_news():
    agents = discover_agents()
    # Executa todos os agentes em paralelo (Magia do Async)
    tasks = [agent.run() for agent in agents]
    results = await asyncio.gather(*tasks)
    return {
        "count": len(results),
        "news_feed": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)