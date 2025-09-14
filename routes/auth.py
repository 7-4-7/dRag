import os
import shutil
from fastapi import APIRouter, Request
from authlib.integrations.starlette_client import OAuth
from fastapi.responses import FileResponse, RedirectResponse
from backend.config import CLIENT_ID, CLIENT_SECRET, PINECONE_API_KEY
from pinecone import Pinecone

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

@router.get("/logout")
async def logout(request: Request):
    if "user" in request.session:
        user_email = request.session["user"].get("email")
        if user_email:
            # Delete Pinecone vectors
            try:
                pc = Pinecone(api_key=PINECONE_API_KEY)
                index = pc.Index('draggg')
                index.delete(delete_all=True, namespace=user_email)
            except Exception as e:
                print(f"Error deleting Pinecone vectors for {user_email}: {e}")

            # Delete kb_dir for the user
            kb_dir_base = "backend/storage/kb"  # adjust this path if needed
            user_kb_dir = os.path.join(kb_dir_base, user_email)

            if os.path.exists(user_kb_dir):
                try:
                    shutil.rmtree(user_kb_dir)
                    print(f"Deleted knowledge base directory: {user_kb_dir}")
                except Exception as e:
                    print(f"Error deleting KB directory for {user_email}: {e}")
            else:
                print(f"No KB directory found for user: {user_email}")

    request.session.clear()
    return RedirectResponse(url="/auth/login")
