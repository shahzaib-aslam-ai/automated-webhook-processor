import hmac
import hashlib

secret = "my-super-secret-key"

body = '{"review_id":"abc123","review_text":"The product arrived damaged and support was unhelpful."}'

signature = hmac.new(
    secret.encode(),
    body.encode(),
    hashlib.sha256
).hexdigest()

print("SIGNATURE:", signature)
print("BODY:", body)