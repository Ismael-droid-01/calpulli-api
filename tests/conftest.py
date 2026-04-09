
import asyncio
import os
from dotenv import load_dotenv
import pymysql
import pytest
from tortoise import Tortoise
from tortoise.contrib.test import tortoise_test_context
from ppml.models import Task, UserProfile, Algorithm, NumericParameter, StringParameter,Result
from ppml.dtos import UserProfileDTO, TaskCreateFormDTO
from ppml.repositories import UsersProfilesRepository, AlgorithmsRepository, TasksRepository

DATABASE_NAME = "ppml_database"
USER= "samuel_user"
PASSWORD = "samuel_password"
TEST_DB_URL = f"mysql://{USER}:{PASSWORD}@localhost:3306/{DATABASE_NAME}" 


def pytest_configure(config):
    if os.path.exists(".env.test"):
        load_dotenv(dotenv_path=".env.test")

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True, scope="session")
async def initialize_tests():
    # Setup: Initialize Tortoise with your models
    connection = pymysql.connect(host='localhost', user=USER, password=PASSWORD)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {DATABASE_NAME}")
    finally:
        connection.close()
    async with tortoise_test_context(
        db_url=TEST_DB_URL, 
        modules=['ppml.models'],

    ) as ctx:
        await Tortoise.generate_schemas()
        yield ctx

@pytest.fixture(autouse=True)
async def clean_database():
    await _clean()
    yield
    await _clean()

async def _clean():
    await Result.all().delete()
    await Task.all().delete()         
    await NumericParameter.all().delete()
    await StringParameter.all().delete()
    await Algorithm.all().delete()    
    await UserProfile.all().delete()

def mock_current_user(user_id: str, username: str):
    """Genera un override de get_current_user para simular autenticación."""
    async def _mock():
        return UserProfileDTO(
            user_id    = user_id,
            username   = username,
            email      = f"{username}@test.com",
            first_name = "Test",
            last_name  = "User",
            is_disabled= False,
            created_at = "2024-01-01T00:00:00",
            updated_at = "2024-01-01T00:00:00",
        )
    return _mock

async def create_test_user(suffix: str = ""):
    repo = UsersProfilesRepository()
    result = await repo.create(
        user_id    = f"test-user-id-{suffix}",
        username   = f"testuser{suffix}",
        email      = f"testuser{suffix}@example.com",
        first_name = f"TestFirstName{suffix}",
        last_name  = f"TestLastName{suffix}"
    )
    return result.unwrap()

async def create_test_algorithm(name: str = "TestAlgo"):
    repo = AlgorithmsRepository()
    result = await repo.create(name=name, type="CLUSTERING")
    return result.unwrap()

async def create_test_task(user_id: str, algorithm_id: int):
    repo = TasksRepository()
    dto = TaskCreateFormDTO(algorithm_id=algorithm_id, response_time=1.23)
    result = await repo.create(user_id=user_id, algorithm_id=algorithm_id, response_time=dto.response_time)
    return result.unwrap()