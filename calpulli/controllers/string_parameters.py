from fastapi import APIRouter as Router,Depends,HTTPException
import calpulli.middleware as MX
import calpulli.services as S
import calpulli.dtos as DTO
router = Router(prefix="/string-parameters")

@router.post("")
async def create_string_parameter(dto: DTO.StringParameterCreateFormDTO, service: S.StringParametersService = Depends(MX.get_string_parameters_service)):
    result = await service.create_string_parameter(dto=dto)
    if result.is_ok:
        return result.unwrap()
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))

@router.get("/{parameter_id}", response_model=DTO.StringParameterDTO)
async def get_string_parameter(parameter_id: int, service: S.StringParametersService = Depends(MX.get_string_parameters_service)):
    result = await service.get_string_parameter_by_id(parameter_id=parameter_id)
    if result.is_ok:
        return result.unwrap()
    else:
        raise HTTPException(status_code=404, detail=str(result.unwrap_err()))

@router.put("/{parameter_id}")
async def update_string_parameter(parameter_id: int, dto: DTO.StringParameterCreateFormDTO, service:S.StringParametersService = Depends(MX.get_string_parameters_service)):
    result = await service.update_string_parameter(parameter_id=parameter_id, dto=dto)
    if result.is_ok:
        return result.unwrap()
    else:        
        raise HTTPException(status_code=404, detail=str(result.unwrap_err() ) )

@router.delete("/{parameter_id}")
async def delete_string_parameter(parameter_id: int, service:S.StringParametersService = Depends(MX.get_string_parameters_service)):
    result = await service.delete_string_parameter_by_id(parameter_id=parameter_id)
    if result.is_ok:
        return {"message": "String parameter deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail=str(result.unwrap_err() ) )