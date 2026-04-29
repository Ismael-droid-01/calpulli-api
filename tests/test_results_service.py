import pytest
from calpulli.dtos import ResultCreateFormDTO
from calpulli.repositories import ResultsRepository
from calpulli.services import ResultsService
from tests.conftest import create_test_algorithm,  create_test_user, create_test_task

@pytest.mark.asyncio
async def test_create_result():
    user      = await create_test_user(suffix="result-create")
    algorithm = await create_test_algorithm(name="AlgoResultCreate")
    task      = await create_test_task(user_id=user.id, algorithm_id=algorithm.algorithm_id)
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
    task = None
    task      = await create_test_task(user_id=user.id, algorithm_id=algorithm.algorithm_id)

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

