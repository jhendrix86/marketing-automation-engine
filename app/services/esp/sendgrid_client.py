"""
Real email delivery via SendGrid's Mail Send API.

https://www.twilio.com/docs/sendgrid/api-reference/mail-send/mail-send
"""

from dataclasses import dataclass
from typing import Optional

import httpx
from loguru import logger

from app.config import settings

_API_URL = "https://api.sendgrid.com/v3/mail/send"


@dataclass
class SendResult:
    success: bool
    error: Optional[str] = None


class SendGridClient:
    def __init__(self):
        self.api_key = settings.sendgrid_api_key

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    async def send_email(self, to_email: str, from_email: str, subject: str, html_content: str) -> SendResult:
        if not self.configured:
            return SendResult(success=False, error="SendGrid is not configured (SENDGRID_API_KEY)")

        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": from_email},
            "subject": subject,
            "content": [{"type": "text/html", "value": html_content or " "}],
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    _API_URL,
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=payload,
                )
        except httpx.HTTPError as exc:
            logger.error(f"SendGrid request failed: {exc}")
            return SendResult(success=False, error=f"SendGrid request failed: {exc}")

        if response.status_code != 202:
            return SendResult(success=False, error=f"SendGrid returned {response.status_code}: {response.text[:300]}")

        return SendResult(success=True)
