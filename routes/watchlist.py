from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from database import db
from utils.token_helper import get_current_user

router = APIRouter()

@router.post("/watchlist/add/{product_id}")
async def add_to_watchlist(product_id: str, user: dict = Depends(get_current_user)):
    await db["watchlist"].update_one(
        {"user_id": user["user_id"]},
        {"$addToSet": {"product_ids": ObjectId(product_id)}},
        upsert=True
    )
    return {"message": "Product added to watchlist"}


@router.get("/watchlist")
async def get_watchlist(user: dict = Depends(get_current_user)):
    watchlist = await db["watchlist"].find_one({"user_id": user["user_id"]})
    product_ids = watchlist.get("product_ids", []) if watchlist else []
    products = await db["products"].find({"_id": {"$in": product_ids}}).to_list(length=None)
    return [{**p, "_id": str(p["_id"])} for p in products]


@router.delete("/watchlist/remove/{product_id}")
async def remove_from_watchlist(product_id: str, user: dict = Depends(get_current_user)):
    result = await db["watchlist"].update_one(
        {"user_id": user["user_id"]},
        {"$pull": {"product_ids": ObjectId(product_id)}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found in watchlist")
    return {"message": "Product removed from watchlist"}
