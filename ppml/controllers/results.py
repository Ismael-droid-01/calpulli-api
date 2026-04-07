from fastapi import APIRouter as Router,Depends,HTTPException
import ppml.middleware as MX
import ppml.services as S
import ppml.dtos as DTO
router = Router(prefix="/results")

@router.post("")
async def create_result(dto: DTO.ResultCreateFormDTO, service: S.ResultsService = Depends(MX.get_results_service)):
    result = await service.create_result(task_id=dto.task_id, dto=dto)
    if result.is_ok:
        return result.unwrap()
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))
    