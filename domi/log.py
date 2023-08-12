import logging
import rich.logging

logger = logging.getLogger("domi")
logger.setLevel(logging.INFO)
logger.addHandler(rich.logging.RichHandler(omit_repeated_times=False, rich_tracebacks=True))

peers = logging.getLogger("domi.peers")
peers.setLevel(logging.INFO)

g_log = logging.getLogger("uvicorn")
g_log.handlers = logger.handlers

g_log = logging.getLogger("uvicorn.access")
g_log.handlers = logger.handlers

del g_log
