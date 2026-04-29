from fastapi import APIRouter as Router,Depends,HTTPException
import calpulli.middleware as MX
import calpulli.services as S
import calpulli.dtos as DTO
router = Router(prefix="/results")

@router.get("/{result_id}", response_model=DTO.ResultDTO)
async def get_result(
    result_id: int, 
    current_user:DTO.UserProfileDTO = Depends(MX.get_current_user),
    service:S.ResultsService = Depends(MX.get_results_service)
    ):
    result = await service.get_result_by_id(
        result_id=result_id,
        user_profile_id=current_user.user_profile_id
    )
    if result.is_ok:
        return result.unwrap()
    
    raise HTTPException(status_code=404, detail=str(result.unwrap_err()))

@router.delete("/{result_id}")
async def delete_result(
    result_id: int, 
    current_user:DTO.UserProfileDTO = Depends(MX.get_current_user),
    service:S.ResultsService = Depends(MX.get_results_service)
    ):
    result = await service.delete_result_by_id(
        result_id=result_id,
        user_profile_id=current_user.user_profile_id
    )
    if result.is_ok:
        return {"message": "Result deleted successfully."}
    
    raise HTTPException(status_code=404, detail=str(result.unwrap_err()))