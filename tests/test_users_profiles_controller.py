import pytest
import calpulli.dtos as DTO
from uuid import uuid4

@pytest.mark.asyncio
async def test_create_user(client_with_before_and_after_clean):
    client = client_with_before_and_after_clean
    # async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
    uid = uuid4().hex[:8]  # Generate a unique identifier for the test user
    username = f"testuser_{uid}"
    password = "password123"
    print(f"Testing with username: {username} and password: {password}")
    json = DTO.UserCreateFormDTO(
        username   = username,
        email      = f"{username}@example.com",
        password   = password,
        first_name = "Test",
        last_name  = "User"
    )
    response = await client.post("/users", json=json.model_dump())
    assert response.status_code == 200

    # Login 
    json = DTO.UserLoginFormDTO(
        username = username,
        password = password
    )
    response = await client.post("/users/login",json=json.model_dump())
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_current_user(client_with_before_and_after_clean):
    client = client_with_before_and_after_clean
    uid = uuid4().hex[:8]  # Generate a unique identifier for the test user
    username = f"testuser_{uid}"
    password = "password123"
    print(f"Testing with username: {username} and password: {password}")
    json = DTO.UserCreateFormDTO(
        username   = username,
        email      = f"{username}@example.com",
        password   = password,
        first_name = "Test",
        last_name  = "User"
    )
    response = await client.post("/users", json=json.model_dump())
    assert response.status_code == 200

    # Login 
    json = DTO.UserLoginFormDTO(
        username = username,
        password = password
    )
    response = await client.post("/users/login",json=json.model_dump())
    assert response.status_code == 200
    login_dto = DTO.UserLoggedInResponseDTO.model_validate(response.json())
    token = login_dto.access_token
    assert token is not None
    # Now, test the /users/me endpoint
    headers = {"Authorization": f"Bearer {token}", "Temporal-Secret-Key": login_dto.temporal_secret}
    response = await client.get("/users/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == username
    assert user_data["email"] == f"{username}@example.com"