"""Reusable cursor-based pagination helper.

Cursor pagination guarantees stable ordering without offset-based performance
degradation or drift when records are inserted or deleted.
"""

import base64
import json
from collections.abc import Callable, Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vistaro.core.errors import BadRequestError

# Maximum permitted cursor string length to prevent memory abuse
MAX_CURSOR_LENGTH = 1024


def encode_cursor(payload: dict[str, Any]) -> str:
    """Encode a dictionary payload into an opaque base64url cursor string."""
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    raw_bytes = canonical_json.encode("utf-8")
    return base64.urlsafe_b64encode(raw_bytes).decode("ascii").rstrip("=")


def decode_cursor(cursor: str | None) -> dict[str, Any] | None:
    """Decode and validate an opaque base64url cursor string.

    Raises ``BadRequestError`` if the cursor is malformed, corrupted, or non-dict.
    Returns ``None`` if ``cursor`` is empty or None.
    """
    if cursor is None:
        return None
    cleaned = cursor.strip()
    if not cleaned:
        return None

    if len(cleaned) > MAX_CURSOR_LENGTH:
        raise BadRequestError("Cursor exceeds maximum allowed length", code="INVALID_CURSOR")

    # Add back base64 padding if needed
    remainder = len(cleaned) % 4
    padded = cleaned + ("=" * (4 - remainder) if remainder else "")

    try:
        raw_bytes = base64.urlsafe_b64decode(padded)
        decoded_text = raw_bytes.decode("utf-8")
        parsed = json.loads(decoded_text)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as err:
        raise BadRequestError(
            "Malformed or corrupted pagination cursor",
            code="INVALID_CURSOR",
        ) from err

    if not isinstance(parsed, dict) or not parsed:
        raise BadRequestError(
            "Pagination cursor payload must be a non-empty dictionary",
            code="INVALID_CURSOR",
        )

    return parsed


class CursorPaginationParams(BaseModel):
    """Query parameters for cursor-paginated endpoints."""

    model_config = ConfigDict(extra="forbid")

    cursor: str | None = Field(
        default=None,
        description="Opaque cursor string pointing to the next page of results",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items to return (1-100, default 20)",
    )


class CursorPage[T](BaseModel):
    """Standard generic page envelope for cursor pagination."""

    model_config = ConfigDict(extra="forbid")

    items: list[T] = Field(description="List of records for the current page")
    next_cursor: str | None = Field(
        default=None,
        description="Cursor token to fetch the subsequent page, or None if at the end",
    )
    has_more: bool = Field(
        default=False,
        description="True if there are additional records beyond this page",
    )


def paginate_results[T](
    fetched_items: Sequence[T],
    limit: int,
    cursor_builder: Callable[[T], dict[str, Any]],
) -> CursorPage[T]:
    """Slice and construct a CursorPage from items queried with ``limit + 1``.

    When querying the database, query ``limit + 1`` records. If more than ``limit``
    records are returned, ``has_more`` is True and ``next_cursor`` is derived from
    the last item on the page using ``cursor_builder``.
    """
    if limit < 1:
        raise BadRequestError("Pagination limit must be at least 1", code="INVALID_LIMIT")

    items_list = list(fetched_items)
    if len(items_list) > limit:
        page_items = items_list[:limit]
        next_cursor = encode_cursor(cursor_builder(page_items[-1]))
        has_more = True
    else:
        page_items = items_list
        next_cursor = None
        has_more = False

    return CursorPage(items=page_items, next_cursor=next_cursor, has_more=has_more)
