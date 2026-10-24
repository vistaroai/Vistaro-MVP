"""Contract tests for idempotency-key validation helper."""

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from vistaro.core.errors import BadRequestError, register_error_handlers
from vistaro.core.idempotency import (
    IDEMPOTENCY_KEY_HEADER,
    optional_idempotency_key,
    require_idempotency_key,
    validate_idempotency_key,
)


def create_idempotency_app() -> FastAPI:
    test_app = FastAPI()
    register_error_handlers(test_app)

    @test_app.post("/action/required")
    def perform_action_required(
        key: str = Depends(require_idempotency_key),
    ) -> dict[str, str]:
        return {"status": "ok", "key": key}

    @test_app.post("/action/optional")
    def perform_action_optional(
        key: str | None = Depends(optional_idempotency_key),
    ) -> dict[str, str | None]:
        return {"status": "ok", "key": key}

    return test_app


client = TestClient(create_idempotency_app())


def test_validate_idempotency_key_valid() -> None:
    assert validate_idempotency_key("req_123-abc.def:99") == "req_123-abc.def:99"
    assert validate_idempotency_key("  trimmed-key  ") == "trimmed-key"


def test_validate_idempotency_key_missing_required() -> None:
    with pytest.raises(BadRequestError) as exc_info:
        validate_idempotency_key(None, required=True)
    assert exc_info.value.code == "MISSING_IDEMPOTENCY_KEY"


def test_validate_idempotency_key_missing_optional() -> None:
    assert validate_idempotency_key(None, required=False) is None
    assert validate_idempotency_key("", required=False) is None
    assert validate_idempotency_key("   ", required=False) is None


def test_validate_idempotency_key_empty() -> None:
    with pytest.raises(BadRequestError) as exc_info:
        validate_idempotency_key("", required=True)
    assert exc_info.value.code == "EMPTY_IDEMPOTENCY_KEY"


def test_validate_idempotency_key_invalid_characters() -> None:
    invalid_cases = [
        "key with spaces",
        "key<with>tags",
        "key\nwithnewline",
        "key🎉emoji",
    ]
    for case in invalid_cases:
        with pytest.raises(BadRequestError) as exc_info:
            validate_idempotency_key(case)
        assert exc_info.value.code == "INVALID_IDEMPOTENCY_KEY"


def test_validate_idempotency_key_length_limits() -> None:
    # 128 characters is valid
    valid_max = "k" * 128
    assert validate_idempotency_key(valid_max) == valid_max

    # 129 characters is rejected
    too_long = "k" * 129
    with pytest.raises(BadRequestError) as exc_info:
        validate_idempotency_key(too_long)
    assert exc_info.value.code == "INVALID_IDEMPOTENCY_KEY"


def test_require_idempotency_key_endpoint_success() -> None:
    response = client.post(
        "/action/required",
        headers={IDEMPOTENCY_KEY_HEADER: "key-12345"},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "key": "key-12345"}


def test_require_idempotency_key_endpoint_missing() -> None:
    response = client.post("/action/required")
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "MISSING_IDEMPOTENCY_KEY"


def test_optional_idempotency_key_endpoint_present() -> None:
    response = client.post(
        "/action/optional",
        headers={IDEMPOTENCY_KEY_HEADER: "opt-key-777"},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "key": "opt-key-777"}


def test_optional_idempotency_key_endpoint_absent() -> None:
    response = client.post("/action/optional")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "key": None}
