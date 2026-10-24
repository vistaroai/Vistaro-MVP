"""Reusable idempotency-key validation helper.

Contract and lifecycle:
1. This helper validates the syntactic validity and bounds of incoming
   ``Idempotency-Key`` request headers.
2. It ensures keys are non-empty, length-bounded (1 to 128 characters), and
   contain only safe characters (alphanumeric, hyphens, underscores, dots, colons).
3. Important: A validation helper alone DOES NOT guarantee exactly-once execution.
   Full execution idempotency requires downstream transactional storage (such as
   the ``tasks.idempotency_key`` column and connector execution records built in
   subsequent tasks like ``AI-001`` and ``MUS-002``).
"""

import re
from typing import Annotated, Final

from fastapi import Header

from vistaro.core.errors import BadRequestError

IDEMPOTENCY_KEY_HEADER: Final[str] = "Idempotency-Key"

# 1 to 128 safe ASCII characters (alphanumerics, hyphen, underscore, dot, colon)
IDEMPOTENCY_KEY_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[a-zA-Z0-9_\-\.:]{1,128}$")


def validate_idempotency_key(key: str | None, *, required: bool = True) -> str | None:
    """Validate and sanitize an incoming idempotency key.

    :param key: The raw header value from the client.
    :param required: If True, raises BadRequestError when the header is missing.
    :return: The sanitized idempotency key string, or None if not required and absent.
    :raises BadRequestError: If the key is missing (when required) or malformed.
    """
    if key is None:
        if required:
            raise BadRequestError(
                f"Missing required '{IDEMPOTENCY_KEY_HEADER}' header",
                code="MISSING_IDEMPOTENCY_KEY",
            )
        return None

    cleaned = key.strip()
    if not cleaned:
        if required:
            raise BadRequestError(
                f"Header '{IDEMPOTENCY_KEY_HEADER}' must not be empty",
                code="EMPTY_IDEMPOTENCY_KEY",
            )
        return None

    if not IDEMPOTENCY_KEY_PATTERN.fullmatch(cleaned):
        raise BadRequestError(
            f"Invalid '{IDEMPOTENCY_KEY_HEADER}' format. "
            "Must be 1-128 characters of alphanumerics, hyphens, underscores, dots, or colons.",
            code="INVALID_IDEMPOTENCY_KEY",
            details={
                "header": IDEMPOTENCY_KEY_HEADER,
                "constraint": "1 to 128 characters matching ^[a-zA-Z0-9_\\-\\.:]{1,128}$",
            },
        )

    return cleaned


def require_idempotency_key(
    idempotency_key: Annotated[
        str | None,
        Header(
            alias=IDEMPOTENCY_KEY_HEADER,
            description="Client-generated unique key ensuring safe request retries.",
        ),
    ] = None,
) -> str:
    """FastAPI dependency requiring a valid Idempotency-Key header."""
    key = validate_idempotency_key(idempotency_key, required=True)
    assert key is not None  # guaranteed by required=True
    return key


def optional_idempotency_key(
    idempotency_key: Annotated[
        str | None,
        Header(
            alias=IDEMPOTENCY_KEY_HEADER,
            description="Optional client-generated unique key ensuring safe request retries.",
        ),
    ] = None,
) -> str | None:
    """FastAPI dependency accepting an optional Idempotency-Key header."""
    return validate_idempotency_key(idempotency_key, required=False)
