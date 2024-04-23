import json
import os
from pathlib import Path
from typing import List, Optional, TypedDict
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import pandas as pd
import pdfplumber
from pydantic import BaseModel
from pdf2docx import Converter

router = APIRouter()
root_assets = os.path.join(os.getcwd(), "public\\assets")


class DataItem(TypedDict):
    url: str
    filename: str


class FilesQuery(BaseModel):
    data: List[DataItem]
    code: Optional[int]
    message: Optional[str]


@router.get("/apis/files/query")
async def filesQuery():
    path = os.path.join(root_assets, "cache.json")
    if not os.path.exists(path):
        return JSONResponse(content={"data": [], "code": 0, "message": "success"})

    with open(path, "r") as files:
        data = json.load(files)
        arr = []
        for key in data:
            arr.append({"url": f"\\{key}\\{data[key]}", "filename": data[key]})

    return JSONResponse(content={"data": arr, "code": 0, "message": "success"})


class TransitionResponse(BaseModel):
    fileUrl: str
    type: str


@router.post("/apis/pdf/transition", response_model=TransitionResponse)
async def pdf_transition(params: Request):
    data = await params.json()
    fileUrl = data.get("fileUrl")
    type = data.get("type")
    if not type:
        return JSONResponse(content={"message": 'The "typs" is missing!'})
    file_path = os.path.join(
        root_assets, "files", fileUrl[1:] if fileUrl[0] == "\\" else fileUrl
    )
    if os.path.exists(file_path):
        run_func = to_word if type == "word" else to_excel
        result = run_func(file_path)
        file_url = result.replace(os.path.join(root_assets, "files"), "")
        return JSONResponse(content={"data": file_url, "message": "failed", "code": 1})
    return JSONResponse(content={"data": False, "message": "failed", "code": 1})


def to_word(path: str):
    # 输出的Word文档路径
    docx_file = path.replace(".pdf", ".docx")
    if os.path.exists(docx_file):
        return docx_file

    # 创建一个转换器
    cv = Converter(path)

    with pdfplumber.open(path) as pdf:
        cv.convert(docx_file, start=0, end=len(pdf.pages))
    # 释放资源
    cv.close()
    return docx_file


def to_excel(path: str):
    # 将DataFrame写入Excel文件
    output_path = path.replace(".pdf", ".xlsx")
    if os.path.exists(output_path):
        return output_path
    # 创建一个Pdf实例
    with pdfplumber.open(path) as pdf:
        all_data = []
        header = None
        for page in pdf.pages:
            table = page.extract_table()
            if header is None:
                header = table[0]
                all_data.extend(table)
            else:
                all_data.extend([row for row in table if row != header])

    # 将提取的表格数据转换为pandas DataFrame
    df = pd.DataFrame(all_data[1:], columns=all_data[0])

    df.to_excel(output_path, index=False)
    return output_path


@router.delete("/apis/delete_file/{file_hash}/{file_name}")
async def delete_file(file_hash: str, file_name: str):
    file_path = os.path.join(root_assets, "files", file_hash, file_name)

    path = os.path.join(root_assets, "cache.json")
    with open(path, "r") as cache:
        data = json.load(cache)
        if file_hash in data:
            del data[file_hash]
        else:
            return {"message": "file is not exists"}

    with open(path, "w") as write_catche:
        json.dump(data or {}, write_catche, indent=2)

    file_to_delete = (
        Path(os.path.dirname(file_path))
        if os.path.isfile(file_path)
        else Path(file_path)
    )

    if os.path.isfile(file_path):
        for child in file_to_delete.iterdir():
            child.unlink()
        file_to_delete.rmdir()
    else:
        file_to_delete.unlink()
    return {"message": "File deleted successfully"}
