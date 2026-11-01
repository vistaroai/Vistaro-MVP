"""Google sign-in (AUTH-001 Phase B), via Authlib's Starlette client.

Design:
- The client registers from ``settings.google_client_id/secret``. When either
  is empty the feature is **off**: ``google_client()`` returns ``None`` and
  the routes answer 503 ``OAUTH_NOT_CONFIGURED`` — so local development and
  all non-Google tests never touch the network.
- Anti-forgery: Authlib stores the ``state`` in the Starlette session (signed
  cookie from ``settings.session_secret``) and validates it during the token
  exchange. We never log tokens, codes, or userinfo.
- Trust model: Google guarantees the returned email is verified (we require
  ``email_verified`` true) and the ``sub`` is stable per Google account.
  ``sub`` is stored in ``users.google_sub`` (the ``DB-001`` column).
"""

from typing import Any

from authlib.integrations.starlette_client import OAuth

from vistaro.core.config import settings

_oauth = OAuth()
_google_registered = False

#: The only userinfo scope we need.
GOOGLE_SCOPE = "openid email profile"


class GoogleUserInfo:
    """The fields we accept from Google (never stored raw)."""

    def __init__(self, sub: str, email: str) -> None:
        self.sub = sub
        self.email = email


def google_oauth_enabled() -> bool:
    """Whether both Google credentials are present."""
    return bool(settings.google_client_id and settings.google_client_secret)


def google_client() -> Any:
    """Return the registered Authlib client, or ``None`` when unconfigured."""
    global _google_registered
    if not google_oauth_enabled():
        return None
    if not _google_registered:
        _oauth.register(
            "google",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            server_metadata_url=(
                "https://accounts.google.com/.well-known/openid-configuration"
            ),
            client_kwargs={"scope": GOOGLE_SCOPE},
        )
        _google_registered = True
    return _oauth.google


def parse_google_userinfo(token_response: dict[str, Any]) -> GoogleUserInfo | None:
    """Extract ``sub``/``email`` while enforcing ``email_verified``.

    Returns ``None`` for anything incomplete or not verified so the caller
    answers with one generic failure (no account-state leaks).
    """
    userinfo = token_response.get("userinfo") if token_response else None
    if not isinstance(userinfo, dict):
        return None
    sub = userinfo.get("sub")
    email = userinfo.get("email")
    email_verified = userinfo.get("email_verified")
    if not isinstance(sub, str) or not sub:
        return None
    if not isinstance(email, str) or not email:
        return None
    if email_verified is not True:
        return None
    return GoogleUserInfo(sub=sub, email=email)
