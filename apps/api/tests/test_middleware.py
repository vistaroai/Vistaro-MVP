"""Contract tests for Request-ID middleware and safe header propagation."""

import re
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient

from vistaro.core.errors import register_error_handlers
from vistaro.core.middleware import (
    REQUEST_ID_HEADER,
    RequestIDMiddleware,
    validate_request_id,
)

UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)


def create_app() -> FastAPI:
    test_app = FastAPI()
    register_error_handlers(test_app)
    test_app.add_middleware(RequestIDMiddleware)

    @test_app.get("/ping")
    def ping() -> dict[str, str]:
        return {"pong": "true"}

    return test_app


client = TestClient(create_app())


def test_request_id_validation_logic() -> None:
    assert validate_request_id(None) is None
    assert validate_request_id("") is None
    assert validate_request_id("   ") is None
    assert validate_request_id("valid-id-123_abc") == "valid-id-123_abc"
    # Reject illegal characters
    assert validate_request_id("id with spaces") is None
    assert validate_request_id("<script>") is None
    assert validate_request_id("id\nnewline") is None
    # Reject overly long strings
    assert validate_request_id("a" * 128) == "a" * 128
    assert validate_request_id("a" * 129) is None


def test_generated_request_id_when_header_missing() -> None:
    response = client.get("/ping")
    assert response.status_code == 200
    assert REQUEST_ID_HEADER in response.headers
    req_id = response.headers[REQUEST_ID_HEADER]
    assert UUID_PATTERN.match(req_id)


def test_safe_propagation_of_valid_incoming_request_id() -> None:
    custom_id = str(uuid.uuid4())
    response = client.get("/ping", headers={REQUEST_ID_HEADER: custom_id})
    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER] == custom_id


def test_malicious_incoming_request_id_is_replaced() -> None:
    # Malicious string with injection or disallowed characters
    response = client.get(
        "/ping",
        headers={REQUEST_ID_HEADER: "<script>alert(1)</script>"},
    )
    assert response.status_code == 200
    echoed_id = response.headers[REQUEST_ID_HEADER]
    assert "<script>" not in echoed_id
    assert UUID_PATTERN.match(echoed_id)


def test_overly_long_incoming_request_id_is_replaced() -> None:
    oversized = "x" * 200
    response = client.get("/ping", headers={REQUEST_ID_HEADER: oversized})
    assert response.status_code == 200
    echoed_id = response.headers[REQUEST_ID_HEADER]
    assert echoed_id != oversized
    assert len(echoed_id) <= 128
    assert UUID_PATTERN.match(echoed_id)
