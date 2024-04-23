import io
import os
from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

router = APIRouter()
root_assets = os.path.join(os.getcwd(), "public\\assets")
@router.get("/apis/download/{file_hash}/{file_name}")
async def preview(file_hash: str, file_name: str):
    file_path = os.path.join(root_assets, "files", file_hash, file_name)
    
    if os.path.exists(file_path):
        file_extension = file_name.split(".")[-1].lower()
        
        if file_extension in ['pdf', 'jpg', 'jpeg', 'png', 'gif']:
            file_content = open(file_path, "rb").read()
            return StreamingResponse(io.BytesIO(file_content), media_type=f'application/{file_extension}')
        else:
            return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)
    
    return JSONResponse(content={"error": "File not found"}, status_code=404)


