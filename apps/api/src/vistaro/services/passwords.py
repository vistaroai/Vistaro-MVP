"""Argon2id password hashing (AUTH-001).

``argon2-cffi`` only — no hand-rolled crypto (WARN-B-011). Password hashes
never leave this module's API in logs; there is no logging in this module at
all (TASK_PLAYBOOK AUTH-001 watch-for).
"""

import contextlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error

#: One shared hasher instance; argon2-cffi's defaults are Argon2id with
#: memory cost 64 MiB, time cost 3, parallelism 4.
_hasher = PasswordHasher()

#: Constant hash used to equalize work when the account does not exist, so
#: login timing cannot reveal whether an email is registered.
DUMMY_HASH = _hasher.hash(secrets.token_urlsafe(24))


def hash_password(password: str) -> str:
    """Hash a password with Argon2id."""
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """Return whether ``password`` matches ``password_hash``."""
    try:
        return _hasher.verify(password_hash, password)
    except Argon2Error:
        return False
    except (ValueError, TypeError):
        # A malformed/unusable stored hash counts as no-match, like a wrong
        # password: never distinguish via error type to the client.
        return False


def verify_login_attempt(password_hash: str | None, password: str) -> bool:
    """Verify a login whether or not the account exists (equalized work).

    Unknown accounts run the same Argon2id verification against ``DUMMY_HASH``
    (the inevitable mismatch is caught, not leaked) so both failure paths
    take comparable time; callers raise the same generic
    ``INVALID_CREDENTIALS`` error for either case.
    """
    if not password_hash:
        # Deliberate mismatch burn: spend the same Argon2id wall time a real
        # verification would take, so timing cannot enumerate accounts. An
        # (astronomically unlikely) match still returns False.
        with contextlib.suppress(Argon2Error):
            _hasher.verify(DUMMY_HASH, password)
        return False
    return verify_password(password_hash, password)
