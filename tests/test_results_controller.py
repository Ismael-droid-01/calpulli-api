from httpx import ASGITransport, AsyncClient
import pytest
from ppml.repositories import ResultsRepository, TasksRepository, UsersProfilesRepository, AlgorithmsRepository
from ppml.dtos import ResultCreateFormDTO, TaskCreateFormDTO
from ppml.services import ResultsService
from ppml.server import app
import ppml.middleware as MX
from tests.test_tasks_controller import mock_current_user

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
    result = await repo.create(name=name, type="classification")
    return result.unwrap()

async def create_test_task(user_id: str, algorithm_id: int):
    repo = TasksRepository()
    dto = TaskCreateFormDTO(algorithm_id=algorithm_id, response_time=1.23)
    result = await repo.create(user_id=user_id, algorithm_id=algorithm_id, response_time=dto.response_time)
    return result.unwrap()

@pytest.mark.asyncio
async def test_create_result():
    user      = await create_test_user(suffix="result-create")
    algorithm = await create_test_algorithm(name="AlgoResultCreate")
    task      = await create_test_task(user_id=user.user_id, algorithm_id=algorithm.algorithm_id)

    service = ResultsService(repository=ResultsRepository())
    dto     = ResultCreateFormDTO(task_id=task.task_id, format="json", url="http://example.com/result.json")
    result  = await service.create_result(task_id=task.task_id, dto=dto)

    assert result.is_ok
    created_result = result.unwrap()
    assert created_result.task_id == task.task_id
    assert created_result.format == "json"
    assert created_result.url == "http://example.com/result.json"
    assert created_result.result_id is not None

@pytest.mark.asyncio
async def test_create_result_task_not_found():
    service = ResultsService(repository=ResultsRepository())
    dto     = ResultCreateFormDTO(task_id=9999, format="json", url="http://example.com/result.json")
    result  = await service.create_result(task_id=9999, dto=dto)

    assert result.is_err

@pytest.mark.asyncio
async def test_get_results_by_task_id():
    user      = await create_test_user(suffix="result-get")
    algorithm = await create_test_algorithm(name="AlgoResultGet")
    task      = await create_test_task(user_id=user.user_id, algorithm_id=algorithm.algorithm_id)

    service = ResultsService(repository=ResultsRepository())
    
    # Create multiple results for the same task
    for i in range(3):
        dto = ResultCreateFormDTO(task_id=task.task_id, format="json", url=f"http://example.com/result_{i}.json")
        await service.create_result(task_id=task.task_id, dto=dto)

    # Retrieve results by task ID
    result = await service.get_results_by_task_id(task_id=task.task_id)
    
    assert result.is_ok
    results_list = result.unwrap()
    assert len(results_list) == 3
    for i, res in enumerate(results_list):
        assert res.task_id == task.task_id
        assert res.format == "json"
        assert res.url == f"http://example.com/result_{i}.json" 

@pytest.mark.asyncio
async def test_get_results_by_task_id_task_not_found():
    service = ResultsService(repository=ResultsRepository())
    result  = await service.get_results_by_task_id(task_id=9999)
    assert result.is_err
   
@pytest.mark.asyncio
async def test_create_result_endpoint():
    user      = await create_test_user(suffix="res-endpoint")
    algorithm = await create_test_algorithm(name="AlgoResEndpoint")
    task      = await create_test_task(user_id=user.user_id, algorithm_id=algorithm.algorithm_id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload  = ResultCreateFormDTO(
            task_id = task.task_id,
            format  = "json",
            url     = "http://storage.example.com/result/1"
        ).model_dump()
        response = await client.post("/results", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task.task_id
    assert data["format"]  == "json"
    assert data["url"]     == "http://storage.example.com/result/1"
    assert "result_id" in data


@pytest.mark.asyncio
async def test_create_result_task_not_found_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload  = ResultCreateFormDTO(
            task_id = 999999,
            format  = "json",
            url     = "http://storage.example.com/result/x"
        ).model_dump()
        response = await client.post("/results", json=payload)

    assert response.status_code == 500


@pytest.mark.asyncio
async def test_create_multiple_results_same_task_endpoint():
    user      = await create_test_user(suffix="res-multi-endpoint")
    algorithm = await create_test_algorithm(name="AlgoResMultiEndpoint")
    task      = await create_test_task(user_id=user.user_id, algorithm_id=algorithm.algorithm_id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload_1 = ResultCreateFormDTO(
            task_id = task.task_id,
            format  = "json",
            url     = "http://example.com/1"
        ).model_dump()
        payload_2 = ResultCreateFormDTO(
            task_id = task.task_id,
            format  = "csv",
            url     = "http://example.com/2"
        ).model_dump()

        r1 = await client.post("/results", json=payload_1)
        r2 = await client.post("/results", json=payload_2)

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["result_id"] != r2.json()["result_id"]

@pytest.mark.asyncio
async def test_get_results_for_task_endpoint():
    user      = await create_test_user(suffix="res-list-endpoint")
    algorithm = await create_test_algorithm(name="AlgoResListEndpoint")
    task      = await create_test_task(user_id=user.user_id, algorithm_id=algorithm.algorithm_id)

    repo = ResultsRepository()
    await repo.create(task_id=task.task_id, format="json", url="http://example.com/1")
    await repo.create(task_id=task.task_id, format="csv",  url="http://example.com/2")

    app.dependency_overrides[MX.get_current_user] = mock_current_user(
        user_id  = user.user_id,
        username = user.username,
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/tasks/{task.task_id}/results")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert all(r["task_id"] == task.task_id for r in data)


@pytest.mark.asyncio
async def test_get_results_for_task_not_found_endpoint():
    user = await create_test_user(suffix="res-list-notfound")

    app.dependency_overrides[MX.get_current_user] = mock_current_user(
        user_id  = user.user_id,
        username = user.username,
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/tasks/999999/results")

    app.dependency_overrides.clear()

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_results_for_task_empty_endpoint():
    user      = await create_test_user(suffix="res-list-empty")
    algorithm = await create_test_algorithm(name="AlgoResListEmpty")
    task      = await create_test_task(user_id=user.user_id, algorithm_id=algorithm.algorithm_id)

    app.dependency_overrides[MX.get_current_user] = mock_current_user(
        user_id  = user.user_id,
        username = user.username,
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/tasks/{task.task_id}/results")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == []