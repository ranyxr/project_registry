from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any, Dict

import bcrypt
from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


def _normalize_password(password: str) -> str:
    encoded = password.encode("utf-8")
    if len(encoded) <= 72:
        return password
    # Hash the password to ensure bcrypt input stays within length limits while
    # keeping comparisons deterministic.
    return sha256(encoded).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check whether provided password matches stored hash."""

    normalized = _normalize_password(plain_password).encode("utf-8")
    return bcrypt.checkpw(normalized, hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """Hash password for storage."""

    normalized = _normalize_password(password).encode("utf-8")
    return bcrypt.hashpw(normalized, bcrypt.gensalt()).decode("utf-8")


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Generate signed JWT for the given subject."""

    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    expire = datetime.now(timezone.utc) + expires_delta
    payload: Dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Validate token and return payload."""

    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:  # pragma: no cover - defensive programming
        raise ValueError("Invalid authentication token") from exc
