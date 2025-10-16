import pytest
from app.tasks import (
    APIResponseError,
    send_email,
)
from requests.models import Response


@pytest.mark.anyio
async def test_send_email(mock_mailtrap_post):
    await send_email("test@example.net", "Test Subject", "Test Body")
    mock_mailtrap_post.assert_called_once()


@pytest.mark.anyio
async def test_send_email_api_error(mock_mailtrap_post):
    failed_response = Response()
    failed_response.status_code = 500
    failed_response._content = b"Internal Server Error"

    mock_mailtrap_post.return_value = failed_response

    with pytest.raises(APIResponseError):
        await send_email("test@example.net", "Test Subject", "Test Body")
