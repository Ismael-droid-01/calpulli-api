from httpx import ASGITransport, AsyncClient
import pytest
from calpulli.dtos import ResultCreateFormDTO
from calpulli.repositories import ResultsRepository
from calpulli.services import ResultsService
from calpulli.server import app
from tests.conftest import create_test_algorithm,  create_test_user

@pytest.mark.skip(reason="This is not a controller unit test, it's more of a test for the ResultsService. Consider moving it to a different test file (e.g test_results_service.py).")
@pytest.mark.asyncio
async def test_create_result():
    user      = await create_test_user(suffix="result-create")
    algorithm = await create_test_algorithm(name="AlgoResultCreate")
    # You must create a task to be able to create a result, but since the task creation is tested in other test, you can just create a task directly using the repositories or services without going through the API endpoints. This way you can isolate the test for the ResultsService and not depend on the Task creation logic.
    task = None
    # task      = await create_test_task(user_id=user.user_id, algorithm_id=algorithm.algorithm_id)

    service = ResultsService(repository=ResultsRepository())
    dto     = ResultCreateFormDTO(task_id=task.task_id, format="json", url="http://example.com/result.json")
    result  = await service.create_result(task_id=task.task_id, dto=dto)

    assert result.is_ok
    created_result = result.unwrap()
    assert created_result.task_id == task.task_id
    assert created_result.format == "json"
    assert created_result.url == "http://example.com/result.json"
    assert created_result.result_id is not None


@pytest.mark.skip(reason="This is not a controller unit test, it's more of a test for the ResultsService. Consider moving it to a different test file (e.g test_results_service.py).")
@pytest.mark.asyncio
async def test_create_result_task_not_found():
    service = ResultsService(repository=ResultsRepository())
    dto     = ResultCreateFormDTO(task_id=9999, format="json", url="http://example.com/result.json")
    result  = await service.create_result(task_id=9999, dto=dto)

    assert result.is_err

@pytest.mark.skip(reason="This is not a controller unit test, it's more of a test for the ResultsService. Consider moving it to a different test file (e.g test_results_service.py).")
@pytest.mark.asyncio
async def test_get_results_by_task_id():
    user      = await create_test_user(suffix="result-get")
    algorithm = await create_test_algorithm(name="AlgoResultGet")
    task = None
    # task      = await create_test_task(user_id=user.user_id, algorithm_id=algorithm.algorithm_id)

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

@pytest.mark.skip(reason="This is not a controller unit test, it's more of a test for the ResultsService. Consider moving it to a different test file (e.g test_results_service.py).")
@pytest.mark.asyncio
async def test_get_results_by_task_id_task_not_found():
    service = ResultsService(repository=ResultsRepository())
    result  = await service.get_results_by_task_id(task_id=9999)
    assert result.is_err


@pytest.mark.skip(reason="This controller is not mandatory cause the results are going to be inserted by the workers, not by the users. Consider removing the endpoint and the controller if it's not strictly necessary.")
@pytest.mark.asyncio
async def test_create_result_endpoint():
    user      = await create_test_user(suffix="res-endpoint")
    algorithm = await create_test_algorithm(name="AlgoResEndpoint")
    task = None
    # task      = await create_test_task(user_id=user.user_id, algorithm_id=algorithm.algorithm_id)

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
