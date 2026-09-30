import secrets
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from ..config import get_settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]

def _flow() -> Flow:
    config = {"web": {"client_id": get_settings().google_client_id, "client_secret": get_settings().google_client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [get_settings().google_redirect_uri]}}
    return Flow.from_client_config(config, scopes=SCOPES, redirect_uri=get_settings().google_redirect_uri)

@router.get("/google")
def begin_google(request: Request):
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(503, "Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.")
    state = secrets.token_urlsafe(32)
    request.session["google_oauth_state"] = state
    url, _ = _flow().authorization_url(access_type="offline", include_granted_scopes="true", prompt="consent", state=state)
    return RedirectResponse(url)

@router.get("/google/callback")
def google_callback(request: Request, state: str, code: str):
    if state != request.session.pop("google_oauth_state", None):
        raise HTTPException(400, "Invalid OAuth state")
    # Token exchange and account association occur here once the application user session is implemented.
    # Credentials must be encrypted with security.encrypt_secret before persistence.
    return {"status": "authorized", "detail": "OAuth callback validated; associate credentials with the signed-in application user."}
