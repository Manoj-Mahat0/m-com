import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://manojmahato08779:Jl5Zz6nzIg0A0rXK@cluster0.lo2gm3g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "ecommerce_db"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

async def insert_admin_user():
    result = await db["users"].update_one(
        {"phone_number": "9876543210"},
        {
            "$set": {
                "otp": "123456",
                "is_verified": False,
                "is_profile_complete": False,
                "role": "ADMIN"
            }
        },
        upsert=True
    )
    print("✅ Admin user inserted or updated.")

if __name__ == "__main__":
    asyncio.run(insert_admin_user())
