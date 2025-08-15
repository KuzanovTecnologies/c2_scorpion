# server.py
import asyncio
import json
import sqlite3
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
import uvicorn
from datetime import datetime

app = FastAPI(title="Whitecat C2-Defensivo POC")

# --- Banco simples em SQLite POC ---
DB = "whitecat_c2.db"
def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS agents (
        id TEXT PRIMARY KEY,
        hostname TEXT,
        last_seen TEXT,
        ws_path TEXT
)
""")
con.commit()
con.close()

def upsert_agent(agent_id, hostname, ws_path):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
    INSERT INTO agents (id, hostname, last_seen, ws_path) VALUES (?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET hostname=excluded.hostname, last_seen=excluded.last_seen, ws_path=excluded.ws_path
    """, (agent_id, hostname, datetime.utcnow().isoformat(), ws_path))
    con.commit()
    con.close()

def update_last_seen(agent_id):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("UPDATE agents SET last_seen=? WHERE id=?", (datetime.utcnow().isoformat(), agent_id))
    con.commit()
    con.close()

def list_agents():
    con=sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT id, hostname, last_seen FROM agents")
    rows = cur.fetchall()
    con.close()
    return [{"id": r[0], "hostname": r[1], "last_seen": r[2]} for r in rows]

# --- gerenciador de conexões WebSocket ---
class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, WebSocket] = {}
    async def connect(self, agent_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active[agent_id] = websocket

    def disconnect(self, agent_id: str):
        if agent_id in self.active:
            del self.active[agent_id]
    async def send_command(self, agent_id: str, command: dict):
        if agent_id not in self.active:
            raise KeyError("Agent offline or not connected")
        ws = self.active[agent_id]
        await ws.send_text(json.dumps(command))
        # aguardamos resposta simples
        response = await ws.receive_text()
        return json.loads(response)

manager = ConnectionManager()

# --- modelos ---
class Heartbeat(baseModel):
    agent_id: str
    cpu_pct: float
    mem_pct: float
    info: dict = {}

class CommandRequest(BaseModel):
    agent_id: str
    command: str
    args: dict = {}

# --- endpoints ---
@app.on_event("startup")
async def startup():
    init_db()

@app.get("/agents")
async def get_agents():
    return list_agents()

@app.post("/heartbeat")
async def heartbeat(hb: Heartbeat):
    update_last_seen(hb.agent_id)
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    try:
        await manager.connect(agent_id, websocket)
        # opcional: primeiro texto recebido é o registro com hostname
        reg = await websocket.receive_text()
        try:
            regj = json.loads(reg)
            hostname = regj.get("hostname", "unknown")
        except Exception:
            hostname = "unknown"
         upsert_agent(agent_id, hostname, f"/ws/{agent_id}")
         while True:
             # servidor apenas aguarda mensagens do agente (ex: logs)
             msg = await websocket.receive_text()
             # aqui só imprimimos logs - salvar em arquivo/log store em produção
             print(f"[{agent_id}] -> {msg}")

@app.post("/send_command")
async def send_command(req: CommandRequest):
    # validações minimas
    cmd = {"command": req.command, "args": req.args, "timestamp": datetime.utcnow().isoformat()}
    try:
        # send_command espera uma resposta
        result = await manager.send_command(req.agent_id, cmd)
        return {"status": "sent", "result": result}
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not connected")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
