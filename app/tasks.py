import logging
import requests
import json

from app.config import config

logger = logging.getLogger(__name__)


class APIResponseError(Exception):
    pass


async def send_email(to: str, subject: str, body: str) -> None:
    logger.debug(f"Sending email to '{to}' with subject '{subject[:20]}'")

    url = config.MAILTRAP_HOST

    payload = {
        "from": {
            "email": config.MAILTRAP_FROM_EMAIL,
            "name": config.MAILTRAP_FROM_NAME,
        },
        "to": [{"email": to}],
        "subject": subject,
        "text": body,
        "category": "Integration Test",
    }

    headers = {
        "Authorization": f"Bearer {config.MAILTRAP_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code != 200:
        logger.error(f"Mailtrap API error: {response.status_code} - {response.text}")
        raise APIResponseError(f"Failed to send email: {response.text}")

    logger.debug("Email sent successfully via Mailtrap.")


async def send_user_registration_email(email: str, confirmation_url: str):
    return await send_email(
        email,
        "Successfully signed up",
        (
            f"Hi {email}! You have successfully signed up to the Stores REST API."
            " Please confirm your email by clicking on the"
            f" following link: {confirmation_url}"
        ),
    )
