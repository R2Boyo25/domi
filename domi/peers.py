import os
import threading
import aiohttp
from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import log


@asynccontextmanager
async def lifespan(app: FastAPI):   
    app.peer_sessions = aiohttp.ClientSession(
        headers={
            "USER-AGENT": "Domi Haven Server"
        }
    )
    
    yield
    
    await app.peer_sessions.close()
