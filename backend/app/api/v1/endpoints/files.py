from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse

from app.core.dependencies import get_current_user_id
from app.services.storage import upload_file, get_presigned_upload_url

router = APIRouter()


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    user_id=Depends(get_current_user_id),
):
    content = await file.read()
    url = upload_file(content, file.filename or "unknown", file.content_type or "application/octet-stream")
    return {"file_url": url, "file_name": file.filename, "content_type": file.content_type}


@router.post("/upload-url")
async def get_upload_url(
    file_name: str = Query(...),
    content_type: str = Query("application/octet-stream"),
    user_id=Depends(get_current_user_id),
):
    result = get_presigned_upload_url(file_name, content_type)
    return result
