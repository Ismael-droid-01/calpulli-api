
import asyncio
import os
from typing import List, Tuple,AsyncGenerator
from dotenv import load_dotenv
import pymysql
import pytest
from httpx import ASGITransport, AsyncClient

from tortoise import Tortoise
from calpulli.models import NumericParameterType, StringParameterValue, NumericParameterValue, Task, UserProfile, Algorithm, NumericParameter, StringParameter,Result,Dataset
from calpulli.dtos import UserProfileDTO
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

async def dummy_close_connections():
    pass

@pytest.fixture(autouse=True, scope="session")
# @pytest.fixture(autouse=True)
async def initialize_tests():
    # Setup: Initialize Tortoise with your models
    connection = pymysql.connect(host='localhost', user=USER, password=PASSWORD)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {DATABASE_NAME}")
            cursor.execute(f"CREATE DATABASE {DATABASE_NAME}")
    finally:
        connection.close()
    
    await Tortoise.init(
        db_url=TEST_DB_URL,
        modules={'models': ['calpulli.models']}
    )
    await Tortoise.generate_schemas()

    original_close = Tortoise.close_connections
    # This is a workaround to prevent Tortoise from closing connections after each test, which can cause issues in an async test environment. 
    # We will close connections manually at the end of the session.
    Tortoise.close_connections = dummy_close_connections
    yield
    Tortoise.close_connections = original_close
    await Tortoise.close_connections()

@pytest.fixture()
async def clean_database():
    await _clean()
    yield
    await _clean()



    # await _clean()

async def _clean():
    await NumericParameterValue.all().delete()
    await StringParameterValue.all().delete()
    await Result.all().delete()
    await Task.all().delete()         
    await NumericParameter.all().delete()
    await StringParameter.all().delete()
    await Algorithm.all().delete()
    await Dataset.all().delete()    
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

# @pytest.fixture
async def create_test_user(suffix: str = "")-> UserProfile:
    repo = UsersProfilesRepository()
    result = await repo.create(
        user_id    = f"test-user-id-{suffix}",
        username   = f"testuser{suffix}",
        email      = f"testuser{suffix}@example.com",
        first_name = f"TestFirstName{suffix}",
        last_name  = f"TestLastName{suffix}"
    )
    return result.unwrap()

async def create_test_task(user_id: str, algorithm_id: int)-> Task:
    repo = TasksRepository()
    result = await repo.create(
        algorithm_id  = algorithm_id,
        user_id       = user_id,
        response_time = 0.0
    )
    return result.unwrap()

@pytest.fixture
async def user():
    idd = uuid4().hex[:8]
    yield await create_test_user(suffix=idd)

# @pytest.fixture
async def create_test_algorithm(name: str = "TestAlgo")-> Algorithm:
    repo = AlgorithmsRepository()
    result = await repo.create(name=name, type="SUPERVISED")
    return result.unwrap()


@pytest.fixture
async def algorithm():
    idd = uuid4().hex[:8]
    yield await create_test_algorithm(name=f"TestAlgo{idd}")



@pytest.fixture
async def float_parameter(algorithm):
    yield await NumericParameter.create(
        algorithm=algorithm,
        name="learning_rate",
        type=NumericParameterType.FLOAT,
        default_value=0.01,
        max_value=1.0
    )


@pytest.fixture
async def integer_parameter(algorithm):
    yield await NumericParameter.create(
        algorithm=algorithm,
        name="n_estimators",
        type=NumericParameterType.INTEGER,
        default_value=100,
        max_value=500
    )


@pytest.fixture
async def boolean_parameter(algorithm):
    yield await NumericParameter.create(
        algorithm=algorithm,
        name="use_bias",
        type=NumericParameterType.BOOLEAN,
        default_value=0,
        max_value=1
    )

@pytest.fixture
async def string_parameter(algorithm:Algorithm)-> AsyncGenerator[StringParameter, None]:
    yield await StringParameter.create(
        algorithm     = algorithm,
        name          = "kernel",
        default_value = "rbf"
    )
@pytest.fixture
async def task(algorithm:Algorithm, user:UserProfile)-> AsyncGenerator[Task, None]:
    repo      = TasksRepository()
    result = await repo.create(
        algorithm_id  = algorithm.algorithm_id,
        user_id       = user.id,
        response_time = 0.0
    )
    yield result.unwrap()

@pytest.fixture
async def prepare_string_parameter_and_task(string_parameter,task):
    yield string_parameter, task

    




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

async def register_and_login_user(client: AsyncClient, suffix: str):
    """Función auxiliar para crear un usuario y obtener su DTO de login."""
    x_id = f"{suffix}_{uuid4().hex[:4]}"
    dto = DTO.UserCreateFormDTO(
        email      = f"user_{x_id}@test.com",
        username   = f"user_{x_id}",
        password   = "testpassword",
        first_name = f"Name_{x_id}",
        last_name  = f"Last_{x_id}"
    )
    
    register_response = await client.post("/users", json=dto.model_dump())
    assert register_response.status_code == 200, f"Error al registrar: {register_response.text}"

    response = await client.post("/users/login", json={"username": dto.username, "password": dto.password})
    assert response.status_code == 200, f"Error al iniciar sesión: {response.text}"
    
    data = response.json()
    return DTO.UserLoggedInResponseDTO(
        user_id         = data.get("user_id"),
        access_token    = data.get("access_token"),
        temporal_secret = data.get("temporal_secret"),
        username        = data.get("username"),
        email           = data.get("email"),
        first_name      = data.get("first_name"),
        last_name       = data.get("last_name")
    )