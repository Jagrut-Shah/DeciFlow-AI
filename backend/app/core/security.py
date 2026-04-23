from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from app.core.config import settings

# Passlib is optional — graceful fallback if not installed
try:
    from passlib.context import CryptContext
    _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    _PASSLIB_AVAILABLE = True
except ImportError:
    _PASSLIB_AVAILABLE = False


# --------------------------------------------------------------------------- #
# Password Hashing                                                             #
# --------------------------------------------------------------------------- #

def hash_password(plain: str) -> str:
    if not _PASSLIB_AVAILABLE:
        raise RuntimeError("passlib[bcrypt] is not installed. Run: pip install passlib[bcrypt]")
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    if not _PASSLIB_AVAILABLE:
        raise RuntimeError("passlib[bcrypt] is not installed. Run: pip install passlib[bcrypt]")
    return _pwd_context.verify(plain, hashed)


# --------------------------------------------------------------------------- #
# Token Creation                                                               #
# --------------------------------------------------------------------------- #

def create_access_token(
    subject: str,
    role: str = "user",
    extra_claims: Optional[dict] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject:       Unique identifier for the principal (e.g. user_id).
        role:          Role claim embedded in token ("user", "admin", etc.).
        extra_claims:  Additional key/value pairs to embed in the payload.
        expires_delta: Override the default expiry window.
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    payload = {
        "sub": subject,           # Standard JWT subject
        "role": role,             # Role-based access control
        "type": "access",         # Token type — strictly checked on verify
        "iat": now.timestamp(),   # Issued at
        "exp": expire.timestamp(),
    }

    if extra_claims:
        # Protect reserved claims from being overwritten
        reserved = {"sub", "role", "type", "iat", "exp"}
        payload.update({k: v for k, v in extra_claims.items() if k not in reserved})

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT refresh token (longer-lived, type='refresh')."""
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(days=7))

    payload = {
        "sub": subject,
        "type": "refresh",
        "iat": now.timestamp(),
        "exp": expire.timestamp(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# --------------------------------------------------------------------------- #
# Token Verification                                                           #
# --------------------------------------------------------------------------- #

def verify_token(token: str, expected_type: str = "access") -> dict:
    """
    Decode and validate a JWT token.

    Raises CustomException (401) on:
      - Expired token
      - Invalid signature / malformed token
      - Missing 'sub' claim
      - Token type mismatch (e.g. refresh token used as access token)
    """
    from app.core.exceptions import CustomException

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise CustomException(
            message="Token has expired. Please log in again.",
            status_code=401,
            error_code="TOKEN_EXPIRED",
        )
    except jwt.InvalidTokenError as exc:
        raise CustomException(
            message=f"Invalid authentication token: {exc}",
            status_code=401,
            error_code="TOKEN_INVALID",
        )

    # --- Enforce sub (subject) ---
    if not payload.get("sub"):
        raise CustomException(
            message="Token is missing required 'sub' claim.",
            status_code=401,
            error_code="TOKEN_MALFORMED",
        )

    # --- Enforce token type ---
    token_type = payload.get("type")
    if token_type != expected_type:
        raise CustomException(
            message=f"Invalid token type. Expected '{expected_type}', got '{token_type}'.",
            status_code=401,
            error_code="TOKEN_TYPE_MISMATCH",
        )

    return payload
