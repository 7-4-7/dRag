from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from authlib.common.errors import AuthlibBaseError
from backend.config import CLIENT_ID, CLIENT_SECRET
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
    try:
        redirect_uri = "http://localhost:5000/auth/callback"
        logger.info(f"Starting OAuth login")
        logger.info(f"CLIENT_ID (first 10 chars): {CLIENT_ID[:10]}...")
        logger.info(f"Using redirect_uri: {redirect_uri}")
        logger.info(f"Request URL: {request.url}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        response = await oauth.google.authorize_redirect(request, redirect_uri)
        logger.info(f"Authorization redirect created successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error in login endpoint: {e}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f'Login failed: {str(e)}')

@router.get("/callback")
async def callback(request: Request):
    try:
        logger.info(f"=== CALLBACK STARTED ===")
        logger.info(f"Full callback URL: {request.url}")
        logger.info(f"Query parameters: {dict(request.query_params)}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        error = request.query_params.get('error')
        if error:
            error_description = request.query_params.get('error_description', 'Unknown error')
            logger.error(f"OAuth error received: {error} - {error_description}")
            raise HTTPException(status_code=400, detail=f'OAuth error: {error_description}')
 
        code = request.query_params.get('code')
        state = request.query_params.get('state')
        logger.info(f"Authorization code present: {bool(code)}")
        logger.info(f"State parameter present: {bool(state)}")
        
        if not code:
            logger.error("No authorization code received")
            raise HTTPException(status_code=400, detail='No authorization code received')
        
        logger.info("Attempting token exchange...")
        token = await oauth.google.authorize_access_token(request)
        logger.info("Token exchange successful")
        logger.info(f"Token keys: {list(token.keys()) if token else 'None'}")

        logger.info("Fetching user info...")
        userinfo_response = await oauth.google.get("https://www.googleapis.com/oauth2/v3/userinfo", token=token)
        userinfo = userinfo_response.json()
        logger.info(f"User info received for: {userinfo.get('email', 'unknown')}")

        request.session['user'] = userinfo
        logger.info("User stored in session successfully")
        
        return RedirectResponse(url="/auth/me")
        
    except AuthlibBaseError as e:
        logger.error(f"Authlib error: {e}")
        logger.error(f"Authlib error type: {type(e)}")
        raise HTTPException(status_code=400, detail=f'OAuth2 authentication failed: {str(e)}')
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in callback: {e}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f'OAuth2 login failed: {str(e)}')

@router.get("/me")
async def me(request: Request):
    user = request.session.get("user")
    if user:
        return user
    raise HTTPException(status_code=401, detail='Not logged in')

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return {'message': 'logout success'}