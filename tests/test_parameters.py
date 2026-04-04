import asyncio
import pytest
from tortoise import Tortoise
from ppml.dtos import AlgorithmCreateFormDTO, NumericParameterCreateFormDTO, StringParameterCreateFormDTO
from ppml.repositories import AlgorithmsRepository, NumericParametersRepository, StringParametersRepository
from ppml.services import AlgorithmsService, NumericParametersService, StringParametersService

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
async def test_create_numeric_parameter_service():
    algo_repo = AlgorithmsRepository()
    algo_service = AlgorithmsService(repository=algo_repo)

    algo_result = await algo_service.create_algorithm(AlgorithmCreateFormDTO(
        name="NaiveBayes",
        type="classification"
    ))
    assert algo_result.is_ok
    algorithm_id = algo_result.unwrap().algorithm_id

    repo = NumericParametersRepository()
    service = NumericParametersService(repository=repo)

    result = await service.create_numeric_parameter(NumericParameterCreateFormDTO(
        algorithm_id    = algorithm_id,
        name            = "learning_rate",
        type            = "float",
        default_value   = 0.01,
        max_value       = 1.0
    ))

    assert result.is_ok
    parameter = result.unwrap()
    assert parameter.name           == "learning_rate"
    assert parameter.algorithm_id   == algorithm_id
    assert parameter.default_value  == 0.01
    assert parameter.max_value      == 1.0


@pytest.mark.asyncio
async def test_create_numeric_parameter_invalid_algorithm_service():
    repo = NumericParametersRepository()
    service = NumericParametersService(repository=repo)

    result = await service.create_numeric_parameter(NumericParameterCreateFormDTO(
        algorithm_id    = 999999,
        name            = "learning_rate",
        type            = "float",
        default_value   = 0.01,
        max_value       = 1.0
    ))

    assert result.is_err


@pytest.mark.asyncio
async def test_get_numeric_parameters_by_algorithm_id_service():
    algo_repo = AlgorithmsRepository()
    algo_service = AlgorithmsService(repository=algo_repo)

    algo_result = await algo_service.create_algorithm(AlgorithmCreateFormDTO(
        name="KNN",
        type="classification"
    ))
    assert algo_result.is_ok
    algorithm_id = algo_result.unwrap().algorithm_id

    repo = NumericParametersRepository()
    service = NumericParametersService(repository=repo)

    await service.create_numeric_parameter(NumericParameterCreateFormDTO(
        algorithm_id    = algorithm_id,
        name            = "n_neighbors",
        type            = "int",
        default_value   = 5.0,
        max_value       = 100.0
    ))

    result = await service.get_numeric_parameters_by_algorithm_id(algorithm_id=algorithm_id)

    assert result.is_ok
    parameters = result.unwrap()
    assert isinstance(parameters, list)
    assert len(parameters) > 0
    assert all(hasattr(p, "parameter_id")   for p in parameters)
    assert all(hasattr(p, "algorithm_id")   for p in parameters)
    assert all(hasattr(p, "name")           for p in parameters)
    assert all(hasattr(p, "default_value")  for p in parameters)
    assert all(hasattr(p, "max_value")      for p in parameters)


@pytest.mark.asyncio
async def test_get_numeric_parameters_by_invalid_algorithm_id_service():
    repo = NumericParametersRepository()
    service = NumericParametersService(repository=repo)

    result = await service.get_numeric_parameters_by_algorithm_id(algorithm_id=999999)

    assert result.is_err

@pytest.mark.asyncio
async def test_create_string_parameter_service():
    algo_repo = AlgorithmsRepository()
    algo_service = AlgorithmsService(repository=algo_repo)

    algo_result = await algo_service.create_algorithm(AlgorithmCreateFormDTO(
        name="XGBoost",
        type="classification"
    ))
    assert algo_result.is_ok
    algorithm_id = algo_result.unwrap().algorithm_id

    repo = StringParametersRepository()
    service = StringParametersService(repository=repo)

    result = await service.create_string_parameter(StringParameterCreateFormDTO(
        algorithm_id    = algorithm_id,
        name            = "criterion",
        type            = "string",
        default_value   = "gini"
    ))

    assert result.is_ok
    parameter = result.unwrap()
    assert parameter.name           == "criterion"
    assert parameter.algorithm_id   == algorithm_id
    assert parameter.default_value  == "gini"


@pytest.mark.asyncio
async def test_create_string_parameter_invalid_algorithm_service():
    repo = StringParametersRepository()
    service = StringParametersService(repository=repo)

    result = await service.create_string_parameter(StringParameterCreateFormDTO(
        algorithm_id    = 999999,
        name            = "criterion",
        type            = "string",
        default_value   = "gini"
    ))

    assert result.is_err


@pytest.mark.asyncio
async def test_get_string_parameters_by_algorithm_id_service():
    algo_repo = AlgorithmsRepository()
    algo_service = AlgorithmsService(repository=algo_repo)

    algo_result = await algo_service.create_algorithm(AlgorithmCreateFormDTO(
        name="AdaBoost",
        type="classification"
    ))
    assert algo_result.is_ok
    algorithm_id = algo_result.unwrap().algorithm_id

    repo = StringParametersRepository()
    service = StringParametersService(repository=repo)

    await service.create_string_parameter(StringParameterCreateFormDTO(
        algorithm_id    = algorithm_id,
        name            = "loss",
        type            = "string",
        default_value   = "linear"
    ))

    result = await service.get_string_parameters_by_algorithm_id(algorithm_id=algorithm_id)

    assert result.is_ok
    parameters = result.unwrap()
    assert isinstance(parameters, list)
    assert len(parameters) > 0
    assert all(hasattr(p, "parameter_id")   for p in parameters)
    assert all(hasattr(p, "algorithm_id")   for p in parameters)
    assert all(hasattr(p, "name")           for p in parameters)
    assert all(hasattr(p, "default_value")  for p in parameters)


@pytest.mark.asyncio
async def test_get_string_parameters_by_invalid_algorithm_id_service():
    repo = StringParametersRepository()
    service = StringParametersService(repository=repo)

    result = await service.get_string_parameters_by_algorithm_id(algorithm_id=999999)

    assert result.is_err