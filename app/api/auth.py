from __future__ import annotations

import hmac
import os
import secrets
import time
from collections import defaultdict, deque
from dotenv import load_dotenv

load_dotenv()

from fastapi import HTTPException, Request, status
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()

ADMIN_USERNAME = os.getenv("RDRS_ADMIN_USERNAME", "")
ADMIN_PASSWORD_HASH = os.getenv("RDRS_ADMIN_PASSWORD_HASH", "")
SESSION_SECRET = os.getenv("RDRS_SESSION_SECRET", "")

if not ADMIN_USERNAME or not ADMIN_PASSWORD_HASH or not SESSION_SECRET:
    raise RuntimeError(
        "Authentication is not configured. Set "
        "RDRS_ADMIN_USERNAME, RDRS_ADMIN_PASSWORD_HASH, "
        "and RDRS_SESSION_SECRET."
    )

if len(SESSION_SECRET) < 32:
    raise RuntimeError("RDRS_SESSION_SECRET must contain at least 32 characters.")

# A small in-memory login limiter for this single-instance demo.
_LOGIN_ATTEMPTS: dict[str, deque[float]] = defaultdict(deque)
_LOGIN_WINDOW_SECONDS = 300
_LOGIN_MAX_ATTEMPTS = 5


def verify_password(password: str) -> bool:
    try:
        return password_hasher.verify(password, ADMIN_PASSWORD_HASH)
    except Exception:
        return False


def check_login_rate_limit(client_ip: str) -> None:
    now = time.monotonic()
    attempts = _LOGIN_ATTEMPTS[client_ip]

    while attempts and now - attempts[0] > _LOGIN_WINDOW_SECONDS:
        attempts.popleft()

    if len(attempts) >= _LOGIN_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again in five minutes.",
        )

    attempts.append(now)


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def require_csrf(request: Request) -> None:
    expected = request.session.get("csrf_token")
    supplied = request.headers.get("x-csrf-token", "")

    if not expected or not supplied or not hmac.compare_digest(expected, supplied):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing or invalid.",
        )


def require_auth(request: Request) -> None:
    if not request.session.get("authenticated"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
