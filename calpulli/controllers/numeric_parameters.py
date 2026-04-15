from fastapi import APIRouter as Router,Depends,HTTPException
import calpulli.middleware as MX
import calpulli.services as S
import calpulli.dtos as DTO
router = Router(prefix="/numeric-parameters")

@router.post("")
async def create_numeric_parameter(dto: DTO.NumericParameterCreateFormDTO, service: S.NumericParametersService = Depends(MX.get_numeric_parameters_service)):
    result = await service.create_numeric_parameter(dto=dto)
    if result.is_ok:
        return result.unwrap()
    else:
        err = result.unwrap_err()
        if isinstance(err, ValueError):
            raise HTTPException(status_code=422, detail=str(err))
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))

@router.get("/{parameter_id}", response_model=DTO.NumericParameterDTO)
async def get_numeric_parameter(parameter_id: int, service: S.NumericParametersService = Depends(MX.get_numeric_parameters_service)):
    result = await service.get_numeric_parameter_by_id(parameter_id=parameter_id)
    if result.is_ok:
        return result.unwrap()
    else:
        raise HTTPException(status_code=404, detail=str(result.unwrap_err()))

@router.put("/{parameter_id}")
async def update_numeric_parameter(parameter_id: int, dto: DTO.NumericParameterCreateFormDTO, service:S.NumericParametersService = Depends(MX.get_numeric_parameters_service)):
    result = await service.update_numeric_parameter(parameter_id=parameter_id, dto=dto)
    if result.is_ok:
        return result.unwrap()
    else:        
        raise HTTPException(status_code=404, detail=str(result.unwrap_err() ) )

@router.delete("/{parameter_id}")
async def delete_numeric_parameter(parameter_id: int, service:S.NumericParametersService = Depends(MX.get_numeric_parameters_service)):
    result = await service.delete_numeric_parameter_by_id(parameter_id=parameter_id)
    if result.is_ok:
        return {"message": "Numeric parameter deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail=str(result.unwrap_err() ) )