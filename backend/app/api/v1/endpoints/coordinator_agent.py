from fastapi import APIRouter, HTTPException
from app.services.coordinator_router import route_request
from app.models.coordinator import CoordinatorRequest
from pydantic import BaseModel

router = APIRouter()


@router.post("/coordinator")
async def coordinate_task(request: CoordinatorRequest):
    try:
        result = await route_request(request.task_type, request.payload)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
