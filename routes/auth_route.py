from fastapi import APIRouter, HTTPException
from database import db
from utils.token_helper import create_access_token
from models.user_model import User
from models.profile_model import UserProfile
from utils.otp_generator import generate_otp, verify_otp
from bson import ObjectId


auth_router = APIRouter()

@auth_router.post("/send-otp")
async def send_otp(phone_number: str):
    otp = generate_otp(phone_number)
    print(f"OTP sent to {phone_number}: {otp}")

    await db["users"].update_one(
        {"phone_number": phone_number},
        {"$set": {"otp": otp}},  # ✅ store the OTP
        upsert=True              # ✅ create user if doesn't exist
    )

    return {"message": "OTP sent"}


@auth_router.post("/verify-otp")
async def verify_otp_login(phone_number: str, otp: str):
    user = await db["users"].find_one({"phone_number": phone_number})

    # Check if user exists and OTP matches
    if not user or str(user.get("otp")) != str(otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if not user:
        # New user - create record
        new_user = {
            "phone_number": phone_number,
            "is_verified": True,
            "is_profile_complete": False
        }
        result = await db["users"].insert_one(new_user)

        await db["profiles"].insert_one({
            "user_id": result.inserted_id,
            "full_name": "",
            "address": ""
        })

        user_id = result.inserted_id
        is_profile_complete = False
    else:
        # Update existing user as verified
        await db["users"].update_one({"phone_number": phone_number}, {"$set": {"is_verified": True}})
        user_id = user["_id"]
        is_profile_complete = user.get("is_profile_complete", False)

    token = create_access_token(data={
        "user_id": str(user_id),
        "phone_number": phone_number
    })

    return {
        "message": "User logged in",
        "access_token": token,
        "token_type": "bearer",
        "is_profile_complete": is_profile_complete
    }
