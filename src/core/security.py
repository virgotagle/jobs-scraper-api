"""API key generation, hashing, and verification utilities."""

import secrets

import bcrypt


def generate_api_key(prefix: str = "sk_live") -> str:
    """Generate a secure API key with the given prefix."""
    random_bytes = secrets.token_urlsafe(32)
    return f"{prefix}_{random_bytes}"


def hash_api_key(api_key: str) -> str:
    """Hash API key using bcrypt for secure storage."""
    return bcrypt.hashpw(api_key.encode(), bcrypt.gensalt()).decode()


def verify_api_key(api_key: str, key_hash: str) -> bool:
    """Verify API key against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(api_key.encode(), key_hash.encode())
    except Exception:
        return False


def get_key_prefix(api_key: str) -> str:
    """Extract first 12 characters of API key for display."""
    return api_key[:12] + "..."
