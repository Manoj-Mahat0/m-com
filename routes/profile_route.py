from fastapi import APIRouter, Form, HTTPException, Depends
from database import db
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from schemas.user_schema import UserIDResponse
from utils.token_helper import get_current_user

router = APIRouter()

class ProfileUpdate(BaseModel):
    full_name: str
    dob: str
    gender: str
    email: EmailStr
    address: str

@router.post("/update-profile")
async def update_profile(data: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]

    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update or insert profile
    profile_data = {
        "user_id": ObjectId(user_id),
        "full_name": data.full_name,
        "dob": data.dob,
        "gender": data.gender,
        "email": data.email,
        "address": data.address,
    }

    profile = await db["profiles"].find_one({"user_id": ObjectId(user_id)})

    if profile:
        await db["profiles"].update_one({"user_id": ObjectId(user_id)}, {"$set": profile_data})
    else:
        await db["profiles"].insert_one(profile_data)

    # Mark profile as complete
    await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_profile_complete": True}}
    )

    return {"message": "Profile updated successfully"}


@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]

    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    profile = await db["profiles"].find_one({"user_id": ObjectId(user_id)})

    if not user or not profile:
        raise HTTPException(status_code=404, detail="User or profile not found")

    return {
        "phone_number": user.get("phone_number"),
        "is_verified": user.get("is_verified", False),
        "is_profile_complete": user.get("is_profile_complete", False),
        "profile": {
            "full_name": profile.get("full_name", ""),
            "dob": profile.get("dob", ""),
            "gender": profile.get("gender", ""),
            "email": profile.get("email", ""),
            "address": profile.get("address", ""),
            "photo_url": profile.get("photo_url")
        }
    }

# ✅ Address creation with type
@router.post("/add-address")
async def add_address(
    address: str = Form(...),
    type: str = Form(...),  # home, office, family, friends, other
    user: dict = Depends(get_current_user)
):
    if type not in ["home", "office", "family", "friends", "other"]:
        raise HTTPException(status_code=400, detail="Invalid address type")

    await db["addresses"].insert_one({
        "user_id": user["user_id"],
        "address": address,
        "type": type
    })
    return {"message": "Address added successfully"}

@router.get("/addresses")
async def get_addresses(user: dict = Depends(get_current_user)):
    addresses = await db["addresses"].find({"user_id": user["user_id"]}).to_list(length=None)
    return [{"id": str(a["_id"]), "address": a["address"], "type": a["type"]} for a in addresses]
