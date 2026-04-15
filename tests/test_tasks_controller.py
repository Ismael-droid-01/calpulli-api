import pytest
from httpx import AsyncClient, ASGITransport
from calpulli.services import TasksService
from calpulli.repositories import TasksRepository
from calpulli.dtos import TaskCreateFormDTO
from calpulli.server import app
import calpulli.middleware as MX
from tests.conftest import create_test_algorithm, create_test_user, mock_current_user

@pytest.mark.asyncio
async def test_create_task_service():
    user      = await create_test_user(suffix="create")
    algorithm = await create_test_algorithm(name="AlgoCreate")
    
    service = TasksService(repository=TasksRepository())
    dto     = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=1.23)
    result  = await service.create_task(user_id=user.user_id, dto=dto)

    assert result.is_ok
    task = result.unwrap()
    assert task.user_id       == user.user_id
    assert task.algorithm_id  == algorithm.algorithm_id
    assert task.response_time == 1.23
    assert task.task_id is not None


@pytest.mark.asyncio
async def test_create_task_user_not_found_service():
    algorithm = await create_test_algorithm(name="AlgoUserNotFound")
    
    service = TasksService(repository=TasksRepository())
    dto     = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=0.5)
    result  = await service.create_task(user_id="nonexistent-user-id", dto=dto)

    assert result.is_err


@pytest.mark.asyncio
async def test_create_task_algorithm_not_found_service():
    user = await create_test_user(suffix="algonotfound")

    service = TasksService(repository=TasksRepository())
    dto     = TaskCreateFormDTO(algorithm_id=999999, response_time=0.5)
    result  = await service.create_task(user_id=user.user_id, dto=dto)

    assert result.is_err


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


@pytest.mark.asyncio
async def test_get_tasks_by_user_not_found_service():
    service = TasksService(repository=TasksRepository())
    result  = await service.get_tasks_by_user(user_id="nonexistent-user-id")
    assert result.is_err


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
async def test_create_task_endpoint():
    user      = await create_test_user(suffix="endpoint-create")
    algorithm = await create_test_algorithm(name="AlgoEndpointCreate")

    app.dependency_overrides[MX.get_current_user] = mock_current_user(
        user_id  = user.user_id,
        username = user.username,
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload  = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=1.5).model_dump()
        response = await client.post("/tasks", json=payload)

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"]      == user.user_id
    assert data["algorithm_id"] == algorithm.algorithm_id
    assert data["response_time"] == 1.5
    assert "task_id" in data


@pytest.mark.asyncio
async def test_get_my_tasks_endpoint():
    user      = await create_test_user(suffix="endpoint-list")
    algorithm = await create_test_algorithm(name="AlgoEndpointList")

    service = TasksService(repository=TasksRepository())
    dto     = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=1.0)
    await service.create_task(user_id=user.user_id, dto=dto)
    await service.create_task(user_id=user.user_id, dto=dto)

    app.dependency_overrides[MX.get_current_user] = mock_current_user(
        user_id  = user.user_id,
        username = user.username,
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/tasks/my-tasks")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert all(t["user_id"] == user.user_id for t in data)


@pytest.mark.asyncio
async def test_get_task_by_id_endpoint():
    user      = await create_test_user(suffix="endpoint-detail")
    algorithm = await create_test_algorithm(name="AlgoEndpointDetail")

    service  = TasksService(repository=TasksRepository())
    dto      = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=3.0)
    created  = await service.create_task(user_id=user.user_id, dto=dto)
    task_id  = created.unwrap().task_id

    app.dependency_overrides[MX.get_current_user] = mock_current_user(
        user_id  = user.user_id,
        username = user.username,
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/tasks/{task_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"]  == task_id
    assert data["user_id"]  == user.user_id


@pytest.mark.asyncio
async def test_get_task_by_id_not_found_endpoint():
    user = await create_test_user(suffix="endpoint-notfound")

    app.dependency_overrides[MX.get_current_user] = mock_current_user(
        user_id  = user.user_id,
        username = user.username,
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/tasks/999999")

    app.dependency_overrides.clear()

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_task_unauthorized_endpoint():
    user_a    = await create_test_user(suffix="owner")
    user_b    = await create_test_user(suffix="intruder")
    algorithm = await create_test_algorithm(name="AlgoUnauth")

    service = TasksService(repository=TasksRepository())
    dto     = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=1.0)
    created = await service.create_task(user_id=user_a.user_id, dto=dto)
    task_id = created.unwrap().task_id

    app.dependency_overrides[MX.get_current_user] = mock_current_user(
        user_id  = user_b.user_id,
        username = user_b.username,
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/tasks/{task_id}")

    app.dependency_overrides.clear()

    assert response.status_code == 403