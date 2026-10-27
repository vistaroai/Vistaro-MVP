"""Email delivery abstraction (AUTH-001).

Two senders and one recording fake:

- :class:`MailpitSmtpSender` (local dev: ``infra/docker-compose.yml`` ships
  Mailpit on ``smtp://localhost:1025``; read mail at ``http://localhost:8025``)
- :class:`ResendHttpSender` (staging/production via the Resend HTTP API once
  ``RESEND_API_KEY`` is set in the platform secret store — never in git)
- :class:`RecordingEmailSender` (tests; clearly labeled FAKE)

None of them ever logs the message body: bodies can contain verification
links whose tokens must not appear in logs (TASK_PLAYBOOK AUTH-001
watch-for).
"""

import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Protocol

import httpx

from vistaro.core.config import settings

logger = logging.getLogger(__name__)

#: Verification links point at the API directly (the web verification page
#: is UI-001); ``api_base_url`` differs per environment.
VERIFY_PATH = "/auth/verify"


class EmailSender(Protocol):
    """Minimal protocol any delivery backend must satisfy."""

    def send(self, to_email: str, subject: str, body: str) -> None:
        """Deliver one plain-text email; raise on failure."""
        ...


@dataclass(frozen=True)
class SentEmail:
    """One recorded message (recorded by the FAKE sender for assertions)."""

    to_email: str
    subject: str
    body: str


class MailpitSmtpSender:
    """SMTP sender aimed at the local Mailpit container."""

    def __init__(self, host: str, port: int, from_email: str) -> None:
        self.host = host
        self.port = port
        self.from_email = from_email

    def send(self, to_email: str, subject: str, body: str) -> None:
        """Send one plain-text mail via blocking SMTP (sync endpoints only)."""
        message = EmailMessage()
        message["From"] = self.from_email
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)
        with smtplib.SMTP(self.host, self.port, timeout=5) as smtp:
            smtp.send_message(message)
        logger.info("email sent via SMTP host=%s port=%s", self.host, self.port)


class ResendHttpSender:
    """HTTPS sender using the Resend REST API (staging/production)."""

    def __init__(self, api_key: str, from_email: str) -> None:
        self.api_key = api_key
        self.from_email = from_email

    def send(self, to_email: str, subject: str, body: str) -> None:
        """Send one plain-text mail via the Resend API; raise on errors."""
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "text": body,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        logger.info("email sent via Resend")


class RecordingEmailSender:  # pragma: no cover - exercised in tests by name
    """FAKE sender for tests: records messages, delivers nothing."""

    def __init__(self) -> None:
        self.sent: list[SentEmail] = []

    def send(self, to_email: str, subject: str, body: str) -> None:
        """Record the message; never touches a network."""
        self.sent.append(SentEmail(to_email=to_email, subject=subject, body=body))


def get_email_sender() -> EmailSender:
    """Pick the sender from settings: Resend when a key exists, else Mailpit."""
    if settings.resend_api_key:
        return ResendHttpSender(settings.resend_api_key, settings.email_from)
    return MailpitSmtpSender(settings.smtp_host, settings.smtp_port, settings.email_from)


def build_verification_email(token: str, to_email: str) -> tuple[str, str]:
    """Return ``(subject, body)`` for one signup verification link."""
    subject = "Verify your Vistaro account"
    link = f"{settings.api_base_url}{VERIFY_PATH}?token={token}"
    body = (
        f"Hello {to_email},\n\n"
        "Welcome to Vistaro. Confirm this email address to activate your "
        "account:\n\n"
        f"{link}\n\n"
        "The link is valid for 24 hours and can be used once. "
        "If you did not sign up, ignore this email."
    )
    return subject, body
