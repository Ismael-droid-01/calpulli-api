import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from tortoise import Tortoise
from ppml.server import app
from ppml.dtos import AlgorithmCreateFormDTO, NumericParameterCreateFormDTO

@pytest.fixture(scope="function")
async def algorithm_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = AlgorithmCreateFormDTO(name="TestAlgoForParams", type="regression").model_dump()
        response = await client.post("/algorithms", json=payload)
        assert response.status_code == 200
        return response.json()["algorithm_id"]


@pytest.mark.asyncio
async def test_create_numeric_parameter_endpoint(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = NumericParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="learning_rate",
            type="FLOAT",
            default_value=0.01,
            max_value=1.0
        ).model_dump()
        response = await client.post("/numeric-parameters", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "learning_rate"
        assert data["type"] == "FLOAT"
        assert data["default_value"] == 0.01
        assert data["max_value"] == 1.0
        assert data["algorithm_id"] == algorithm_id
        assert "parameter_id" in data


@pytest.mark.asyncio
async def test_get_numeric_parameter_by_id_endpoint(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = NumericParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="max_depth",
            type="INTEGER",
            default_value=5,
            max_value=100
        ).model_dump()
        create_response = await client.post("/numeric-parameters", json=payload)
        assert create_response.status_code == 200
        parameter_id = create_response.json()["parameter_id"]

        response = await client.get(f"/numeric-parameters/{parameter_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["parameter_id"] == parameter_id
        assert data["name"] == "max_depth"
        assert data["type"] == "INTEGER"


@pytest.mark.asyncio
async def test_get_numeric_parameter_by_id_not_found_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/numeric-parameters/999999")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_numeric_parameter_endpoint(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = NumericParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="n_eEstimators",
            type="INTEGER",
            default_value=100,
            max_value=500
        ).model_dump()
        create_response = await client.post("/numeric-parameters", json=payload)
        assert create_response.status_code == 200
        parameter_id = create_response.json()["parameter_id"]

        updated_payload = NumericParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="n_estimators",
            type="INTEGER",
            default_value=200,
            max_value=1000
        ).model_dump()
        response = await client.put(f"/numeric-parameters/{parameter_id}", json=updated_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["default_value"] == 200
        assert data["max_value"] == 1000


@pytest.mark.asyncio
async def test_update_numeric_parameter_not_found_endpoint(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = NumericParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="ghost_param",
            type="FLOAT",
            default_value=0.0,
            max_value=1.0
        ).model_dump()
        response = await client.put("/numeric-parameters/999999", json=payload)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_numeric_parameter_endpoint(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = NumericParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="to_delete",
            type="FLOAT",
            default_value=0.5,
            max_value=1.0
        ).model_dump()
        create_response = await client.post("/numeric-parameters", json=payload)
        assert create_response.status_code == 200
        parameter_id = create_response.json()["parameter_id"]

        response = await client.delete(f"/numeric-parameters/{parameter_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Numeric parameter deleted successfully."

        get_response = await client.get(f"/numeric-parameters/{parameter_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_numeric_parameter_not_found_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete("/numeric-parameters/999999")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_numeric_parameter_boolean_valid(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = NumericParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="is_enabled",
            type="BOOLEAN",
            default_value=0,
            max_value=1
        ).model_dump()
        response = await client.post("/numeric-parameters", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "BOOLEAN"
        assert data["default_value"] == 0.0
        assert data["max_value"] == 1.0


@pytest.mark.asyncio
async def test_create_numeric_parameter_boolean_invalid(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = NumericParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="bad_boolean",
            type="BOOLEAN",
            default_value=5,   # inválido
            max_value=1
        ).model_dump()
        response = await client.post("/numeric-parameters", json=payload)
        assert response.status_code == 422  # o 400, según cómo manejes el ValueError en tu router


@pytest.mark.asyncio
async def test_create_numeric_parameter_integer_valid(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = NumericParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="n_layers",
            type="INTEGER",
            default_value=3,
            max_value=10
        ).model_dump()
        response = await client.post("/numeric-parameters", json=payload)
        assert response.status_code == 200
        assert response.json()["type"] == "INTEGER"


@pytest.mark.asyncio
async def test_create_numeric_parameter_integer_invalid(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = NumericParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="bad_int",
            type="INTEGER",
            default_value=3.7,  # inválido
            max_value=10
        ).model_dump()
        response = await client.post("/numeric-parameters", json=payload)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_numeric_parameter_invalid_type(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "algorithm_id": algorithm_id,
            "name": "bad_type",
            "type": "INVALID_TYPE",   # valor fuera del enum
            "default_value": 1.0,
            "max_value": 10.0
        }
        response = await client.post("/numeric-parameters", json=payload)
        assert response.status_code == 422