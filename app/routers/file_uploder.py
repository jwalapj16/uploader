from fastapi import APIRouter, Request, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os
import shutil

router = APIRouter()

templates = Jinja2Templates(directory="app/static")
UPLOAD_FOLDER = "app/uploads"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_class= HTMLResponse)
async def welcome(request: Request):
    return templates.TemplateResponse("index.html",
                                     {"request": request,"name":"Jwala "})


# Upload Page
@router.get("/upload", response_class=HTMLResponse)
def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return {"message": f"File '{file.filename}' uploaded successfully!"}

# Download Page

@router.get("/files", response_class=HTMLResponse)
async def show_files(request: Request):
    # Example: Listing files from a local folder
    file_list = os.listdir("uploads")  # or fetch from S3
    return templates.TemplateResponse("show_files.html", {"request": request, "files": file_list})

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    return {"error": "File not found"}


@router.get("/download", response_class=HTMLResponse)
def list_files(request: Request):
    print("inside folder ")
    files = os.listdir(UPLOAD_FOLDER)
    return templates.TemplateResponse("download.html", {"request": request, "files": files})



@router.get("/delete/{file_name}")
async def delete_file(file_name: str):
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": f"File '{file_name}' deleted"}
    return {"error": "File not found"}