import os
import gnupg
import fastapi

from domi import log

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

async def authenticate_user(ws: fastapi.WebSocket):    
    ctx = create_context()
    challenge = generate_random_challenge()
    
    await ws.accept()
    
    auth_packet = await ws.receive_bytes()
    
    log.logger.info(f"Beginning authentication of {auth_packet.username}")
    
    await ws.send_bytes(sign(encrypt(challenge, auth_packet.key), auth_packet.key))
    
    user_response = await ws.receive_bytes()
    
    if not is_signed(user_response):
        await ws.close()

    if decrypt(user_response) != challenge:
        await ws.close()

    session = sessions.open_session(ip_address=ws.client.host)

    await ws.send_bytes(session)
    
    return session
