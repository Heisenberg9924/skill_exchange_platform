from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def create_access_token(user_id: int):

    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None