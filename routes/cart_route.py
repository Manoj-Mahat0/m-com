from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from database import db
from utils.token_helper import get_current_user

router = APIRouter()

@router.post("/add/{product_id}")
async def add_to_cart(product_id: str, quantity: int = 1, user: dict = Depends(get_current_user)):
    product = await db["products"].find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db["cart"].update_one(
        {"user_id": user["user_id"], "product_id": ObjectId(product_id)},
        {"$inc": {"quantity": quantity}},
        upsert=True
    )
    return {"message": "Product added to cart"}


@router.get("/")
async def view_cart(user: dict = Depends(get_current_user)):
    items = await db["cart"].find({"user_id": user["user_id"]}).to_list(length=None)
    
    # Filter out items that don't have 'product_id'
    valid_items = [item for item in items if "product_id" in item]
    product_ids = [item["product_id"] for item in valid_items]

    products = await db["products"].find({"_id": {"$in": product_ids}}).to_list(length=None)
    product_map = {str(p["_id"]): p for p in products}

    cart_response = []
    for item in valid_items:
        pid = str(item["product_id"])
        if pid in product_map:
            cart_response.append({
                "product": {**product_map[pid], "_id": pid},
                "quantity": item["quantity"]
            })

    return cart_response



@router.put("/update/{product_id}")
async def update_quantity(product_id: str, quantity: int, user: dict = Depends(get_current_user)):
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    result = await db["cart"].update_one(
        {"user_id": user["user_id"], "product_id": ObjectId(product_id)},
        {"$set": {"quantity": quantity}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Cart updated"}


@router.delete("/remove/{product_id}")
async def remove_from_cart(product_id: str, user: dict = Depends(get_current_user)):
    result = await db["cart"].delete_one({"user_id": user["user_id"], "product_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Product removed from cart"}
