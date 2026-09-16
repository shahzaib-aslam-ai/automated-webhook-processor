import os
import hmac
import hashlib

from dotenv import load_dotenv


load_dotenv()

SECRET = "my-super-secret-key"

if not SECRET:
    raise RuntimeError("WEBHOOK_SECRET is missing")

def verify_signature(payload_body: bytes, received_signature: str) -> bool:

    expected = hmac.new(
        SECRET.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()

    print("EXPECTED:", expected)
    print("RECEIVED:", received_signature)

    return hmac.compare_digest(
        expected,
        received_signature
    )