from datetime import datetime
import stripe
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from database import db
from utils.token_helper import get_current_user
from config import Key

router = APIRouter()
stripe.api_key = Key

@router.post("/create-checkout-session")
async def create_checkout_session(address_id: str, user: dict = Depends(get_current_user)):
    cart_items = await db["cart"].find({"user_id": user["user_id"]}).to_list(length=None)
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    product_ids = [ObjectId(item["product_id"]) for item in cart_items]
    products = await db["products"].find({"_id": {"$in": product_ids}}).to_list(length=None)

    line_items = []
    for item in cart_items:
        product = next((p for p in products if str(p["_id"]) == str(item["product_id"])), None)
        if product:
            line_items.append({
                "price_data": {
                    "currency": "inr",
                    "product_data": {"name": product["name"]},
                    "unit_amount": int(product["price"] * 100),
                },
                "quantity": item["quantity"],
            })

    if not line_items:
        raise HTTPException(status_code=400, detail="No valid products found")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=f"http://localhost:8501/?address_id={address_id}&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url="http://localhost:8000/payment-cancelled",
        )
        return {"payment_url": session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cod-order")
async def create_cod_order(address_id: str, user: dict = Depends(get_current_user)):
    cart_items = await db["cart"].find({"user_id": user["user_id"]}).to_list(length=None)
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    product_ids = [ObjectId(item["product_id"]) for item in cart_items]
    products = await db["products"].find({"_id": {"$in": product_ids}}).to_list(length=None)

    total_amount = 0
    order_items = []
    for item in cart_items:
        product = next((p for p in products if str(p["_id"]) == str(item["product_id"])), None)
        if product:
            order_items.append({
                "product_id": str(product["_id"]),
                "name": product["name"],
                "price": product["price"],
                "quantity": item["quantity"]
            })
            total_amount += product["price"] * item["quantity"]

    order = {
        "user_id": user["user_id"],
        "address_id": address_id,
        "items": order_items,
        "total": total_amount,
        "payment_mode": "COD",
        "status": "PENDING",  # you can change to "PLACED" if needed
        "created_at": datetime.utcnow()
    }

    result = await db["orders"].insert_one(order)
    await db["cart"].delete_many({"user_id": user["user_id"]})  # optional

    return {"message": "COD order placed successfully", "order_id": str(result.inserted_id)}

@router.get("/orders")
async def get_all_orders():
    orders = await db["orders"].find().sort("created_at", -1).to_list(length=None)

    formatted_orders = []
    for order in orders:
        created_at = order.get("created_at")
        created_at_str = created_at.isoformat() if created_at else ""

        formatted_orders.append({
            "order_id": str(order.get("_id")),
            "user_id": order.get("user_id", "N/A"),
            "address_id": order.get("address_id", "N/A"),
            "items": order.get("items", []),
            "total": order.get("total", 0),
            "payment_mode": order.get("payment_mode", "UNKNOWN"),
            "status": order.get("status", "PENDING"),
            "created_at": created_at_str
        })

    return formatted_orders

