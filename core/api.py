import os
import sys
import logging
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Standardize path for Umbrasol imports
sys.path.append(os.getcwd())

from core.umbrasol import UmbrasolCore
from config import settings

app = FastAPI(title="Umbrasol Neural API")

# Enable CORS for universal access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the interface directory
if os.path.exists("interface"):
    app.mount("/interface", StaticFiles(directory="interface"), name="interface")

@app.get("/")
async def get_ui():
    return FileResponse("interface/index.html")

# Instantiate the Core Agent
# We disable voice_mode by default for the web UI; users can toggle it.
agent = UmbrasolCore(voice_mode=False)

class CommandRequest(BaseModel):
    command: str
    voice: bool = False

@app.get("/health")
def health_check():
    """Returns system status and platform identity."""
    stats = agent.hands.get_system_stats()
    physical = agent.hands.get_physical_state()
    return {
        "status": "online",
        "version": settings.VERSION,
        "platform": sys.platform,
        "telemetry": {
            "cpu": stats.get("cpu_total", 0),
            "ram": stats.get("ram", 0),
            "battery": physical.get("battery", "N/A")
        }
    }

@app.websocket("/ws/thoughts")
async def thought_stream(websocket: WebSocket):
    """
    Handles duplex communication for real-time thought streaming.
    Receives commands and yields structured thought/action/result objects.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            command = data.get("command")
            voice = data.get("voice", False)
            
            if not command:
                continue
            
            # Update agent settings based on UI toggle
            agent.voice_mode = voice
            context = f"[Web Interface @ {sys.platform}]"
            
            await websocket.send_json({"type": "status", "content": "Initializing Neural Logic..."})
            
            # Direct stream from the MonolithSoul
            # execute_task_stream yields dicts: {'type': 'talk'|'action', 'content': ...}
            for chunk in agent.soul.execute_task_stream(command, context=context):
                await websocket.send_json(chunk)
                
                # If an action is identified, the backend executes it and reports the result
                if chunk["type"] == "action":
                    for action in chunk["actions"]:
                        await websocket.send_json({"type": "status", "content": f"Executing: {action['tool']}..."})
                        # Use the core's safe dispatcher
                        result = agent._safe_dispatch(action["tool"], action["cmd"])
                        await websocket.send_json({"type": "result", "content": str(result)})
            
            await websocket.send_json({"type": "done", "content": "Objective complete."})
            
    except WebSocketDisconnect:
        logging.info("Neural Dashboard Client disconnected.")
    except Exception as e:
        logging.error(f"WebSocket Error: {e}")
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except:
            pass

def start_server(host="0.0.0.0", port=8091):
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
