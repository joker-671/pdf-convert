import hashlib
import json
import os
import shutil
from typing import Optional
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()
root_assets = os.path.join(os.getcwd(), "public\\assets")
if not os.path.exists(root_assets):
    os.makedirs(root_assets, exist_ok=True)

class UplaodResponseData(BaseModel):
    filename:str
    url:str
    exists:Optional[bool]

class UploadResponse(BaseModel):
    data:Optional[UplaodResponseData] 
    message:Optional[str]
    code:int

@router.post("/apis/upload",response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    uploaded_file_hash = hashlib.sha256()
    while chunk := file.file.read(4096):
        uploaded_file_hash.update(chunk)

    upload_hash = uploaded_file_hash.hexdigest()
    file_path = os.path.join(root_assets, f'files\\{upload_hash}\\{file.filename}')

    download_url = f'\\{upload_hash}\\{file.filename}'
    if os.path.exists(file_path):
        return JSONResponse(content={
            "data":{"filename": file.filename, "url": download_url,"exists":True},
            "code": 0,
            "message":"The file is exists!"
        })
    
    file.file.seek(0)
    saveFile(upload_hash, file)
    
    return JSONResponse(content={
        "data":{"filename": file.filename, "url": download_url},
        "code":0,
        "message":'success'
    })

def saveFile(fileHash:str, file:UploadFile = File(...)):
    cache_file_path = os.path.join(root_assets, 'cache.json')
    cache_data = {} #用于查询上传的文件列表
    
    if os.path.exists(cache_file_path):
        with open(cache_file_path, "r") as cache_file:
            cache_data = json.load(cache_file)

    filename = file.filename
    cache_data[fileHash] = filename

    with open(cache_file_path, "w") as cache_file:
        json.dump(cache_data, cache_file, indent=2)

    file_dir = os.path.join(root_assets, "files", fileHash)
    os.makedirs(file_dir, exist_ok=True)
    
    with open(os.path.join(file_dir, filename), "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

def has_file_extension(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension != ""

def check_and_create_file(file_path:str):
    file_dir =  os.path.dirname(file_path) if has_file_extension(file_path) else file_path
    
    if not os.path.exists(file_dir):
        try:
            os.makedirs(file_dir)
            print(f"目录 {file_dir} 不存在，已成功创建。")
        except Exception as e:
            print(f"创建目录 {file_dir} 失败：{e}")
    else:
        print(f"目录 {file_dir} 已经存在。")

    if not os.path.exists(file_path):
        try:
            with open(file_path, 'w') as file:
                if file_path.endswith('.json'):
                    json.dump({}, file, indent=2)
            print(f"文件 {file_path} 不存在，已成功创建。")
        except Exception as e:
            print(f"创建文件 {file_path} 失败：{e}")
    else:
        print(f"文件 {file_path} 已经存在。")

