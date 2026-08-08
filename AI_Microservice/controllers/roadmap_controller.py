# controllers/roadmap_controller.py
from fastapi import APIRouter, HTTPException,Depends
from pydantic import BaseModel
from services.roadmap_service import generate_roadmap_for_user
from config.auth import validate_api_key

router = APIRouter()

class RoadmapRequest(BaseModel):
    user_id: str
    target_role: str
    model: str = "gemini-flash-latest"

@router.post("/roadmap", dependencies=[Depends(validate_api_key)])
async def roadmap(req: RoadmapRequest):
    result = await generate_roadmap_for_user(req.user_id, req.target_role, model=req.model)
    if result.get("error"):
        raise HTTPException(status_code=404, detail=result["error"])
    return result
