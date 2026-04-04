from pydantic import BaseModel, Field

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
    type: str = Field(..., description="The type/category of the algorithm")

class AlgorithmCreatedResponseDTO(BaseModel):
    algorithm_id: int = Field(..., description="The unique identifier of the created algorithm")
    name: str = Field(..., description="The name of the created algorithm")
    type: str = Field(..., description="The type/category of the created algorithm")

class AlgorithmDTO(BaseModel):
    algorithm_id: int = Field(..., description="The unique identifier of the algorithm")
    name: str = Field(..., description="The name of the algorithm")
    type: str = Field(..., description="The type/category of the algorithm")
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