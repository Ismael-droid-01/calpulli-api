import pytest
from calpulli.models import Algorithm, AlgorithmType, StringParameter, StringParameterValue, Task, UserProfile


# --- Fixtures ---

@pytest.fixture
async def algorithm(client_with_before_and_after_clean):
    return await Algorithm.create(name="TestAlgoString", type=AlgorithmType.SUPERVISED)


@pytest.fixture
async def user(client_with_before_and_after_clean):
    return await UserProfile.create(
        user_id="user-456",
        username="testuser2",
        email="test2@test.com",
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
async def string_parameter(algorithm):
    return await StringParameter.create(
        algorithm=algorithm,
        name="kernel",
        default_value="rbf"
    )


# --- Tests ---

@pytest.mark.asyncio
async def test_create_string_value_valid(string_parameter, task):
    instance = StringParameterValue(
        parameter=string_parameter,
        task=task,
        value="linear"
    )
    await instance.save()
    assert instance.parameter_value_id is not None


@pytest.mark.asyncio
async def test_create_string_value_uses_default(string_parameter, task):
    instance = StringParameterValue(
        parameter=string_parameter,
        task=task,
        value=string_parameter.default_value
    )
    await instance.save()
    assert instance.value == "rbf"


@pytest.mark.asyncio
async def test_create_string_value_empty(string_parameter, task):
    instance = StringParameterValue(
        parameter=string_parameter,
        task=task,
        value=""
    )
    await instance.save()
    assert instance.parameter_value_id is not None


@pytest.mark.asyncio
async def test_create_string_value_max_length(string_parameter, task):
    long_value = "a" * 255
    instance = StringParameterValue(
        parameter=string_parameter,
        task=task,
        value=long_value
    )
    await instance.save()
    assert instance.parameter_value_id is not None


@pytest.mark.asyncio
async def test_create_string_value_exceeds_max_length(string_parameter, task):
    too_long = "a" * 256
    instance = StringParameterValue(
        parameter=string_parameter,
        task=task,
        value=too_long
    )
    with pytest.raises(Exception):
        await instance.save()


@pytest.mark.asyncio
async def test_create_multiple_values_same_parameter(string_parameter, task):
    for val in ["rbf", "linear", "poly"]:
        instance = StringParameterValue(
            parameter=string_parameter,
            task=task,
            value=val
        )
        await instance.save()
        assert instance.parameter_value_id is not None