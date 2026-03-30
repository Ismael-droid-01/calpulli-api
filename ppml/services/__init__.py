
from ppml.models import UserProfile
from option import Err,Ok,Result
import ppml.dtos as DTO
from xolo.client import XoloClient
from ppml.log import Log
from ppml.repositories import UsersProfilesRepository
import os
L = Log(
    name=__name__,
    path=os.environ.get("PPML_LOG_PATH","./logs/"),
)
class UsersService:
    def __init__(self,repository: UsersProfilesRepository, xolo:XoloClient):
        self.repository = repository
        self.xolo = xolo
    async def create_user(self,dto:DTO.UserCreateFormDTO)->Result[DTO.UserCreatedResponseDTO,Exception]:
        try:
            result = self.xolo.signup(
                username   = dto.username,
                email      = dto.email,
                password   = dto.password,
                first_name = dto.first_name,
                last_name  = dto.last_name,
                scope      = "ppml",
                expiration = "1y",
            )
            if result.is_err:
                L.error(f"Error creating user: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            
            xolo_response = result.unwrap()
            user_id       = xolo_response.key

            user_result = await self.repository.create(
                user_id    = user_id,
                username   = dto.username,
                email      = dto.email,
                first_name = dto.first_name,
                last_name  = dto.last_name,
            )
            if user_result.is_err:
                L.error(f"Error saving user to repository: {user_result.unwrap_err()}")
                return Err(user_result.unwrap_err())
            
            user = user_result.unwrap()
            return Ok(DTO.UserCreatedResponseDTO(
                user_id  = user.user_id,
                username = user.username,
                email    = user.email
            ))
        except Exception as e:
            L.error(f"Exception occurred while creating user: {e}")
            return Err(e)
    async def login(self,dto:DTO.UserLoginFormDTO)->Result[DTO.UserLoggedInResponseDTO,Exception]:
        try:
            result = self.xolo.auth(
                username    = dto.username,
                password    = dto.password,
                scope       = "ppml",
                expiration  = "1h",
                renew_token = True
            )
            if result.is_err:
                L.error(f"Error logging in: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            xolo_response = result.unwrap()
            return Ok(DTO.UserLoggedInResponseDTO(
                access_token = xolo_response.access_token,
                email=xolo_response.email,
                username=xolo_response.username,
                first_name=xolo_response.first_name,
                last_name=xolo_response.last_name,
                temporal_secret=xolo_response.temporal_secret,
                user_id=xolo_response.user_id,
            ))
        except Exception as e:
            L.error(f"Exception occurred while logging in: {e}")
            return Err(e)
    def get_users(self):
        pass
    def get_user_by_id(self):
        pass