from fastapi import APIRouter, Request, HTTPException
from authlib.integrations.starlette_client import OAuth
from fastapi.responses import FileResponse

from backend.config import CLIENT_ID, CLIENT_SECRET, SECRET_KEY

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth setup
oauth = OAuth()
oauth.register(
    name="google",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile https://www.googleapis.com/auth/drive.readonly"},
)

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("callback")
    return await oauth.google.authorize_redirect(request, redirect_uri, access_type="offline", prompt="consent")

@router.get("/callback")
async def callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token['userinfo']
    request.session["user"] = dict(userinfo)
    request.session["access_token"] = token["access_token"]
    return FileResponse("backend/static/chat.html")


@router.get("/me")
async def me(request: Request):
        return {"token": request.session["access_token"]}
