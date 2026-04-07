
from ppml.models import UserProfile
from option import Err,Ok,Result
import ppml.dtos as DTO
from xolo.client import XoloClient
from ppml.log import Log
from ppml.repositories import TasksRepository, UsersProfilesRepository, AlgorithmsRepository, NumericParametersRepository, StringParametersRepository
import os

L = Log(
    name=__name__,
    path=os.environ.get("PPML_LOG_PATH","./logs/"),
)

class UserProfilesService:

    def __init__(self,repository: UsersProfilesRepository, xolo:XoloClient):
        self.repository = repository
        self.xolo = xolo
    
    async def get_by_username(self, username:str)->Result[UserProfile,Exception]:
        try:
            result = await self.repository.get_by_username(username=username)
            if result.is_err:
                L.error(f"Error getting user profile by username: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            user_profile = result.unwrap()
            return Ok(user_profile)
        except Exception as e:
            L.error(f"Exception occurred while getting user profile by username: {e}")
            return Err(e)
        
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

class AlgorithmsService:

    def __init__(self, repository: AlgorithmsRepository):
        self.repository = repository
    
    async def create_algorithm(self, dto:DTO.AlgorithmCreateFormDTO)->Result[DTO.AlgorithmCreatedResponseDTO,Exception]:
        try:
            result = await self.repository.create(
                name=dto.name,
                type=dto.type
            )
            if result.is_err:
                L.error(f"Error creating algorithm: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            algorithm = result.unwrap()
            return Ok(DTO.AlgorithmCreatedResponseDTO(
                algorithm_id    =   algorithm.algorithm_id,
                name            =   algorithm.name,
                type            =   algorithm.type
            ))
        except Exception as e:
            L.error(f"Exception occurred while creating algorithm: {e}")
            return Err(e)
    
    async def get_algorithms(self)->Result[list[DTO.AlgorithmDTO],Exception]:
        try:
            result = await self.repository.get_all()
            if result.is_err:
                L.error(f"Error getting algorithms: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            algorithms = result.unwrap()
            return Ok([
                DTO.AlgorithmDTO(
                    algorithm_id    =   alg.algorithm_id,
                    name            =   alg.name,
                    type            =   alg.type,
                    created_at      =   alg.created_at.isoformat(),
                    updated_at      =   alg.updated_at.isoformat(),
                ) for alg in algorithms
            ])
        except Exception as e:
            L.error(f"Exception occurred while getting algorithms: {e}")
            return Err(e)

    async def get_algorithm_by_id(self, algorithm_id:int)->Result[DTO.AlgorithmDTO,Exception]:
        try:
            result = await self.repository.get_by_id(algorithm_id=algorithm_id)
            if result.is_err:
                L.error(f"Error getting algorithm by id: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            algorithm = result.unwrap()
            return Ok(DTO.AlgorithmDTO(
                algorithm_id    =   algorithm.algorithm_id,
                name            =   algorithm.name,
                type            =   algorithm.type,
                created_at      =   algorithm.created_at.isoformat(),
                updated_at      =   algorithm.updated_at.isoformat(),
            ))
        except Exception as e:
            L.error(f"Exception occurred while getting algorithm by id: {e}")
            return Err(e)
        
    async def get_algorithms_by_type(self, type:str)->Result[list[DTO.AlgorithmDTO],Exception]:
        try:
            result = await self.repository.get_by_type(type=type)
            if result.is_err:
                L.error(f"Error getting algorithms by type: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            algorithms = result.unwrap()
            return Ok([
                DTO.AlgorithmDTO(
                    algorithm_id    =   alg.algorithm_id,
                    name            =   alg.name,
                    type            =   alg.type,
                    created_at      =   alg.created_at.isoformat(),
                    updated_at      =   alg.updated_at.isoformat(),
                ) for alg in algorithms
            ])
        except Exception as e:
            L.error(f"Exception occurred while getting algorithms by type: {e}")
            return Err(e)
    
    async def update_algorithm(self, algorithm_id:int, dto:DTO.AlgorithmCreateFormDTO)->Result[DTO.AlgorithmDTO,Exception]:
        try:
            result = await self.repository.update(
                algorithm_id=algorithm_id,
                name=dto.name,
                type=dto.type
            )
            if result.is_err:
                L.error(f"Error updating algorithm: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            algorithm = result.unwrap()
            return Ok(DTO.AlgorithmDTO(
                algorithm_id    =   algorithm.algorithm_id,
                name            =   algorithm.name,
                type            =   algorithm.type,
                created_at      =   algorithm.created_at.isoformat(),
                updated_at      =   algorithm.updated_at.isoformat(),
            ))
        except Exception as e:
            L.error(f"Exception occurred while updating algorithm: {e}")
            return Err(e)

    async def delete_algorithm_by_id(self, algorithm_id:int)->Result[bool,Exception]:
        try:
            result = await self.repository.delete_by_id(algorithm_id=algorithm_id)
            if result.is_err:
                L.error(f"Error deleting algorithm by id: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            return Ok(result.unwrap())
        except Exception as e:
            L.error(f"Exception occurred while deleting algorithm by id: {e}")
            return Err(e)
    
    async def get_algorithm_parameters(self, algorithm_id: int) -> Result[DTO.AlgorithmParametersDTO, Exception]:
        try:
            result = await self.repository.get_parameters_by_algorithm_id(algorithm_id=algorithm_id)
            if result.is_err:
                L.error(f"Error getting algorithm parameters: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            data = result.unwrap()
            return Ok(DTO.AlgorithmParametersDTO(
                algorithm_id        = data["algorithm_id"],
                numeric_parameters  = [
                    DTO.NumericParameterDTO(
                        parameter_id    = param.parameter_id,
                        algorithm_id    = param.algorithm_id,
                        name            = param.name,
                        type            = param.type,
                        default_value   = param.default_value,
                        max_value       = param.max_value,
                        created_at      = param.created_at.isoformat(),
                        updated_at      = param.updated_at.isoformat()
                    ) for param in data["numeric_parameters"]
                ],
                string_parameters   = [
                    DTO.StringParameterDTO(
                        parameter_id    = param.parameter_id,
                        algorithm_id    = param.algorithm_id,
                        name            = param.name,
                        default_value   = param.default_value,
                        created_at      = param.created_at.isoformat(),
                        updated_at      = param.updated_at.isoformat()
                    ) for param in data["string_parameters"]
                ]
            ))
        except Exception as e:
            L.error(f"Exception occurred while getting algorithm parameters: {e}")
            return Err(e)

class NumericParametersService:
    
    def __init__(self, repository: NumericParametersRepository):
        self.repository = repository

    async def create_numeric_parameter(self, dto: DTO.NumericParameterCreateFormDTO)->Result[DTO.NumericParameterCreatedResponseDTO,Exception]:
        try:
            result = await self.repository.create(
                algorithm_id    = dto.algorithm_id,
                name            = dto.name,
                type            = dto.type,
                default_value   = dto.default_value,
                max_value       = dto.max_value
            )
            if result.is_err:
                L.error(f"Error creating numeric parameter: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            parameter = result.unwrap()
            return Ok(DTO.NumericParameterCreatedResponseDTO(
                parameter_id    = parameter.parameter_id,
                algorithm_id    = parameter.algorithm_id,
                name            = parameter.name,
                type            = parameter.type,
                default_value   = parameter.default_value,
                max_value       = parameter.max_value
            ))
        except Exception as e:
            L.error(f"Exception occurred while creating numeric parameter: {e}")
            return Err(e)
    
    async def get_numeric_parameters_by_algorithm_id(self, algorithm_id:int)->Result[list[DTO.NumericParameterDTO],Exception]:
        try:
            result = await self.repository.get_by_algorithm_id(algorithm_id=algorithm_id)
            if result.is_err:
                L.error(f"Error getting numeric parameters by algorithm id: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            parameters = result.unwrap()
            return Ok([
                DTO.NumericParameterDTO(
                    parameter_id    = param.parameter_id,
                    algorithm_id    = param.algorithm_id,
                    name            = param.name,
                    type            = param.type,
                    default_value   = param.default_value,
                    max_value       = param.max_value,
                    created_at      = param.created_at.isoformat(),
                    updated_at      = param.updated_at.isoformat()
                ) for param in parameters
            ])
        except Exception as e:
            L.error(f"Exception occurred while getting numeric parameters by algorithm id: {e}")
            return Err(e)
    
    async def get_numeric_parameter_by_id(self, parameter_id:int)->Result[DTO.NumericParameterDTO,Exception]:
        try:
            result = await self.repository.get_by_id(parameter_id=parameter_id)
            if result.is_err:
                L.error(f"Error getting numeric parameter by id: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            param = result.unwrap()
            return Ok(DTO.NumericParameterDTO(
                parameter_id    = param.parameter_id,
                algorithm_id    = param.algorithm_id,
                name            = param.name,
                type            = param.type,
                default_value   = param.default_value,
                max_value       = param.max_value,
                created_at      = param.created_at.isoformat(),
                updated_at      = param.updated_at.isoformat()
            ))
        except Exception as e:
            L.error(f"Exception occurred while getting numeric parameter by id: {e}")
            return Err(e)
    
    async def update_numeric_parameter(self, parameter_id:int, dto: DTO.NumericParameterCreateFormDTO)->Result[DTO.NumericParameterDTO,Exception]:
        try:
            result = await self.repository.update(
                parameter_id    = parameter_id,
                name            = dto.name,
                type            = dto.type,
                default_value   = dto.default_value,
                max_value       = dto.max_value
            )
            if result.is_err:
                L.error(f"Error updating numeric parameter: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            param = result.unwrap()
            return Ok(DTO.NumericParameterDTO(
                parameter_id    = param.parameter_id,
                algorithm_id    = param.algorithm_id,
                name            = param.name,
                type            = param.type,
                default_value   = param.default_value,
                max_value       = param.max_value,
                created_at      = param.created_at.isoformat(),
                updated_at      = param.updated_at.isoformat()
            ))
        except Exception as e:
            L.error(f"Exception occurred while updating numeric parameter: {e}")
            return Err(e)
    
    async def delete_numeric_parameter_by_id(self, parameter_id:int)->Result[bool,Exception]:
        try:
            result = await self.repository.delete_by_id(parameter_id=parameter_id)
            if result.is_err:
                L.error(f"Error deleting numeric parameter by id: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            return Ok(result.unwrap())
        except Exception as e:
            L.error(f"Exception occurred while deleting numeric parameter by id: {e}")
            return Err(e)

class StringParametersService:
    
    def __init__(self, repository: StringParametersRepository):
        self.repository = repository
    
    async def create_string_parameter(self, dto: DTO.StringParameterCreateFormDTO)->Result[DTO.StringParameterCreatedResponseDTO,Exception]:
        try:
            result = await self.repository.create(
                algorithm_id    = dto.algorithm_id,
                name            = dto.name,
                default_value   = dto.default_value
            )
            if result.is_err:
                L.error(f"Error creating string parameter: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            parameter = result.unwrap()
            return Ok(DTO.StringParameterCreatedResponseDTO(
                parameter_id    = parameter.parameter_id,
                algorithm_id    = parameter.algorithm_id,
                name            = parameter.name,
                default_value   = parameter.default_value
            ))
        except Exception as e:
            L.error(f"Exception occurred while creating string parameter: {e}")
            return Err(e)
    
    async def get_string_parameters_by_algorithm_id(self, algorithm_id:int)->Result[list[DTO.StringParameterDTO],Exception]:
        try:
            result = await self.repository.get_by_algorithm_id(algorithm_id=algorithm_id)
            if result.is_err:
                L.error(f"Error getting string parameters by algorithm id: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            parameters = result.unwrap()
            return Ok([
                DTO.StringParameterDTO(
                    parameter_id    = param.parameter_id,
                    algorithm_id    = param.algorithm_id,
                    name            = param.name,
                    default_value   = param.default_value,
                    created_at      = param.created_at.isoformat(),
                    updated_at      = param.updated_at.isoformat()
                ) for param in parameters
            ])
        except Exception as e:
            L.error(f"Exception occurred while getting string parameters by algorithm id: {e}")
            return Err(e)
    
    async def get_string_parameter_by_id(self, parameter_id:int)->Result[DTO.StringParameterDTO,Exception]:
        try:
            result = await self.repository.get_by_id(parameter_id=parameter_id)
            if result.is_err:
                L.error(f"Error getting string parameter by id: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            param = result.unwrap()
            return Ok(DTO.StringParameterDTO(
                parameter_id    = param.parameter_id,
                algorithm_id    = param.algorithm_id,
                name            = param.name,
                default_value   = param.default_value,
                created_at      = param.created_at.isoformat(),
                updated_at      = param.updated_at.isoformat()
            ))
        except Exception as e:
            L.error(f"Exception occurred while getting string parameter by id: {e}")
            return Err(e)

    async def update_string_parameter(self, parameter_id:int, dto: DTO.StringParameterCreateFormDTO)->Result[DTO.StringParameterDTO,Exception]:
        try:
            result = await self.repository.update(
                parameter_id    = parameter_id,
                name            = dto.name,
                default_value   = dto.default_value
            )
            if result.is_err:
                L.error(f"Error updating string parameter: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            param = result.unwrap()
            return Ok(DTO.StringParameterDTO(
                parameter_id    = param.parameter_id,
                algorithm_id    = param.algorithm_id,
                name            = param.name,
                default_value   = param.default_value,
                created_at      = param.created_at.isoformat(),
                updated_at      = param.updated_at.isoformat()
            ))
        except Exception as e:
            L.error(f"Exception occurred while updating string parameter: {e}")
            return Err(e)
    
    async def delete_string_parameter_by_id(self, parameter_id:int)->Result[bool,Exception]:
        try:
            result = await self.repository.delete_by_id(parameter_id=parameter_id)
            if result.is_err:
                L.error(f"Error deleting string parameter by id: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            return Ok(result.unwrap())
        except Exception as e:
            L.error(f"Exception occurred while deleting string parameter by id: {e}")
            return Err(e)

class TasksService:

    def __init__(self, repository: TasksRepository):
        self.repository = repository

    async def create_task(
        self, 
        user_id: str,           
        dto: DTO.TaskCreateFormDTO
    ) -> Result[DTO.TaskCreatedResponseDTO, Exception]:
        try:
            result = await self.repository.create(
                user_id       = user_id,
                algorithm_id  = dto.algorithm_id,
                response_time = dto.response_time
            )
            if result.is_err:
                L.error(f"Error creating task: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            task = result.unwrap()
            return Ok(DTO.TaskCreatedResponseDTO(
                task_id       = task.task_id,
                user_id       = user_id,
                algorithm_id  = dto.algorithm_id,
                response_time = task.response_time,
                created_at    = task.created_at.isoformat(),
            ))
        except Exception as e:
            L.error(f"Exception occurred while creating task: {e}")
            return Err(e)

    async def get_tasks_by_user(
        self, 
        user_id: str
    ) -> Result[list[DTO.TaskDTO], Exception]:
        try:
            result = await self.repository.get_by_user_id(user_id=user_id)
            if result.is_err:
                L.error(f"Error getting tasks by user: {result.unwrap_err()}")
                return Err(result.unwrap_err())
            tasks = result.unwrap()
            return Ok([
                DTO.TaskDTO(
                    task_id       = task.task_id,
                    user_id       = user_id,
                    algorithm_id  = task.algorithm_id,
                    response_time = task.response_time,
                    created_at    = task.created_at.isoformat(),
                    updated_at    = task.updated_at.isoformat(),
                ) for task in tasks
            ])
        except Exception as e:
            L.error(f"Exception occurred while getting tasks by user: {e}")
            return Err(e)