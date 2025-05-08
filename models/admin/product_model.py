from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class Product(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str
    description: str
    price: float
    category: str
    feature_image: Optional[str] = None
    product_images: Optional[List[str]] = []

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
