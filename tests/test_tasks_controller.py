import pytest
from httpx import AsyncClient, ASGITransport
from calpulli.services import TasksService
from calpulli.repositories import TasksRepository
from calpulli.dtos import TaskCreateFormDTO
from calpulli.server import app
import calpulli.middleware as MX
from tests.conftest import create_test_algorithm, create_test_user,  mock_current_user, prepare_with_user_algorithm_client, prepare_with_user_algorithm_task_client
from calpulli.models import Algorithm, NumericParameter,NumericParameterType,AlgorithmType
import calpulli.dtos as DTO

@pytest.mark.asyncio
async def test_create_task_service(prepare_with_user_algorithm_client):
    user,algorithm,client = prepare_with_user_algorithm_client
    headers ={"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}

    dto = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=1.23)
    response = await client.post("/tasks",json=dto.model_dump(),headers = headers) 
    assert response.status_code == 200  # Validación de campos faltantes
    # algorithm = await create_test_algorithm(name="AlgoCreate")
    
    # This comes from the fixture prepare_with_algorithm_user_task_client
    # service = TasksService(repository=TasksRepository())
    # dto     = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=1.23)
    # result  = await service.create_task(user_id=user.user_id, dto=dto)

    # assert result.is_ok
    # task = result.unwrap()
    # assert task.user_id       == user.user_id
    # assert task.algorithm_id  == algorithm.algorithm_id
    # assert task.response_time == 1.23
    # assert task.task_id is not None

@pytest.mark.asyncio
async def test_create_new_task_integration(get_user_clean_and_get_client):
    user,client =  get_user_clean_and_get_client
    
    # A. Preparar los datos reales en la base de datos en memoria
    
    algo = await Algorithm.create(name="Kmeans", type=AlgorithmType.UNSUPERVISED)
    
    param = await NumericParameter.create(
        algorithm     = algo,
        name          = "k",
        type          = NumericParameterType.INTEGER,
        default_value = 2,
        max_value     = 100
    )

    payload = DTO.TaskCreateAggregateDTO(
        algorithm_id   = algo.algorithm_id,
        numeric_values = [],
        string_values  = [],
        # user_id        = user.
    )
    
    # C. Ejecutar la petición HTTP
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}
    response = await client.post("/tasks/run", json=payload.model_dump(),headers=headers)
    
    # D. Validaciones HTTP
    print("Response status code:", response)
    assert response.status_code == 200


@pytest.mark.skip(reason="this test is not a controller test, it's more a task service test, we should move it to the service tests")
@pytest.mark.asyncio
async def test_create_task_user_not_found_service():
    algorithm = await create_test_algorithm(name="AlgoUserNotFound")
    
    service = TasksService(repository=TasksRepository())
    dto     = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=0.5)
    result  = await service.create_task(user_id="nonexistent-user-id", dto=dto)

    assert result.is_err


@pytest.mark.skip(reason="this test is not a controller test, it's more a task service test, we should move it to the service tests")
@pytest.mark.asyncio
async def test_create_task_algorithm_not_found_service():
    user = await create_test_user(suffix="algonotfound")

    service = TasksService(repository=TasksRepository())
    dto     = TaskCreateFormDTO(algorithm_id=999999, response_time=0.5)
    result  = await service.create_task(user_id=user.user_id, dto=dto)

    assert result.is_err


@pytest.mark.skip(reason="this test is not a controller test, it's more a task service test, we should move it to the service tests")
@pytest.mark.asyncio
async def test_get_tasks_by_user_service():
    user      = await create_test_user(suffix="getbyuser")
    algorithm = await create_test_algorithm(name="AlgoGetByUser")

    service = TasksService(repository=TasksRepository())
    dto     = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=2.0)

    await service.create_task(user_id=user.user_id, dto=dto)
    await service.create_task(user_id=user.user_id, dto=dto)

    result = await service.get_tasks_by_user(user_id=user.user_id)

    assert result.is_ok
    tasks = result.unwrap()
    assert isinstance(tasks, list)
    assert len(tasks) >= 2
    assert all(t.user_id == user.user_id for t in tasks)


@pytest.mark.skip(reason="this test is not a controller test, it's more a task service test, we should move it to the service tests")
@pytest.mark.asyncio
async def test_get_tasks_by_user_not_found_service():
    service = TasksService(repository=TasksRepository())
    result  = await service.get_tasks_by_user(user_id="nonexistent-user-id")
    assert result.is_err


@pytest.mark.skip(reason="this test is not a controller test, it's more a task service test, we should move it to the service tests")
@pytest.mark.asyncio
async def test_get_tasks_by_user_empty_service():
    user    = await create_test_user(suffix="empty")
    service = TasksService(repository=TasksRepository())
    result  = await service.get_tasks_by_user(user_id=user.user_id)

    if result.is_ok:
        assert result.unwrap() == []
    else:
        assert result.is_err



@pytest.mark.asyncio
async def test_get_my_tasks_endpoint(prepare_with_user_algorithm_task_client):
    user,_,task,client = prepare_with_user_algorithm_task_client
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}
    # user      = await create_test_user(suffix="endpoint-list")
    # algorithm = await create_test_algorithm(name="AlgoEndpointList")

    # service = TasksService(repository=TasksRepository())
    # dto     = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=1.0)
    # await service.create_task(user_id=user.user_id, dto=dto)
    # await service.create_task(user_id=user.user_id, dto=dto)

    # app.dependency_overrides[MX.get_current_user] = mock_current_user(
    #     user_id  = user.user_id,
    #     username = user.username,
    # )

    # async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
    response = await client.get("/tasks/my-tasks",headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # assert all(t["user_id"] == user.user_id for t in data)


@pytest.mark.asyncio
async def test_get_task_by_id_endpoint(prepare_with_user_algorithm_task_client):
    user,_,tasks,client = prepare_with_user_algorithm_task_client
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}
    # user      = await create_test_user(suffix="endpoint-detail")
    # algorithm = await create_test_algorithm(name="AlgoEndpointDetail")

    # service  = TasksService(repository=TasksRepository())
    # dto      = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=3.0)
    # created  = await service.create_task(user_id=user.user_id, dto=dto)
    # task_id  = created.unwrap().task_id

    # app.dependency_overrides[MX.get_current_user] = mock_current_user(
    #     user_id  = user.user_id,
    #     username = user.username,
    # )

    # async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
    task = tasks[0]
    response = await client.get(f"/tasks/{task.task_id}", headers=headers)

    # app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"]  == task.task_id
    assert data["algorithm_id"]  == task.algorithm_id
    # assert data["user_id"]  == user.user_id


@pytest.mark.asyncio
async def test_get_task_by_id_not_found_endpoint(prepare_with_user_algorithm_task_client):
    user,_,_,client = prepare_with_user_algorithm_task_client
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}
    response = await client.get("/tasks/999999", headers=headers)

    app.dependency_overrides.clear()

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_task_unauthorized_endpoint(prepare_with_user_algorithm_task_client):
    user, algorithm, tasks, client = prepare_with_user_algorithm_task_client
    task = tasks[0]
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": "invalid-temporal-secret"}
    response = await client.get(f"/tasks/{task.task_id}", headers=headers)
    assert response.status_code == 401