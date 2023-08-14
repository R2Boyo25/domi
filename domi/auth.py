import os
import re

import gnupg
import fastapi

from domi import log, pbuf, sessions

def create_context(keyring=None):
    gnupghome = os.getenv("DOMI_GPGHOME", "/data/")
    
    if not os.path.exists(gnupghome):
        os.mkdir(gnupghome)
    
    return gnupg.GPG(
        gnupghome=gnupghome,
        keyring=keyring
    )

def generate_key():
    pass

def generate_random_challenge():
    return os.urandom(4096)

def verify_challenge(ctx: gnupg.GPG, response: str, challenge: str):
    if not ctx.verify(challenge):
        return False
    
    if ctx.decrypt(response) == challenge:
        return True

    return False

def generate_encrypted_challenge(ctx: gnupg.GPG, key: bytes):
    return 

async def register_user(ws: fastapi.WebSocket, username: str) -> None | sessions.Session:
    await ws.send_text(f"ACK {username}")
    log.logger.info(f"Beginning registration of @{username}.")

    pubkey = await ws.receive_bytes()

    encrypted_challenge()
    
    log.logger.info(f"@{username} has completed registration.")
    

async def authenticate_user(ws: fastapi.WebSocket, username: str) -> None | sessions.Session:
    await ws.send_text(f"ACK {username}")
    log.logger.info(f"Beginning authentication of @{auth_packet.username}.")
    
    pubkey = await ws.receive_bytes()
    
    ctx = create_context()
    challenge = generate_random_challenge()

    return

    await ws.send_bytes(sign(encrypt(challenge, auth_packet.key), auth_packet.key))
    
    user_response = await ws.receive_bytes()
    
    if not is_signed(user_response):
        await ws.close()
        return None

    if decrypt(user_response) != challenge:
        await ws.close()
        return None

    session = sessions.open_session(ip_address=ws.client.host)

    await ws.send_bytes(session)

    log.logger.info(f"@{auth_packet.username} has authenticated successfully.")
    
    return session

async def handle_user_auth(ws: fastapi.WebSocket) -> None | sessions.Session:
    split_command = (await ws.receive_text()).split()

    if len(split_command) != 2:
        await ws.send_text(f"Invalid syntax: must be <command> <username> where command is AUTH or REGISTER")
        await ws.close()
        return None

    auth_command, username = split_command

    if not 0 < len(username) <= 35:
        await ws.send_text(f"Invalid username: username must be 1-35 chars long")
        await ws.close()
        return None

    if not re.fullmatch("[0-9a-zA-Z_.]", username):
        await ws.send_text(f"Invalid username: can only contain 0-9, a-z, A-Z, _, or .")
        await ws.close()
        return None
    
    auth_command = auth_command.lower()
    
    match auth_command:
        case "auth":
            return await authenticate_user(ws, username)
        case "register":
            result = await register_user(ws, username)

            if result is None:
                return result

            return await authenticate_user(ws, username)
        case _:
            await ws.send_text(f"{auth_command.upper()} not AUTH or REGISTER")
            await ws.close()
            return None
