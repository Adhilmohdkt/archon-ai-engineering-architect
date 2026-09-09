from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.API import schemas
from app.API.services.archon_service import ArchonService

service = ArchonService()

router = APIRouter(
    prefix="/api/v1/archon",
    tags=["Archon"]
)


@router.post("", response_model=schemas.ArchonResponse)
async def start_archon(
    request: schemas.ArchonRequest,
    background_tasks: BackgroundTasks
):

    result = await service.start(request.user_goal)

    background_tasks.add_task(
        service.run,
        result.thread_id,
        request.user_goal
    )

    return result


@router.post(
    "/{thread_id}/resume",
    response_model=schemas.ArchonResponse
)
async def resume_archon(
    thread_id: str,
    request: schemas.HumanResumeRequest
):

    result = await service.resume(
        thread_id=thread_id,
        decision=request.decision,
        feedback=request.feedback
    )

    return result


@router.get(
    "/{thread_id}",
    response_model=schemas.ArchonResponse
)
async def get_archon_run(thread_id: str):

    result = await service.get_run(thread_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Archon run not found"
        )

    return result