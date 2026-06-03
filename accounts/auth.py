from datetime import datetime, timedelta

import jwt
from django.conf import settings


TOKEN_LIFETIME_HOURS = 24


def create_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_LIFETIME_HOURS),
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm='HS256',
    )


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256'],
        )
        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None
    