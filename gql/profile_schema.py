import strawberry
from typing import List, Optional
from database import db

@strawberry.type
class ProfileType:
    id: str
    user_id: str
    full_name: str
    dob: str
    gender: str
    email: str
    address: str
    photo_url: Optional[str]

@strawberry.type
class ProfileQuery:
    @strawberry.field
    async def all_profiles(self) -> List[ProfileType]:
        profiles_cursor = db["profiles"].find()
        profiles = await profiles_cursor.to_list(length=None)
        return [
            ProfileType(
                id=str(p["_id"]),
                user_id=str(p["user_id"]),
                full_name=p.get("full_name", ""),
                dob=p.get("dob", ""),
                gender=p.get("gender", ""),
                email=p.get("email", ""),
                address=p.get("address", ""),
                photo_url=p.get("photo_url")
            )
            for p in profiles
        ]
