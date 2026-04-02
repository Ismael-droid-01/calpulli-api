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