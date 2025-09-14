from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from backend.routes import auth, drive, rag
from backend.config import SECRET_KEY
from fastapi.responses import FileResponse
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",  
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=86400,
    same_site="lax",
    https_only=False,
)

app.include_router(auth.router)
app.include_router(drive.router)
app.include_router(rag.router)

@app.get("/")
def initial(request : Request):
    user = request.session.get('user')
    if not user:
        return FileResponse("backend/static/index.html")
    return FileResponse("backend/static/chat.html")

