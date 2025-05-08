# schemas/user_schema.py

from pydantic import BaseModel

class UserIDResponse(BaseModel):
    user_id: str
