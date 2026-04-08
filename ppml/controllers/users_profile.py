from fastapi import APIRouter as Router,Depends,HTTPException
import ppml.middleware as MX
import ppml.services as S
from ppml.helpers import PPMLError
import ppml.dtos as DTO
router = Router(prefix="/users")


@router.post("")
async def create_user(
    dto:DTO.UserCreateFormDTO,
    service:S.UserProfilesService = Depends(MX.get_users_service), 
):
    try:
        result = await service.create_user(dto)
        if result.is_ok:
            return result.unwrap()
        else:
            raise PPMLError(status_code=500, detail=str(result.unwrap_err())).to_http_exception()
    except Exception as e:
        raise PPMLError.from_exception(e).to_http_exception()

@router.post("/login")
async def login(dto:DTO.UserLoginFormDTO, service:S.UserProfilesService = Depends(MX.get_users_service)):
    try:
        result = await service.login(dto)
        if result.is_ok:
            return result.unwrap()
        else:        
            raise PPMLError(status_code=500, detail=str(result.unwrap_err())).to_http_exception()
    except Exception as e:
        raise PPMLError.from_exception(e).to_http_exception()

@router.get("/me")
async def get_current_user(
    current_user: DTO.UserProfileDTO = Depends(MX.get_current_user)
):
    return current_user

