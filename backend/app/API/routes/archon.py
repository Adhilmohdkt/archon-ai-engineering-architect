from fastapi  import APIRouter
from app.API import schemas
from app.API.services import archon_service
import asyncio
service = archon_service()

router = APIRouter(prefix="/api/v1/archon",tags=['Archon'])

@router.post("", response_model=schemas.ArchonResponse)
async def start_archon(request: schemas.ArchonRequest):

    result = await service.start(request.user_goal)

    return {
        "thread_id": result["thread_id"],
        "status": result["status"],
        "user_goal": request.user_goal,
    }