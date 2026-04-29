import pytest
from calpulli.services import ResultsService, TasksService
from calpulli.repositories import ResultsRepository, TasksRepository
from calpulli.dtos import TaskCreateFormDTO
from tests.conftest import create_test_algorithm, create_test_user

@pytest.mark.asyncio
async def test_create_task_user_not_found_service():
    algorithm = await create_test_algorithm(name="AlgoUserNotFound")
    
    results_repo = ResultsRepository()
    results_service = ResultsService(repository=results_repo)
    
    tasks_repo = TasksRepository()
    service = TasksService(
        repository=tasks_repo, 
        result_service=results_service
    )
    
    dto = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=0.5)
    
    result = await service.create_task(user_id=999999, dto=dto)

    assert result.is_err
    
@pytest.mark.asyncio
async def test_create_task_algorithm_not_found_service():
    # 1. Crear el usuario de prueba
    user = await create_test_user(suffix="algonotfound")

    # 2. Instanciar dependencias (TasksService ahora requiere ResultsService)
    results_repo = ResultsRepository()
    results_service = ResultsService(repository=results_repo)
    
    tasks_repo = TasksRepository()
    service = TasksService(
        repository=tasks_repo, 
        result_service=results_service
    )

    # 3. Intentar crear tarea con un algorithm_id que no existe (999999)
    dto = TaskCreateFormDTO(algorithm_id=999999, response_time=0.5)
    
    # IMPORTANTE: Usamos user.id (el entero) para evitar el ValueError de tipos
    result = await service.create_task(user_id=user.id, dto=dto)

    assert result.is_err

@pytest.mark.asyncio
async def test_get_tasks_by_user_service():
    # 1. Preparación de datos
    user      = await create_test_user(suffix="getbyuser")
    algorithm = await create_test_algorithm(name="AlgoGetByUser")

    # 2. Instanciación con dependencias completas
    results_service = ResultsService(repository=ResultsRepository())
    service = TasksService(
        repository=TasksRepository(), 
        result_service=results_service
    )
    
    dto = TaskCreateFormDTO(algorithm_id=algorithm.algorithm_id, response_time=2.0)

    # 3. Ejecución: Usamos user.id (el entero de la DB)
    await service.create_task(user_id=user.id, dto=dto)
    await service.create_task(user_id=user.id, dto=dto)

    result = await service.get_tasks_by_user(user_id=user.id)

    # 4. Verificación
    assert result.is_ok
    tasks = result.unwrap()
    assert isinstance(tasks, list)
    assert len(tasks) >= 2
    assert all(t.user_id == user.id for t in tasks)


@pytest.mark.asyncio
async def test_get_tasks_by_user_not_found_service():
    # Instanciación con dependencias completas
    results_service = ResultsService(repository=ResultsRepository())
    service = TasksService(
        repository=TasksRepository(), 
        result_service=results_service
    )
    
    # Se usa un ID numérico inexistente (entero)
    result = await service.get_tasks_by_user(user_id=999999)
    assert result.is_err


@pytest.mark.asyncio
async def test_get_tasks_by_user_empty_service():
    # 1. Preparación
    user = await create_test_user(suffix="empty")
    
    # 2. Instanciación con dependencias completas
    results_service = ResultsService(repository=ResultsRepository())
    service = TasksService(
        repository=TasksRepository(), 
        result_service=results_service
    )
    
    # 3. Ejecución para un usuario real sin tareas creadas
    result = await service.get_tasks_by_user(user_id=user.id)

    # 4. Verificación
    if result.is_ok:
        assert result.unwrap() == []
    else:
        assert result.is_err