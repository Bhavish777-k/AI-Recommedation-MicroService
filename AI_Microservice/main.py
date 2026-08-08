# main.py
from fastapi import FastAPI
from controllers.roadmap_controller import router as roadmap_router
from config.database import mongo_client
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()
app.include_router(roadmap_router, prefix="/api")

@app.on_event("startup")
async def startup_db_client():
    try:
        # ping to ensure connection
        await mongo_client.admin.command("ping")
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)

@app.get("/")
def ping():
    return {"status": "Server Started Successfully"}

@app.on_event("shutdown")
async def shutdown_db_client():
    try:
        mongo_client.close()
        print("MongoDB connection closed")
    except Exception:
        pass
