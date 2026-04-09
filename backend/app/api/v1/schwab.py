"""Schwab / Thinkorswim integration endpoints.

S1 — Authentication:
  GET  /schwab/status      → connection status + token expiry
  GET  /schwab/auth-url    → returns OAuth2 URL for browser login
  POST /schwab/callback    → exchanges authorization code for token
  POST /schwab/disconnect  → deletes stored token
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services import schwab_client

router = APIRouter(prefix="/schwab", tags=["schwab"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class SchwabStatusResponse(BaseModel):
    connected: bool
    token_age_days: float | None
    refresh_expires_in_days: float | None
    needs_relogin: bool
    message: str


class SchwabAuthUrlResponse(BaseModel):
    auth_url: str
    instructions: str


class SchwabCallbackRequest(BaseModel):
    redirected_url: str


class SchwabCallbackResponse(BaseModel):
    success: bool
    message: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/status", response_model=SchwabStatusResponse)
async def get_schwab_status(current_user: User = Depends(get_current_user)):
    """Check Schwab connection status and token expiry."""
    status = await schwab_client.get_connection_status()

    if not status["connected"]:
        message = "No conectado. Usa /schwab/auth-url para iniciar sesión."
    elif status["needs_relogin"]:
        message = "Token próximo a expirar. Re-autentícate pronto."
    else:
        days = status["refresh_expires_in_days"]
        message = f"Conectado. Token válido por {days:.1f} días más."

    return SchwabStatusResponse(**status, message=message)


@router.get("/auth-url", response_model=SchwabAuthUrlResponse)
async def get_auth_url(current_user: User = Depends(get_current_user)):
    """Get the Schwab OAuth2 URL. Open it in your browser to log in."""
    if not schwab_client.settings.schwab_app_key:
        raise HTTPException(
            status_code=503,
            detail="SCHWAB_APP_KEY no está configurado en el servidor.",
        )

    url = schwab_client.get_auth_url()
    return SchwabAuthUrlResponse(
        auth_url=url,
        instructions=(
            "1. Abre la URL en tu navegador.\n"
            "2. Inicia sesión con tu cuenta Schwab/Thinkorswim.\n"
            "3. Después del login, serás redirigido a https://127.0.0.1 "
            "(puede mostrar error de conexión — eso es normal).\n"
            "4. Copia la URL completa de la barra del navegador y "
            "envíala a POST /schwab/callback."
        ),
    )


@router.post("/callback", response_model=SchwabCallbackResponse)
async def handle_callback(
    body: SchwabCallbackRequest,
    current_user: User = Depends(get_current_user),
):
    """Exchange the OAuth2 callback URL for tokens.

    After logging in via the auth URL, Schwab redirects to https://127.0.0.1?code=...
    Paste that full redirected URL here to complete authentication.
    """
    try:
        await schwab_client.exchange_code_for_token(body.redirected_url)
        return SchwabCallbackResponse(
            success=True,
            message="¡Cuenta Schwab conectada exitosamente! Token guardado.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/disconnect")
async def disconnect(current_user: User = Depends(get_current_user)):
    """Remove stored Schwab token. Requires re-authentication to reconnect."""
    await schwab_client._delete_token()
    return {"success": True, "message": "Cuenta Schwab desconectada."}
