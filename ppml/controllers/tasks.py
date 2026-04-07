from fastapi import APIRouter as Router, Depends, HTTPException
import ppml.middleware as MX
import ppml.services as S
import ppml.dtos as DTO

router = Router(prefix="/tasks")

@router.post("", response_model=DTO.TaskCreatedResponseDTO)
async def create_task(
    dto:          DTO.TaskCreateFormDTO,
    current_user: DTO.UserProfileDTO  = Depends(MX.get_current_user),
    service:      S.TasksService      = Depends(MX.get_tasks_service),
):
    result = await service.create_task(user_id=current_user.user_id, dto=dto)
    if result.is_ok:
        return result.unwrap()
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))


@router.get("/my-tasks", response_model=list[DTO.TaskDTO])
async def get_my_tasks(
    current_user: DTO.UserProfileDTO = Depends(MX.get_current_user),
    service:      S.TasksService     = Depends(MX.get_tasks_service),
):
    result = await service.get_tasks_by_user(user_id=current_user.user_id)
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
        if task.user_id != current_user.user_id:
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
