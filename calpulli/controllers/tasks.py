from fastapi import APIRouter as Router, Depends, HTTPException
from calpulli.core.worker.consumer import TaskConsumer
import calpulli.middleware as MX
import calpulli.services as S
import calpulli.dtos as DTO
import asyncio
from calpulli.errors import CalpulliError
from calpulli.log import Log
from calpulli.core.worker.events import TaskCreatedEvent
import calpulli.config as Cfg

L = Log(
    name= __name__,
    path= Cfg.CALPULLI_LOG_PATH
)
# from roryclient.client import RoryClient

router = Router(prefix="/tasks")

@router.post("", response_model=DTO.TaskCreatedResponseDTO)
async def create_task(
    dto:          DTO.TaskCreateFormDTO,
    current_user: DTO.UserProfileDTO  = Depends(MX.get_current_user),
    service:      S.TasksService      = Depends(MX.get_tasks_service),
    # rory_client: RoryClient          = Depends(MX.get_rory_client)

):
    result = await service.create_task(
        user_id = current_user.user_profile_id,
        dto     = dto,
        # rory_client = rory_client

    )
    if result.is_ok:
        return result.unwrap()
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))

@router.post("/run")
async def run_task(
    dto: DTO.TaskCreateAggregateDTO, 
    current_user:DTO.UserProfileDTO = Depends(MX.get_current_user), # Extrae usuario de Xolo
    service: S.TasksService = Depends(MX.get_tasks_service),
    task_consumer: TaskConsumer = Depends(MX.get_task_consumer)
):
    # Aseguramos que la tarea le pertenezca al usuario del token
    dto.user_id = current_user.user_profile_id
    result      = await service.create_task_aggregate(dto)
    
    if result.is_err:
        raise CalpulliError(status_code=500, detail=str(result.unwrap_err())).to_http_exception()
    task_data = result.unwrap()
    
    # Empujar a la cola en background
    try:
        event = TaskCreatedEvent(task_id=task_data.task_id)
        task_consumer.queue.put_nowait(event)
        L.info(f"Task {task_data.task_id} enqueued for processing.")
    except asyncio.QueueFull:
        # Manejo opcional si la cola estalla
        L.error(f"Failed to enqueue task {task_data.task_id} for processing.")
        
    return task_data
    # else:


@router.get("/my-tasks", response_model=list[DTO.TaskDTO])
async def get_my_tasks(
    current_user: DTO.UserProfileDTO = Depends(MX.get_current_user),
    service:      S.TasksService     = Depends(MX.get_tasks_service),
):
    result = await service.get_tasks_by_user(user_id=current_user.user_profile_id)
    if result.is_ok:
        return result.unwrap()
    else:
        raise HTTPException(status_code=404, detail=str(result.unwrap_err()))


@router.get("/{task_id}", response_model=DTO.TaskDTO)
async def get_task(
    task_id:      int,
    current_user: DTO.UserProfileDTO = Depends(MX.get_current_user),
    service:      S.TasksService     = Depends(MX.get_tasks_service),
):
    result = await service.get_task_by_id(task_id=task_id)
    if result.is_ok:
        task = result.unwrap()
        if task.user_id != current_user.user_profile_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this task.")
        return task
    else:
        raise HTTPException(status_code=404, detail=str(result.unwrap_err()))

@router.get("/{task_id}/results", response_model=list[DTO.ResultDTO])
async def get_results_for_task(
    task_id:      int,
    current_user: DTO.UserProfileDTO = Depends(MX.get_current_user),
    service:      S.ResultsService     = Depends(MX.get_results_service),
):
    result = await service.get_results_by_task_id(task_id=task_id)
    if result.is_ok:
        return result.unwrap()
    else:
        raise HTTPException(status_code=404, detail=str(result.unwrap_err()))
