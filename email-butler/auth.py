"""
auth.py — Gmail OAuth2 authentication
Handles login, token storage, and token refresh.
Run this file directly to log in for the first time.
"""

import logging
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Note: 'gmail.modify' implies 'readonly', but explicit declaration prevents scope reduction errors.
SCOPES: list[str] = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

BASE_DIR: Path = Path(__file__).resolve().parent
CREDENTIALS_FILE: Path = BASE_DIR / "credentials.json"
TOKEN_FILE: Path = BASE_DIR / "token.json"


def get_credentials() -> Credentials:
    """Return valid Gmail credentials, handling refresh and re-authentication."""
    creds = None

    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as e:
            logger.warning(f"Failed to load existing token: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                logger.warning("Token refresh failed. Initiating re-authentication.")
                creds = _execute_auth_flow()
        else:
            creds = _execute_auth_flow()

        TOKEN_FILE.write_text(creds.to_json())

    return creds


def _execute_auth_flow() -> Credentials:
    """Isolate the blocking browser authentication flow."""
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            f"Required credentials file missing: {CREDENTIALS_FILE}"
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    return flow.run_local_server(port=0)


if __name__ == "__main__":
    creds = get_credentials()
    logger.info(f"Authentication verified. Token secured at: {TOKEN_FILE}")
