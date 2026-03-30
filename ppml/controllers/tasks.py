from fastapi import APIRouter as Router,Depends
from fastapi import status

router = Router(prefix="/tasks")
@router.post("")
async def create_task():
    pass

@router.get("")
async def get_tasks():
    pass

@router.get("/{task_id}")
async def get_task_by_id(task_id: int):
    pass