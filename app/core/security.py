import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pwdlib import PasswordHash
from app.core.config import settings


password_hasher = PasswordHash.recommended()

JWT_ALGORITHM = "HS256"
JWT_ISSUER = "digi-coc"
JWT_AUDIENCE = "digi-coc-api"
ACCESS_TOKEN_MINUTES = 30


def get_jwt_secret() -> str:
    secret = settings.digicoc_jwt_secret

    if not secret or len(secret) < 32:
        raise RuntimeError(
            "DIGICOC_JWT_SECRET must be configured with a secret "
            "of at least 32 characters."
        )

    return secret


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters.")

    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password, password_hash)
    except Exception:
        return False


def create_access_token(personnel_id: UUID) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(personnel_id),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "type": "access",
    }

    return jwt.encode(
        payload,
        get_jwt_secret(),
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        get_jwt_secret(),
        algorithms=[JWT_ALGORITHM],
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        options={
            "require": ["sub", "iat", "exp", "iss", "aud", "type"],
        },
    )

    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Invalid token type.")

    # Validate the subject as a UUID.
    UUID(payload["sub"])

    return payload