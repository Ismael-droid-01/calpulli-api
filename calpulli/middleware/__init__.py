import calpulli.services as S
from xolo.client import XoloClient
from typing import Annotated, Optional
from fastapi import Depends,Header,HTTPException,Request
from calpulli.repositories import AlgorithmsRepository, NumericParametersRepository, UsersProfilesRepository,StringParametersRepository
from fastapi.security import OAuth2PasswordBearer
import calpulli.config as Cfg
import calpulli.dtos as DTO
from calpulli.log import Log
from roryclient.client import RoryClient
from calpulli.core.worker.consumer import TaskConsumer

L = Log(
    name = __name__,
    path = Cfg.CALPULLI_LOG_PATH,
)


def get_rory_client()->RoryClient:
    return RoryClient(
        hostname = Cfg.RORY_HOSTNAME,
        port     = Cfg.RORY_PORT,
        timeout  = Cfg.RORY_TIMEOUT
    )

def get_xolo_client()->XoloClient:
    return XoloClient(
        api_url= Cfg.XOLO_API_URL,
        secret= Cfg.XOLO_SECRET_KEY
    )


def get_users_service(xolo_client:S.XoloClient = Depends(get_xolo_client))->S.UserProfilesService:
    repository = UsersProfilesRepository()
    return S.UserProfilesService(repository=repository, xolo=xolo_client)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

async def __get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    temporal_secret_key: Annotated[Optional[str], Header(alias="Temporal-Secret-Key")] = None,
    users_profiles_service: S.UserProfilesService = Depends(get_users_service),
    xolo_client: XoloClient = Depends(get_xolo_client)
):

    try:
        user_result =  xolo_client.get_current_user(
            token = token, 
            temporal_secret = temporal_secret_key
        )
        if user_result.is_err:
            e = user_result.unwrap_err() 
            L.error({
                "msg": f"Error getting user from Xolo: {e.detail.msg}",
                "code": e.code,
                "raw_error": e.detail.raw_error
            })
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user_dto            = user_result.unwrap()
        user_profile_result = await users_profiles_service.get_by_username(username = user_dto.username)
        # print("User profile result:", user_profile_result)
        if user_profile_result.is_err:
            e = user_profile_result.unwrap_err()
            L.error({
                "msg": f"Error getting user profile: {e}",
            })
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user_profile    = user_profile_result.unwrap()
        create_at = user_profile.created_at.isoformat() if user_profile.created_at else None
        updated_at = user_profile.updated_at.isoformat() if user_profile.updated_at else None
        user_profile_dto = DTO.UserProfileDTO(
            user_profile_id = user_profile.id,
            user_id    = user_profile.user_id,
            username   = user_profile.username,
            email      = user_profile.email,
            first_name = user_profile.first_name,
            last_name  = user_profile.last_name,
            is_disabled= user_profile.is_disabled,
            created_at = create_at,
            updated_at = updated_at,
        )
        return user_profile_dto
        # user_profile = 

    except Exception as e:
        L.error(f"Error in __get_current_user: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

async def get_current_user(
    current_user: Annotated[DTO.UserProfileDTO, Depends(__get_current_user)]
):
    if current_user.is_disabled:
        raise HTTPException(
            status_code=403,
            detail=f"User {current_user.user_id} is disabled."
        )
    return current_user

def get_algorithms_service() -> S.AlgorithmsService:
    return S.AlgorithmsService(repository=AlgorithmsRepository())

def get_numeric_parameters_service() -> S.NumericParametersService:
    return S.NumericParametersService(repository=NumericParametersRepository())

def get_string_parameters_service() -> S.StringParametersService:
    return S.StringParametersService(repository=StringParametersRepository())

def get_results_service() -> S.ResultsService:  
    return S.ResultsService(repository=S.ResultsRepository())

def get_tasks_service(
        result_service: S.ResultsService = Depends(get_results_service)
) -> S.TasksService:
    return S.TasksService(
        repository=S.TasksRepository(),
        result_service=result_service
    )



def get_task_consumer(request:Request) -> TaskConsumer:
    return request.app.state.task_consumer