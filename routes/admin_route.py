from fastapi import APIRouter, HTTPException, Query
from utils.token_helper import create_access_token

admin_router = APIRouter()

# Hardcoded admin credentials (can be moved to environment variables later)
ADMIN_PHONE = "9876543210"
ADMIN_OTP = "123456"

@admin_router.post("/admin/login")
async def admin_login(
    phone_number: str = Query(...),
    otp: str = Query(...)
):
    if phone_number == ADMIN_PHONE and otp == ADMIN_OTP:
        token = create_access_token({
            "phone_number": phone_number,
            "role": "ADMIN"
        })
        return {
            "message": "Admin logged in successfully",
            "access_token": token,
            "token_type": "bearer"
        }
    raise HTTPException(status_code=401, detail="Invalid admin credentials")
