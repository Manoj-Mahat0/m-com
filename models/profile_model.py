from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional


# Helper to use ObjectId with Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


# =======================
# User Model
# =======================
class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    phone_number: str
    is_verified: bool = False
    is_profile_complete: bool = False

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# =======================
# User Profile Model
# =======================
class UserProfile(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    user_id: PyObjectId
    full_name: str = ""
    dob: str = ""
    gender: str = ""
    email: EmailStr = ""
    address: str = ""
    photo_url: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
