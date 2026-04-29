import pytest
from calpulli.models import StringParameterValue
from tortoise.exceptions import ValidationError
pytestmark = pytest.mark.asyncio(scope="session")
# --- Tests ---

@pytest.mark.asyncio
async def test_create_string_value_valid(prepare_string_parameter_and_task):
    string_parameter, task = prepare_string_parameter_and_task
    instance = StringParameterValue(
        parameter = string_parameter,
        task      = task,
        value     = "linear"
    )
    await instance.save()
    assert instance.parameter_value_id is not None


@pytest.mark.asyncio
async def test_create_string_value_uses_default(prepare_string_parameter_and_task):
    string_parameter, task = prepare_string_parameter_and_task
    instance = StringParameterValue(
        parameter = string_parameter,
        task      = task,
        value     = string_parameter.default_value
    )
    await instance.save()
    assert instance.value == string_parameter.default_value


@pytest.mark.asyncio
async def test_create_string_value_empty(prepare_string_parameter_and_task):
    string_parameter, task = prepare_string_parameter_and_task
    instance = StringParameterValue(
        parameter = string_parameter,
        task      = task,
        value     = ""
    )
    await instance.save()
    assert instance.parameter_value_id is not None


@pytest.mark.asyncio
async def test_create_string_value_max_length(prepare_string_parameter_and_task):
    string_parameter, task = prepare_string_parameter_and_task
    long_value = "a" * 255
    instance = StringParameterValue(
        parameter = string_parameter,
        task      = task,
        value     = long_value
    )
    await instance.save()
    assert instance.parameter_value_id is not None


@pytest.mark.asyncio
async def test_create_string_value_exceeds_max_length(prepare_string_parameter_and_task):
    string_parameter, task = prepare_string_parameter_and_task
    too_long = "a" * 256
    instance = StringParameterValue(
        parameter = string_parameter,
        task      = task,
        value     = too_long
    )
    with pytest.raises(ValidationError):
        await instance.save()


@pytest.mark.asyncio
async def test_create_multiple_values_same_parameter(prepare_string_parameter_and_task):
    string_parameter, task = prepare_string_parameter_and_task
    for val in ["rbf", "linear", "poly"]:
        instance = StringParameterValue(
            parameter = string_parameter,
            task      = task,
            value     = val
        )
        await instance.save()
        assert instance.parameter_value_id is not None