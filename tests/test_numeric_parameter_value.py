import pytest
from calpulli.models import Algorithm, AlgorithmType, NumericParameter, NumericParameterType, NumericParameterValue, Task, UserProfile


# --- Fixtures ---

@pytest.fixture
async def algorithm(clean_database):
    return await Algorithm.create(name="TestAlgo", type=AlgorithmType.SUPERVISED)


@pytest.fixture
async def user(clean_database):
    return await UserProfile.create(
        user_id="user-123",
        username="testuser",
        email="test@test.com",
        first_name="Test",
        last_name="User"
    )


@pytest.fixture
async def task(algorithm, user):
    return await Task.create(
        algorithm=algorithm,
        user=user,
        response_time=0.0
    )


@pytest.fixture
async def float_parameter(algorithm):
    return await NumericParameter.create(
        algorithm=algorithm,
        name="learning_rate",
        type=NumericParameterType.FLOAT,
        default_value=0.01,
        max_value=1.0
    )


@pytest.fixture
async def integer_parameter(algorithm):
    return await NumericParameter.create(
        algorithm=algorithm,
        name="n_estimators",
        type=NumericParameterType.INTEGER,
        default_value=100,
        max_value=500
    )


@pytest.fixture
async def boolean_parameter(algorithm):
    return await NumericParameter.create(
        algorithm=algorithm,
        name="use_bias",
        type=NumericParameterType.BOOLEAN,
        default_value=0,
        max_value=1
    )


# --- Tests FLOAT ---

@pytest.mark.asyncio
async def test_create_float_value_valid(float_parameter, task):
    instance = NumericParameterValue(
        parameter=float_parameter,
        task=task,
        value=0.5
    )
    await instance.save()
    assert instance.parameter_value_id is not None


@pytest.mark.asyncio
async def test_create_float_value_exceeds_max(float_parameter, task):
    with pytest.raises(ValueError, match="max_value"):
        await NumericParameterValue(
            parameter=float_parameter,
            task=task,
            value=2.0
        ).save()


# --- Tests INTEGER ---

@pytest.mark.asyncio
async def test_create_integer_value_valid(integer_parameter, task):
    instance = NumericParameterValue(
        parameter=integer_parameter,
        task=task,
        value=200
    )
    await instance.save()
    assert instance.parameter_value_id is not None


@pytest.mark.asyncio
async def test_create_integer_value_not_integer(integer_parameter, task):
    with pytest.raises(ValueError, match="integer"):
        await NumericParameterValue(
            parameter=integer_parameter,
            task=task,
            value=3.7
        ).save()


@pytest.mark.asyncio
async def test_create_integer_value_exceeds_max(integer_parameter, task):
    with pytest.raises(ValueError, match="max_value"):
        await NumericParameterValue(
            parameter=integer_parameter,
            task=task,
            value=999
        ).save()


# --- Tests BOOLEAN ---

@pytest.mark.asyncio
async def test_create_boolean_value_valid_zero(boolean_parameter, task):
    instance = NumericParameterValue(
        parameter=boolean_parameter,
        task=task,
        value=0.0
    )
    await instance.save()
    assert instance.parameter_value_id is not None


@pytest.mark.asyncio
async def test_create_boolean_value_valid_one(boolean_parameter, task):
    instance = NumericParameterValue(
        parameter=boolean_parameter,
        task=task,
        value=1.0
    )
    await instance.save()
    assert instance.parameter_value_id is not None


@pytest.mark.asyncio
async def test_create_boolean_value_invalid(boolean_parameter, task):
    with pytest.raises(ValueError, match="BOOLEAN"):
        await NumericParameterValue(
            parameter=boolean_parameter,
            task=task,
            value=5.0
        ).save()