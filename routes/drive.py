from fastapi import APIRouter, HTTPException, Request
import httpx
from pydantic import BaseModel


router = APIRouter(prefix='/drive', tags=['drive'])


@router.get('/')
def health_check():
    return {'message' : 'In Drive route'}

@router.get('/get_all_files')
async def get_all_files(request : Request):
    user = request.session.get("user")
    token = request.session.get('access_token')

    if not user or not token:
        raise HTTPException(status_code=400,
                            detail = 'Authentication Incomplete')
    
    try:
        headers = {'Authorization' : f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/drive/v3/files",
                headers = headers,
                params = {"pageSize": 100, "fields": "files(id,name,mimeType)"}
            )
            
            response.raise_for_status()
            files = response.json().get("files", [])
            return {'files':files}
    except Exception as e:
        print('sddsdsds')
        print(e)
        raise HTTPException(status_code=400, detail='Error occured while obtaining files')
            
@router.post('/download_files')
def download_files():
    
    

