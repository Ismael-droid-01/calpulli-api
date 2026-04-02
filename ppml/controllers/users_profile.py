from fastapi import APIRouter as Router,Depends,HTTPException
import ppml.middleware as MX
import ppml.services as S
import ppml.dtos as DTO
router = Router(prefix="/users")


@router.post("")
async def create_user(
    dto:DTO.UserCreateFormDTO,
    service:S.UserProfilesService = Depends(MX.get_users_service), 
):
    result = await service.create_user(dto)
    if result.is_ok:
        return result.unwrap()
    else:
        raise HTTPException(status_code=500, detail=str(result.unwrap_err() ) )

@router.post("/login")
async def login(dto:DTO.UserLoginFormDTO, service:S.UserProfilesService = Depends(MX.get_users_service)):
    result = await service.login(dto)
    if result.is_ok:
        return result.unwrap()
    else:        
        raise HTTPException(status_code=500, detail=str(result.unwrap_err() ) )

@router.get("/me")
async def get_current_user(
    current_user: DTO.UserProfileDTO = Depends(MX.get_current_user)
):
    return current_user

