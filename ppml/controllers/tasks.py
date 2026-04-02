from fastapi import APIRouter as Router,Depends
from fastapi import status
import ppml.middleware as MX
import ppml.models as M
import ppml.dtos as DTO
router = Router(prefix="/tasks")

@router.post("")
async def create_task(
    current_user: DTO.UserProfileDTO = Depends(MX.get_current_user)
):
    pass
    


@router.get("")
async def get_tasks():
    pass

@router.get("/{task_id}")
async def get_task_by_id(task_id: int):
    pass