from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from database import db
from models.admin.category_model import Category, PyObjectId
from utils.token_helper import admin_only
from bson import ObjectId
from typing import List
import os, uuid, shutil

router = APIRouter()
CATEGORY_UPLOAD_FOLDER = "uploads/categories"
os.makedirs(CATEGORY_UPLOAD_FOLDER, exist_ok=True)

class CategoryCreate(BaseModel):
    name: str

def save_image(file: UploadFile):
    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(CATEGORY_UPLOAD_FOLDER, filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return path.replace("\\", "/")

@router.post("/create", dependencies=[Depends(admin_only)])
async def create_category(
    name: str = Form(...),
    image: UploadFile = File(...)
):
    existing = await db["categories"].find_one({"name": name})
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    image_path = save_image(image)
    category_data = {
        "name": name,
        "image": image_path
    }
    result = await db["categories"].insert_one(category_data)
    return {"id": str(result.inserted_id), "name": name, "image": image_path}

@router.get("/all")
async def get_all_categories():
    categories = await db["categories"].find().to_list(length=None)
    return [{
        "id": str(cat["_id"]),
        "name": cat["name"],
        "image": cat.get("image", "")
    } for cat in categories]

@router.put("/{category_id}", dependencies=[Depends(admin_only)])
async def update_category(
    category_id: str,
    name: str = Form(...),
    image: UploadFile = File(None)
):
    update_data = {"name": name}
    if image:
        image_path = save_image(image)
        update_data["image"] = image_path

    result = await db["categories"].update_one(
        {"_id": ObjectId(category_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category updated"}

@router.delete("/{category_id}", dependencies=[Depends(admin_only)])
async def delete_category(category_id: str):
    result = await db["categories"].delete_one({"_id": ObjectId(category_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}
