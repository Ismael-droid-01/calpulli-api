from pydantic import BaseModel, Field
from typing import  Optional,List
from calpulli.models import AlgorithmType

class UserCreateFormDTO(BaseModel):
    username: str = Field(..., description="The desired username for the new user")
    email: str = Field(..., description="The email address of the new user")
    password: str = Field(..., description="The password for the new user")
    first_name: str = Field(..., description="The first name of the new user")
    last_name: str = Field(..., description="The last name of the new user")
    
class UserCreatedResponseDTO(BaseModel):
    user_id: str = Field(..., description="The unique identifier of the created user")
    username: str = Field(..., description="The username of the created user")
    email: str = Field(..., description="The email address of the created user")

class UserLoginFormDTO(BaseModel):
    username: str = Field(..., description="The username of the user attempting to log in")
    password: str = Field(..., description="The password of the user attempting to log in")
    
class UserLoggedInResponseDTO(BaseModel):
    user_id: str = Field(..., description="The unique identifier of the logged-in user")
    username: str = Field(..., description="The username of the logged-in user")
    email: str = Field(..., description="The email address of the logged-in user")
    first_name: str = Field(..., description="The first name of the logged-in user")
    last_name: str = Field(..., description="The last name of the logged-in user")
    access_token: str = Field(..., description="The authentication token for the signed-in user")
    temporal_secret: str = Field(..., description="A temporary secret for additional security measures during the session")

class UserProfileDTO(BaseModel):
    user_profile_id:int = Field(..., description="The unique identifier of the user profile")
    user_id: str = Field(..., description="The unique identifier of the user")
    username: str = Field(..., description="The username of the user")
    email: str = Field(..., description="The email address of the user")
    first_name: str = Field(..., description="The first name of the user")
    last_name: str = Field(..., description="The last name of the user")
    is_disabled: bool = Field(default=False, description="Indicates whether the user account is disabled")
    created_at: str = Field(..., description="The ISO8601 timestamp when the user profile was created")
    updated_at: str = Field(..., description="The ISO8601 timestamp when the user profile was last updated")

class AlgorithmCreateFormDTO(BaseModel):
    name: str = Field(..., description="The name of the algorithm")
    type: AlgorithmType = Field(..., description="The type/category of the algorithm (e.g., 'CLUSTERING', 'ML')")

class AlgorithmCreatedResponseDTO(BaseModel):
    algorithm_id: int = Field(..., description="The unique identifier of the created algorithm")
    name: str = Field(..., description="The name of the created algorithm")
    type: AlgorithmType = Field(..., description="The type/category of the created algorithm")

class AlgorithmDTO(BaseModel):
    algorithm_id: int = Field(..., description="The unique identifier of the algorithm")
    name: str = Field(..., description="The name of the algorithm")
    type: AlgorithmType = Field(..., description="The type/category of the algorithm")
    created_at: str = Field(..., description="The ISO8601 timestamp when the algorithm was created")
    updated_at: str = Field(..., description="The ISO8601 timestamp when the algorithm was last updated")

class NumericParameterCreateFormDTO(BaseModel):
    algorithm_id: int = Field(..., description="The unique identifier of the associated algorithm")
    name: str = Field(..., description="The name of the numeric parameter")
    type: str = Field(..., description="The data type of the numeric parameter (e.g., 'float', 'int')")
    default_value: float = Field(..., description="The default value for the numeric parameter")
    max_value: float = Field(..., description="The maximum allowed value for the numeric parameter")

class NumericParameterCreatedResponseDTO(BaseModel):
    parameter_id: int = Field(..., description="The unique identifier of the created numeric parameter")
    algorithm_id: int = Field(..., description="The unique identifier of the associated algorithm")
    name: str = Field(..., description="The name of the numeric parameter")
    type: str = Field(..., description="The data type of the numeric parameter (e.g., 'float', 'int')")
    default_value: float = Field(..., description="The default value for the numeric parameter")
    max_value: float = Field(..., description="The maximum allowed value for the numeric parameter")

class NumericParameterDTO(BaseModel):
    parameter_id: int = Field(..., description="The unique identifier of the numeric parameter")
    algorithm_id: int = Field(..., description="The unique identifier of the associated algorithm")
    name: str = Field(..., description="The name of the numeric parameter")
    type: str = Field(..., description="The data type of the numeric parameter (e.g., 'float', 'int')")
    default_value: float = Field(..., description="The default value for the numeric parameter")
    max_value: float = Field(..., description="The maximum allowed value for the numeric parameter")
    created_at: str = Field(..., description="The ISO8601 timestamp when the numeric parameter was created")
    updated_at: str = Field(..., description="The ISO8601 timestamp when the numeric parameter was last updated")

class StringParameterCreateFormDTO(BaseModel):
    algorithm_id: int = Field(..., description="The unique identifier of the associated algorithm")
    name: str = Field(..., description="The name of the string parameter")
    default_value: str = Field(..., description="The default value for the string parameter")

class StringParameterCreatedResponseDTO(BaseModel):
    parameter_id: int = Field(..., description="The unique identifier of the created string parameter")
    algorithm_id: int = Field(..., description="The unique identifier of the associated algorithm")
    name: str = Field(..., description="The name of the string parameter")
    default_value: str = Field(..., description="The default value for the string parameter")

class StringParameterDTO(BaseModel):
    parameter_id: int = Field(..., description="The unique identifier of the string parameter")
    algorithm_id: int = Field(..., description="The unique identifier of the associated algorithm")
    name: str = Field(..., description="The name of the string parameter")
    default_value: str = Field(..., description="The default value for the string parameter")
    created_at: str = Field(..., description="The ISO8601 timestamp when the string parameter was created")
    updated_at: str = Field(..., description="The ISO8601 timestamp when the string parameter was last updated")

class AlgorithmParametersDTO(BaseModel):
    algorithm_id: int = Field(..., description="The unique identifier of the algorithm")
    numeric_parameters: list[NumericParameterDTO] = Field(default=[], description="List of numeric parameters for the algorithm")
    string_parameters: list[StringParameterDTO] = Field(default=[], description="List of string parameters for the algorithm")

class TaskCreateFormDTO(BaseModel):
    algorithm_id: int = Field(..., description="The unique identifier of the algorithm to be executed")
    response_time: float = Field(..., description="The expected response time for the task execution in seconds")

class TaskCreatedResponseDTO(BaseModel):
    task_id: int = Field(..., description="The unique identifier of the created task")
    user_id: int = Field(..., description="The unique identifier of the user who created the task")
    algorithm_id: int = Field(..., description="The unique identifier of the algorithm to be executed")
    response_time: float = Field(..., description="The expected response time for the task execution in seconds")

class TaskDTO(BaseModel):
    task_id: int = Field(..., description="The unique identifier of the task")
    user_id: int = Field(..., description="The unique identifier of the user who created the task")
    algorithm_id: int = Field(..., description="The unique identifier of the algorithm to be executed")
    response_time: float = Field(..., description="The expected response time for the task execution in seconds")
    created_at: str = Field(..., description="The ISO8601 timestamp when the task was created")
    updated_at: str = Field(..., description="The ISO8601 timestamp when the task was last updated")

class ResultCreateFormDTO(BaseModel):  
    task_id: int = Field(..., description="The unique identifier of the task associated with this result")
    format: str = Field(..., description="The format of the result (e.g., 'json', 'csv')")
    url: str = Field(..., description="The URL where the result can be accessed")

class ResultCreatedResponseDTO(BaseModel):  
    result_id: int = Field(..., description="The unique identifier of the created result")
    task_id: int = Field(..., description="The unique identifier of the task associated with this result")
    format: str = Field(..., description="The format of the result (e.g., 'json', 'csv')")
    url: str = Field(..., description="The URL where the result can be accessed")

class ResultDTO(BaseModel): 
    result_id: int = Field(..., description="The unique identifier of the result")
    task_id: int = Field(..., description="The unique identifier of the task associated with this result")
    format: str = Field(..., description="The format of the result (e.g., 'json', 'csv')")
    url: str = Field(..., description="The URL where the result can be accessed")
    created_at: str = Field(..., description="The ISO8601 timestamp when the result was created")
    updated_at: str = Field(..., description="The ISO8601 timestamp when the result was last updated")


class NumericValueDTO(BaseModel):
    name: str
    value: float

class StringValueDTO(BaseModel):
    name: str
    value: str

class TaskWithParametersDTO(BaseModel):
    task_id: int
    algorithm__id: Optional[str] = Field(None, description="The unique identifier of the associated algorithm, if available")
    
    algorithm_name: Optional[str] = Field(None, description="The name of the algorithm associated with the task, if available")
    status: str 
    numeric_parameters: list[NumericValueDTO] = []
    string_parameters: list[StringValueDTO] = []


class NumericValueCreateDTO(BaseModel):
    parameter_id: int
    value: float

class StringValueCreateDTO(BaseModel):
    parameter_id: int
    value: str

class TaskCreateAggregateDTO(BaseModel):
    algorithm_id: int
    user_id: Optional[int] = Field(None, description="The unique identifier of the user creating the task, if available")
    numeric_values: List[NumericValueCreateDTO] = []
    string_values: List[StringValueCreateDTO] = []