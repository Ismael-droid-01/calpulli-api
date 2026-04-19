
import asyncio
import os
from typing import List, Tuple,AsyncGenerator
from wsgiref import headers
from dotenv import load_dotenv
import pymysql
import pytest
from httpx import ASGITransport, AsyncClient

from tortoise import Tortoise
from tortoise.contrib.test import tortoise_test_context
from calpulli.models import Task, UserProfile, Algorithm, NumericParameter, StringParameter,Result
from calpulli.dtos import UserProfileDTO, TaskCreateFormDTO
from calpulli.repositories import UsersProfilesRepository, AlgorithmsRepository, TasksRepository
from calpulli.server import app
import calpulli.dtos as DTO
from uuid import uuid4
DATABASE_NAME = "calpulli_database"
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


@pytest.fixture()
async def client():
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client
            
@pytest.fixture()
async def client_with_before_and_after_clean():
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await _clean()  # Limpiar la base de datos antes de cada test
            yield client
            await _clean()  # Limpiar la base de datos después de cada test


@pytest.fixture()
async def get_user_clean_and_get_client(client_with_before_and_after_clean)-> Tuple[DTO.UserLoggedInResponseDTO,AsyncClient]:
    x_id = uuid4().hex
    dto = DTO.UserCreateFormDTO(
        email    = f"testuser_{x_id}@test.com",
        username = f"testuser_{x_id}",
        password = "testpassword",
        first_name= f"TestFirstName_{x_id}",
        last_name = f"TestLastName_{x_id}"
    )
    response = await client_with_before_and_after_clean.post("/users", json=dto.model_dump())
    assert response.status_code == 200
    response = await client_with_before_and_after_clean.post("/users/login", json={"username": dto.username, "password": dto.password})
    data_json = response.json()
    dto = DTO.UserLoggedInResponseDTO(
        first_name      = data_json.get("first_name"),
        last_name       = data_json.get("last_name"),
        temporal_secret = data_json.get("temporal_secret"),
        user_id         = data_json.get("user_id"),
        access_token    = data_json.get("access_token"),
        email           = data_json.get("email"),
        username        = data_json.get("username"),
    )
    return dto,client_with_before_and_after_clean 



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
        modules=['calpulli.models'],

    ) as ctx:
        await Tortoise.generate_schemas()
        yield ctx

@pytest.fixture()
async def clean_database():
    await _clean()
    yield
    await _clean()



    # await _clean()

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
    result = await repo.create(name=name, type="SUPERVISED")
    return result.unwrap()

# async def create_test_task(user_id: str, algorithm_id: int):
#     repo = TasksRepository()
#     dto = TaskCreateFormDTO(algorithm_id=algorithm_id, response_time=1.23)
#     result = await repo.create(user_id=user_id, algorithm_id=algorithm_id, response_time=dto.response_time)
#     return result.unwrap()

@pytest.fixture()
async def prepare_with_user_algorithm_client(get_user_clean_and_get_client)-> AsyncGenerator[Tuple[DTO.UserLoggedInResponseDTO,Algorithm,AsyncClient], None]:
    user, client = get_user_clean_and_get_client
    algo_suffix  = uuid4().hex[:8]
    algorithm    = await create_test_algorithm(name=f"Algo{algo_suffix}")
    yield user, algorithm, client
@pytest.fixture()
async def prepare_with_user_algorithm_task_client(get_user_clean_and_get_client)-> AsyncGenerator[Tuple[DTO.UserLoggedInResponseDTO,Algorithm,List[Task],AsyncClient], None]:
    user, client = get_user_clean_and_get_client
    algorithm = await create_test_algorithm(name="TaskCreatorAlgo")
    tasks = []
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}
    for i in range(3):
        task_json = DTO.TaskCreateFormDTO(
            algorithm_id=algorithm.algorithm_id, 
            response_time=1.0 + i
        )
        response = await client.post("/tasks", json=task_json.model_dump(),headers=headers)
        assert response.status_code == 200
        task_data = response.json()
        tasks.append(
            DTO.TaskCreatedResponseDTO.model_validate(task_data)
        )
    return user,algorithm,tasks,client