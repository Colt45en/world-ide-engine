"""
Simple Bus server for the World Engine prototype.
- WebSocket stream endpoint: /stream -> pushes frame packets at ~60Hz
- Command HTTP endpoint: /command -> accepts JSON commands
- CORS enabled for local dev
"""

import asyncio
import json
import random
import time
from typing import Set
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
try:
    import nexus.qtp_bridge as qtp_bridge
except Exception:
    import qtp_bridge


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="World Engine Bus (dev)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients: Set[WebSocket] = set()

async def broadcast_loop():
    tick = 0
    while True:
        tick += 1
        # generate engine-driven frame packet
        packet = qtp_bridge.generate_frame_packet(tick)

        data = json.dumps(packet)

        data = json.dumps(packet)

        # broadcast to all connected websockets
        closed = []
        for ws in list(clients):
            try:
                await ws.send_text(data)
            except Exception:
                # collect dead sockets to remove
                closed.append(ws)
        for ws in closed:
            clients.discard(ws)
            logging.info(f"WS disconnect: {ws.client}")

        # sleep for ~60Hz
        await asyncio.sleep(1.0 / 60.0)


@app.on_event("startup")
async def on_startup():
    # start background broadcaster
    app.state.broadcast_task = asyncio.create_task(broadcast_loop())


@app.on_event("shutdown")
async def on_shutdown():
    task = getattr(app.state, "broadcast_task", None)
    if task:
        task.cancel()


@app.websocket("/stream")
async def stream(ws: WebSocket):
    await ws.accept()
    logging.info(f"WS connect: {ws.client}")
    clients.add(ws)
    try:
        while True:
            # listen for pings from client; keep alive
            text = await ws.receive_text()
            # echo acks for debugging
            await ws.send_text(json.dumps({"ack": text}))
    except WebSocketDisconnect:
        clients.discard(ws)
        logging.info(f"WS disconnect: {ws.client}")
    except Exception:
        clients.discard(ws)
        logging.info(f"WS disconnect: {ws.client}")


@app.post("/command")
async def command(req: Request):
    payload = await req.json()
    # DEBUG: echo back with status
    return {"status": "ok", "received": payload}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
