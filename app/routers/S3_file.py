from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import boto3
import os

from app.database import SessionLocal
from app.models import FileRecord

router = APIRouter()

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# AWS S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")


@router.post("/upload")
async def upload_file(file: UploadFile, db: Session = Depends(get_db)):
    try:
        # Extract file extension
        filename, file_extension = os.path.splitext(file.filename)

        # Add Month-Day to filename
        date_suffix = datetime.now().strftime("%m%d")
        new_filename = f"{filename}_{date_suffix}{file_extension}"

        # Upload to S3
        s3_client.upload_fileobj(file.file, BUCKET_NAME, new_filename)

        # Save file details to DB
        file_record = FileRecord(
            original_name=file.filename,
            stored_name=new_filename,
            bucket_name=BUCKET_NAME
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        return {"message": f"File '{new_filename}' uploaded successfully", "file_id": file_record.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files")
def list_files(db: Session = Depends(get_db)):
    files = db.query(FileRecord).all()
    return files


@router.delete("/files/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    file_record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete from S3
    s3_client.delete_object(Bucket=file_record.bucket_name, Key=file_record.stored_name)

    # Delete from DB
    db.delete(file_record)
    db.commit()

    return {"message": f"File '{file_record.stored_name}' deleted successfully"}


@router.get("/download/{file_id}")
def download_file(file_id: int, db: Session = Depends(get_db)):
    file_record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    # Generate a presigned URL for downloading
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': file_record.bucket_name, 'Key': file_record.stored_name},
        ExpiresIn=3600
    )
    return {"download_url": url}