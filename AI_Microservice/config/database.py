# config/database.py
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise RuntimeError("MONGO_URL not set in environment")

mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client["skillswap"]

# Export names: mongo_client and db
