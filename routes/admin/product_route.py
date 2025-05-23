from bson import ObjectId
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Body
from typing import List
from database import db
from utils.token_helper import admin_only
import os, uuid, shutil

router = APIRouter()
UPLOAD_FOLDER = "uploads/products"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_file(file: UploadFile):
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path.replace("\\", "/")

@router.post("/add")
async def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category_id: str = Form(...),
    feature_image: UploadFile = File(...),
    product_images: List[UploadFile] = File(...),
    _: dict = Depends(admin_only)
):
    category = await db["categories"].find_one({"_id": ObjectId(category_id)})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    feature_img_path = save_file(feature_image)
    additional_images = [save_file(img) for img in product_images]

    product = {
        "name": name,
        "description": description,
        "price": price,
        "category": {
            "id": str(category["_id"]),
            "name": category["name"]
        },
        "feature_image": feature_img_path,
        "product_images": additional_images,
    }

    result = await db["products"].insert_one(product)
    return {"message": "Product added", "product_id": str(result.inserted_id)}

@router.get("/all")
async def get_products(_: dict = Depends(admin_only)):
    products = await db["products"].find().to_list(length=None)
    return [{**p, "_id": str(p["_id"])} for p in products]

@router.put("/edit/{product_id}")
async def edit_product(
    product_id: str,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category_id: str = Form(...),
    feature_image: UploadFile = File(None),
    product_images: List[UploadFile] = File(None),
    _: dict = Depends(admin_only)
):
    category = await db["categories"].find_one({"_id": ObjectId(category_id)})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = {
        "name": name,
        "description": description,
        "price": price,
        "category": {
            "id": str(category["_id"]),
            "name": category["name"]
        }
    }

    if feature_image:
        update_data["feature_image"] = save_file(feature_image)

    if product_images:
        update_data["product_images"] = [save_file(img) for img in product_images]

    result = await db["products"].update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found or not changed")
    return {"message": "Product updated"}

@router.delete("/delete/{product_id}")
async def delete_product(product_id: str, _: dict = Depends(admin_only)):
    result = await db["products"].delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}

@router.patch("/admin/update-order-status/{order_id}")
async def update_order_status_admin(
    order_id: str,
    new_status: str = Body(..., embed=True),
    _: dict = Depends(admin_only)
):
    update_result = await db["orders"].update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": new_status}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found or status unchanged")

    return {"message": f"Order status updated to '{new_status}'"}


#["PENDING", "PLACED", "SHIPPED", "DELIVERED", "CANCELLED"]
