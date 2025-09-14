from fastapi import APIRouter, HTTPException, Request
import httpx
from pydantic import BaseModel
from pathlib import Path
from typing import List

router = APIRouter(prefix='/drive', tags=['drive'])
kb_dir = Path('backend/rag/kb')

class DownloadRequest(BaseModel):
    ids : List[str]

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
            
class DownloadRequest(BaseModel):
    file_ids: List[str]
    web_search: bool


@router.post('/download_files')
async def download_files(payload: DownloadRequest, request: Request):
    user = request.session.get("user")
    token = request.session.get('access_token')

    if not user or not token:
        raise HTTPException(status_code=400, detail='Authentication Incomplete')

    headers = {'Authorization': f"Bearer {token}"}
    kb_dir.mkdir(parents=True, exist_ok=True)

    downloaded = []
    errors = []

    async with httpx.AsyncClient() as client:
        for file_id in payload.file_ids:
            try:
                meta_url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
                meta_resp = await client.get(meta_url, headers=headers, params={"fields": "name"})
                meta_resp.raise_for_status()
                file_name = meta_resp.json()["name"]

                # Step 2: Download file content
                download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
                content_resp = await client.get(download_url, headers=headers)
                content_resp.raise_for_status()

                # Step 3: Save to kb_dir
                file_path = kb_dir / file_name
                with open(file_path, "wb") as f:
                    f.write(content_resp.content)

                downloaded.append(file_name)
            except Exception as e:
                errors.append({file_id: str(e)})

    return {
        "message": f"{len(downloaded)} file(s) downloaded to knowledge base.",
        "downloaded_files": downloaded,
        "errors": errors,
        "web_search_enabled": payload.web_search
    }
