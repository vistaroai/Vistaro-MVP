"""Contract tests for cursor-based pagination helper."""

from dataclasses import dataclass

import pytest
from pydantic import ValidationError

from vistaro.core.errors import BadRequestError
from vistaro.core.pagination import (
    CursorPaginationParams,
    decode_cursor,
    encode_cursor,
    paginate_results,
)


@dataclass(frozen=True)
class MockItem:
    id: str
    created_at: str


def test_cursor_encode_decode_roundtrip() -> None:
    payload = {"id": "item-123", "created_at": "2026-10-24T12:00:00Z"}
    cursor = encode_cursor(payload)
    assert isinstance(cursor, str)
    assert "=" not in cursor  # Unpadded base64url

    decoded = decode_cursor(cursor)
    assert decoded == payload


def test_cursor_empty_or_none() -> None:
    assert decode_cursor(None) is None
    assert decode_cursor("") is None
    assert decode_cursor("   ") is None


def test_cursor_malformed_base64() -> None:
    with pytest.raises(BadRequestError) as exc_info:
        decode_cursor("???not-valid-base64???")
    assert exc_info.value.code == "INVALID_CURSOR"


def test_cursor_non_json_payload() -> None:
    # Valid base64 encoding of plain non-JSON text
    import base64

    non_json = base64.urlsafe_b64encode(b"just-plain-string").decode("ascii")
    with pytest.raises(BadRequestError) as exc_info:
        decode_cursor(non_json)
    assert exc_info.value.code == "INVALID_CURSOR"


def test_cursor_non_dict_json() -> None:
    # Valid base64 encoding of a JSON array instead of an object
    import base64

    array_json = base64.urlsafe_b64encode(b"[1, 2, 3]").decode("ascii")
    with pytest.raises(BadRequestError) as exc_info:
        decode_cursor(array_json)
    assert exc_info.value.code == "INVALID_CURSOR"


def test_cursor_exceeding_max_length() -> None:
    huge_cursor = "a" * 1025
    with pytest.raises(BadRequestError) as exc_info:
        decode_cursor(huge_cursor)
    assert exc_info.value.code == "INVALID_CURSOR"


def test_paginate_results_empty() -> None:
    page = paginate_results(
        fetched_items=[],
        limit=10,
        cursor_builder=lambda item: {"id": item.id},
    )
    assert page.items == []
    assert page.next_cursor is None
    assert page.has_more is False


def test_paginate_results_under_limit() -> None:
    items = [
        MockItem("1", "2026-10-24T10:00:00Z"),
        MockItem("2", "2026-10-24T10:01:00Z"),
    ]
    page = paginate_results(
        fetched_items=items,
        limit=5,
        cursor_builder=lambda item: {"id": item.id, "created_at": item.created_at},
    )
    assert page.items == items
    assert page.next_cursor is None
    assert page.has_more is False


def test_paginate_results_exactly_limit() -> None:
    items = [
        MockItem("1", "2026-10-24T10:00:00Z"),
        MockItem("2", "2026-10-24T10:01:00Z"),
    ]
    # When exactly limit items were returned by SQL query (no limit+1 record)
    page = paginate_results(
        fetched_items=items,
        limit=2,
        cursor_builder=lambda item: {"id": item.id},
    )
    assert page.items == items
    assert page.next_cursor is None
    assert page.has_more is False


def test_paginate_results_has_more() -> None:
    # SQL query asked for limit + 1 = 3 items
    items = [
        MockItem("1", "2026-10-24T10:00:00Z"),
        MockItem("2", "2026-10-24T10:01:00Z"),
        MockItem("3", "2026-10-24T10:02:00Z"),
    ]
    page = paginate_results(
        fetched_items=items,
        limit=2,
        cursor_builder=lambda item: {"id": item.id, "created_at": item.created_at},
    )
    assert len(page.items) == 2
    assert page.items == items[:2]
    assert page.has_more is True
    assert page.next_cursor is not None

    # Verify next_cursor correctly points to the last item on the page (item 2)
    decoded = decode_cursor(page.next_cursor)
    assert decoded == {"id": "2", "created_at": "2026-10-24T10:01:00Z"}


def test_pagination_params_bounds() -> None:
    params = CursorPaginationParams(limit=50)
    assert params.limit == 50
    assert params.cursor is None

    # Validation errors on bounds
    with pytest.raises(ValidationError):
        CursorPaginationParams(limit=0)

    with pytest.raises(ValidationError):
        CursorPaginationParams(limit=101)
