from fastapi import APIRouter as Router,Depends,HTTPException
import calpulli.middleware as MX
import calpulli.services as S
import calpulli.dtos as DTO
router = Router(prefix="/algorithms")

@router.post("")
async def create_algorithm(dto: DTO.AlgorithmCreateFormDTO, service: S.AlgorithmsService = Depends(MX.get_algorithms_service)):
    result = await service.create_algorithm(dto=dto)
    if result.is_ok:
        return result.unwrap()
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))

@router.get("/list", response_model=list[DTO.AlgorithmDTO])
async def get_all_algorithms(service:S.AlgorithmsService = Depends(MX.get_algorithms_service)):
    result = await service.get_algorithms()
    if result.is_ok:
        return result.unwrap()
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err()))

@router.get("/type/{type}", response_model=list[DTO.AlgorithmDTO])
async def get_algorithms_by_type(type: str, service:S.AlgorithmsService = Depends(MX.get_algorithms_service)):
    result = await service.get_algorithms_by_type(type=type)
    if result.is_ok:
        return result.unwrap()
    else:
        raise HTTPException(status_code=404, detail=str(result.unwrap_err()))

@router.get("/{algorithm_id}", response_model=DTO.AlgorithmDTO)
async def get_algorithm(algorithm_id: int, service:S.AlgorithmsService = Depends(MX.get_algorithms_service)):
    result = await service.get_algorithm_by_id(algorithm_id=algorithm_id)
    if result.is_ok:
        return result.unwrap()
    else:
        raise HTTPException(status_code=404, detail=str(result.unwrap_err()))

@router.get("/{algorithm_id}/parameters", response_model=DTO.AlgorithmParametersDTO)
async def get_algorithm_parameters(algorithm_id: int, service: S.AlgorithmsService = Depends(MX.get_algorithms_service)):
    result = await service.get_algorithm_parameters(algorithm_id=algorithm_id)
    if result.is_ok:
        return result.unwrap()
    else:
        raise HTTPException(status_code=404, detail=str(result.unwrap_err()))

@router.put("/{algorithm_id}")
async def update_algorithm(algorithm_id: int, dto: DTO.AlgorithmCreateFormDTO, service:S.AlgorithmsService = Depends(MX.get_algorithms_service)):
    result = await service.update_algorithm(algorithm_id=algorithm_id, dto=dto)
    if result.is_ok:
        return result.unwrap()
    else:        
        raise HTTPException(status_code=404, detail=str(result.unwrap_err()))

@router.delete("/{algorithm_id}")
async def delete_algorithm(algorithm_id: int, service:S.AlgorithmsService = Depends(MX.get_algorithms_service)):
    result = await service.delete_algorithm_by_id(algorithm_id=algorithm_id)
    if result.is_ok:
        return {"message": "Algorithm deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail=str(result.unwrap_err()))