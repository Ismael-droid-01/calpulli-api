import pytest
from httpx import AsyncClient,ASGITransport
from ppml.server import app
import ppml.dtos as DTO

from uuid import uuid4
from tortoise import Tortoise
import asyncio

TEST_DB_URL = "mysql://samuel_user:samuel_password@localhost:3306/ppml_database" 
@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True, scope="session")
async def initialize_tests():
    # Setup: Initialize Tortoise with your models
    await Tortoise.init(
        db_url=TEST_DB_URL,
        modules={'models': ['ppml.models']}
    )
    await Tortoise.generate_schemas()
    
    yield # Tests run here
    
    # Teardown: Clean up
    await Tortoise.close_connections()

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        uid = uuid4().hex[:8]  # Generate a unique identifier for the test user
        username = f"testuser_{uid}"
        password = "password123"
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