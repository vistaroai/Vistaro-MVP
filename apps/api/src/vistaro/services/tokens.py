"""One-time token primitives for authentication (AUTH-001).

Tokens (session credentials, email-verification links) are generated with
:mod:`secrets` and only ever stored as SHA-256 hex digests, so a database
leak of ``sessions``/``email_verifications`` yields no usable secrets
(WARN-D-007 follow-through). No token or digest is ever logged.
"""

import hashlib
import secrets


def generate_token() -> str:
    """Return a URL-safe random token to hand to browsers."""
    return secrets.token_urlsafe(32)


def token_digest(token: str) -> str:
    """SHA-256 hex digest; the only form of a token stored server-side."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
