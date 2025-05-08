from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from utils.token_helper import get_current_user
from database import db
from bson import ObjectId
import os
import shutil

photo_router = APIRouter()

UPLOAD_DIR = "uploads/profile_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@photo_router.post("/upload-profile-photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    # Save file with unique name
    extension = file.filename.split(".")[-1]
    filename = f"{user_id}.{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save photo path in DB
    profile = await db["profiles"].find_one({"user_id": ObjectId(user_id)})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    await db["profiles"].update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": {"photo_url": file_path}}
    )

    return {
        "message": "Profile photo uploaded successfully",
        "photo_url": file_path
    }
