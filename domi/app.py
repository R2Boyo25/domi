import os
from typing import Annotated
from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, Header, Request
from starlette.websockets import WebSocketDisconnect

from domi import peers, log, auth


load_dotenv()


app = FastAPI(lifespan=peers.lifespan)


@app.get("/")
async def root(user_agent: Annotated[str | None, Header()] = None):
    log.logger.info("User-Agent: %s" % user_agent)

    return {"message": "Hello World!"}


@app.websocket("/events")
async def event_stream(ws: WebSocket):
    await ws.accept()

    try:
        if (session := await auth.handle_user_auth(ws)) is None:
            return

    except WebSocketDisconnect:
        return

    # User is authenticated


# @app.get("/{to}")
# async def send_message(to: str):
#    async with app.peer_sessions.get(f"http://{to}") as response:
#        return await response.json()
