from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from authlib.common.errors import AuthlibBaseError
from config import CLIENT_ID, CLIENT_SECRET, SECRET_KEY
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth Setup
oauth = OAuth()
oauth.register(
    name='google',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={'scope': "openid email profile"},
)

router = APIRouter(prefix='/auth', tags=['auth'])

@router.get('/')
def health_check():
    return {'message': "In auth"}

@router.get("/login")
async def login(request: Request):
    redirect_uri = "http://localhost:8000/auth/callback"
    logger.info(f"Using redirect_uri: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def callback(request: Request):
    try:
        logger.info(f"Callback received with params: {dict(request.query_params)}")
        error = request.query_params.get('error')
        if error:
            error_description = request.query_params.get('error_description', 'Unknown error')
            logger.error(f"OAuth error: {error} - {error_description}")
            raise HTTPException(status_code=400, detail=f'OAuth error: {error_description}')
        
        token = await oauth.google.authorize_access_token(request)
        logger.info("Token exchange successful")
        
        userinfo_response = await oauth.google.get("https://www.googleapis.com/oauth2/v3/userinfo", token=token)
        userinfo = userinfo_response.json()
        
        request.session['user'] = userinfo
        logger.info(f"User logged in: {userinfo.get('email')}")
        return RedirectResponse(url="/auth/me")
        
    except AuthlibBaseError as e:
        logger.error(f"Authlib error: {e}")
        raise HTTPException(status_code=400, detail=f'OAuth2 authentication failed: {str(e)}')
    except Exception as e:
        logger.error(f"Unexpected error in callback: {e}")
        logger.error(f"Request URL: {request.url}")
        logger.error(f"Request params: {dict(request.query_params)}")
        raise HTTPException(status_code=400, detail=f'OAuth2 login failed: {str(e)}')

@router.get("/me")
async def me(request: Request):
    user = request.session.get("user")
    if user:
        return user
    raise HTTPException(status_code=401, detail='Not logged in')

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return {'message' : 'logout success'}