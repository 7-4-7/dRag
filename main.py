from fastapi import FastAPI, Request, Depends, HTTPException
from starlette.middleware.sessions import SessionMiddleware
from backend.routes import auth
from backend.config import SECRET_KEY

app = FastAPI()

# Updated session middleware with proper OAuth configuration
app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY,
    max_age=1800,  # 30 minutes
    same_site='lax',  # Important for OAuth redirects
    https_only=False  # Set to True in production with HTTPS
)

app.include_router(auth.router)
#app.include_router(some_other_router)

@app.get("/")
def health_check():
    return {'message': 'ALIVE !!!!'}

# Optional: Test endpoint to verify sessions are working
@app.get("/test-session")
def test_session(request: Request):
    if 'test' not in request.session:
        request.session['test'] = 'session_working'
        return {"message": "Session created"}
    else:
        return {"message": "Session working", "value": request.session['test']}