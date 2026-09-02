from fastapi  import APIRouter
from app.API import schemas
from app.API.services.archon_service import ArchonService
import asyncio
service = ArchonService()

router = APIRouter(prefix="/api/v1/archon",tags=['Archon'])

@router.post("", response_model=schemas.ArchonResponse)
async def start_archon(request: schemas.ArchonRequest):

    result = await service.start(request.user_goal)

    return result


@router.post( "/{thread_id}/resume",response_model=schemas.ArchonResponse)
async def resume_archon(thread_id: str ,request : schemas.HumanResumeRequest):

    result = await service.resume(thread_id= thread_id,decision=request.decision,
                                  feedback=request.feedback)
    return result