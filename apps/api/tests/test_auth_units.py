"""AUTH-001 unit tests: hashing, tokens, and the FAKE/labeled email senders."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from vistaro.services.email import (
    MailpitSmtpSender,
    RecordingEmailSender,
    ResendHttpSender,
    build_verification_email,
    get_email_sender,
)
from vistaro.services.passwords import (
    DUMMY_HASH,
    hash_password,
    verify_login_attempt,
    verify_password,
)
from vistaro.services.tokens import generate_token, token_digest


def test_argon2id_roundtrip() -> None:
    digest = hash_password("S3cure-passphrase!")
    assert digest.startswith("$argon2id$")
    assert verify_password(digest, "S3cure-passphrase!")
    assert not verify_password(digest, "wrong-password")


def test_malformed_stored_hash_counts_as_no_match() -> None:
    assert not verify_password("garbage-not-a-hash", "whatever")


def test_unknown_account_burns_equal_work_and_fails() -> None:
    # Explicitly exercise the unknown-account path (hash arg None) and the
    # dummy-hash constant to keep both 401 branches symmetric.
    assert DUMMY_HASH.startswith("$argon2id$")
    assert not verify_login_attempt(None, "any-password")
    assert verify_login_attempt(hash_password("right-password"), "right-password")


def test_tokens_are_digest_stored_never_reversible() -> None:
    token = generate_token()
    digest = token_digest(token)
    assert token != digest
    assert len(digest) == 64  # sha256 hex
    assert token_digest(token) == digest
    assert token_digest(generate_token()) != digest


def test_verification_email_template_has_one_useable_link() -> None:
    subject, body = build_verification_email("abc-token-value", "u@example.test")
    assert subject == "Verify your Vistaro account"
    assert "/auth/verify?token=abc-token-value" in body


def test_recording_sender_is_a_fake_that_records_without_delivery() -> None:
    sender = RecordingEmailSender()
    sender.send("to@example.test", "Subject", "Body with token")
    assert len(sender.sent) == 1
    assert sender.sent[0].subject == "Subject"


def test_get_email_sender_prefers_resend_when_key_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from vistaro.core.config import settings

    monkeypatch.setattr(settings, "resend_api_key", "test-key")
    assert isinstance(get_email_sender(), ResendHttpSender)
    monkeypatch.setattr(settings, "resend_api_key", "")
    assert isinstance(get_email_sender(), MailpitSmtpSender)


def test_mailpit_delivers_the_link_when_mailpit_is_up() -> None:
    """Integration check against the compose stack's Mailpit (labeled).

    Skipped when Mailpit is not reachable, matching the DB fixture pattern.
    """
    import smtplib

    import httpx

    try:
        MailpitSmtpSender("localhost", 1025, "Vistaro <no-reply@vistaro.local>").send(
            "verify@example.test",
            f"AUTH-001 mailpit check {uuid.uuid4().hex}",
            f"http://127.0.0.1:8000/auth/verify?token={generate_token()}",
        )
    except (ConnectionError, OSError, smtplib.SMTPException):
        pytest.skip("Mailpit is not reachable")

    deadline = datetime.now(tz=UTC) + timedelta(seconds=10)
    while datetime.now(tz=UTC) < deadline:
        response = httpx.get("http://localhost:8025/api/v1/messages")
        if response.json()["total"] >= 1:
            subjects = [m["Subject"] for m in response.json()["messages"]]
            assert any("AUTH-001 mailpit check" in s for s in subjects)
            return
    pytest.fail("Mailpit did not surface the message within 10s")
