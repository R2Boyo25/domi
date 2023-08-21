import os
import re

import fastapi

from domi import log, pbuf, sessions, gpg
from domi.gpg import create_context, mktempfile, encrypt, verify, decrypt, GPGContext


def generate_key():
    pass


def generate_random_challenge():
    return os.urandom(4096)


def verify_challenge(ctx: GPGContext, response: str, challenge: str):
    if not ctx.ctx.verify(challenge):
        return False

    if ctx.ctx.decrypt(response) == challenge:
        return True

    return False


def generate_encrypted_challenge(ctx: GPGContext) -> (bytes, bytes):
    original_challenge = generate_random_challenge()
    encrypted_challenge = ctx.ctx.encrypt(original_challenge, [])

    return (encrypted_challenge, original_challenge)


async def register_user(
    ws: fastapi.WebSocket, username: str
) -> None | sessions.Session:
    with GPGContext(username) as ctx:
        await ws.send_text(f"ACK {username}")
        log.logger.info(f"Beginning registration of @{username}.")

        pubkey = await ws.receive_bytes()
        encrypted_challenge, challenge = generate_encrypted_challenge(ctx)

        await ws.send_bytes(encrypted_challenge)

        client_response = await ws.receive_bytes()

        if not verify_challenge(ctx, client_response, challenge):
            await ws.close()
            return None

        log.logger.info(f"@{username} has completed registration.")


async def authenticate_user(
    ws: fastapi.WebSocket, username: str
) -> None | sessions.Session:
    await ws.send_text(f"ACK {username}")
    log.logger.info(f"Beginning authentication of @{auth_packet.username}.")

    pubkey = await ws.receive_text()

    ctx = create_context()

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


def validate_username(username: str) -> None or str:
    if not 0 < len(username) <= 35:
        return f"ERROR username must be 1-35 chars long"

    if not re.fullmatch("[0-9a-zA-Z_.]{1,35}", username):
        return f"ERROR username can only contain 0-9, a-z, A-Z, _, or ."

    return None


async def handle_user_auth(ws: fastapi.WebSocket) -> None | sessions.Session:
    split_command = (await ws.receive_text()).split()

    if len(split_command) != 2:
        await ws.send_text(
            f"ERROR syntax is <command> <username> where command is AUTH or REGISTER"
        )
        await ws.close()

        return None

    auth_command, username = split_command
    auth_command = auth_command.lower()

    if auth_command not in {"auth", "register"}:
        await ws.send_text(f"ERROR {auth_command.upper()} not AUTH or REGISTER")
        await ws.close()

        return None

    if (error := validate_username(username)) != None:
        await ws.send_text(error)
        await ws.close()

        return None

    match auth_command:
        case "auth":
            return await authenticate_user(ws, username)
        case "register":
            result = await register_user(ws, username)

            if result is None:
                return result

            return await authenticate_user(ws, username)
