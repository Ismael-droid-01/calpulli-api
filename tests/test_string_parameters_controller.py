import pytest
from httpx import AsyncClient, ASGITransport
from calpulli.server import app
from calpulli.dtos import AlgorithmCreateFormDTO, StringParameterCreateFormDTO

@pytest.fixture(scope="function")
async def algorithm_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = AlgorithmCreateFormDTO(name="TestAlgoForStringParams", type="SUPERVISED").model_dump()
        response = await client.post("/algorithms", json=payload)
        assert response.status_code == 200
        return response.json()["algorithm_id"]


@pytest.mark.asyncio
async def test_create_string_parameter_endpoint(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = StringParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="kernel",
            default_value="rbf"
        ).model_dump()
        response = await client.post("/string-parameters", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "kernel"
        assert data["default_value"] == "rbf"
        assert data["algorithm_id"] == algorithm_id
        assert "parameter_id" in data


@pytest.mark.asyncio
async def test_get_string_parameter_by_id_endpoint(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = StringParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="criterion",
            default_value="gini"
        ).model_dump()
        create_response = await client.post("/string-parameters", json=payload)
        assert create_response.status_code == 200
        parameter_id = create_response.json()["parameter_id"]

        response = await client.get(f"/string-parameters/{parameter_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["parameter_id"] == parameter_id
        assert data["name"] == "criterion"
        assert data["default_value"] == "gini"


@pytest.mark.asyncio
async def test_get_string_parameter_by_id_not_found_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/string-parameters/999999")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_string_parameter_endpoint(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = StringParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="solver",
            default_value="lbfgs"
        ).model_dump()
        create_response = await client.post("/string-parameters", json=payload)
        assert create_response.status_code == 200
        parameter_id = create_response.json()["parameter_id"]

        updated_payload = StringParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="solver",
            default_value="adam"
        ).model_dump()
        response = await client.put(f"/string-parameters/{parameter_id}", json=updated_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "solver"
        assert data["default_value"] == "adam"


@pytest.mark.asyncio
async def test_update_string_parameter_not_found_endpoint(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = StringParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="ghost_param",
            default_value="none"
        ).model_dump()
        response = await client.put("/string-parameters/999999", json=payload)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_string_parameter_endpoint(algorithm_id):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = StringParameterCreateFormDTO(
            algorithm_id=algorithm_id,
            name="to_delete",
            default_value="value"
        ).model_dump()
        create_response = await client.post("/string-parameters", json=payload)
        assert create_response.status_code == 200
        parameter_id = create_response.json()["parameter_id"]

        response = await client.delete(f"/string-parameters/{parameter_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "String parameter deleted successfully."

        get_response = await client.get(f"/string-parameters/{parameter_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_string_parameter_not_found_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete("/string-parameters/999999")
        assert response.status_code == 404