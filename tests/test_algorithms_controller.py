import pytest
from calpulli.dtos import AlgorithmCreateFormDTO, NumericParameterCreateFormDTO, StringParameterCreateFormDTO

@pytest.mark.asyncio
async def test_create_algorithm_endpoint(controller_client):
    payload = AlgorithmCreateFormDTO(name="DecisionTree", type="SUPERVISED").model_dump()
    response = await controller_client.post("/algorithms", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "DecisionTree"
    assert data["type"] == "SUPERVISED"
    assert "algorithm_id" in data

@pytest.mark.asyncio
async def test_create_algorithm_duplicate_endpoint(controller_client):
    payload = AlgorithmCreateFormDTO(name="DuplicateAlgo", type="UNSUPERVISED").model_dump()
    first = await controller_client.post("/algorithms", json=payload)
    assert first.status_code == 200
    second = await controller_client.post("/algorithms", json=payload)
    assert second.status_code == 500

@pytest.mark.asyncio
async def test_get_all_algorithms_endpoint(controller_client):
    payload = AlgorithmCreateFormDTO(name="NaiveBayes", type="SUPERVISED").model_dump()
    await controller_client.post("/algorithms", json=payload)
    response = await controller_client.get("/algorithms/list")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all("algorithm_id" in alg for alg in data)

@pytest.mark.asyncio
async def test_get_algorithm_by_id_endpoint(controller_client):
    payload = AlgorithmCreateFormDTO(name="RandomForest", type="SUPERVISED").model_dump()
    create_response = await controller_client.post("/algorithms", json=payload)
    assert create_response.status_code == 200
    algorithm_id = create_response.json()["algorithm_id"]
    
    response = await controller_client.get(f"/algorithms/{algorithm_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["algorithm_id"] == algorithm_id
    assert data["name"] == "RandomForest"

@pytest.mark.asyncio
async def test_get_algorithm_by_id_not_found_endpoint(controller_client):
    response = await controller_client.get("/algorithms/999999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_algorithms_by_type_endpoint(controller_client):
    payload = AlgorithmCreateFormDTO(name="GradientBoosting", type="UNSUPERVISED").model_dump()
    await controller_client.post("/algorithms", json=payload)
    response = await controller_client.get("/algorithms/type/UNSUPERVISED")
    assert response.status_code == 200
    data = response.json()
    assert all(alg["type"] == "UNSUPERVISED" for alg in data)

@pytest.mark.asyncio
async def test_get_algorithms_by_type_not_found_endpoint(controller_client):
    response = await controller_client.get("/algorithms/type/nonexistent_type")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_algorithm_endpoint(controller_client):
    payload = AlgorithmCreateFormDTO(name="OldName", type="UNSUPERVISED").model_dump()
    create_res = await controller_client.post("/algorithms", json=payload)
    algorithm_id = create_res.json()["algorithm_id"]
    
    updated_payload = AlgorithmCreateFormDTO(name="NewName", type="SUPERVISED").model_dump()
    response = await controller_client.put(f"/algorithms/{algorithm_id}", json=updated_payload)
    assert response.status_code == 200
    assert response.json()["name"] == "NewName"

@pytest.mark.asyncio
async def test_update_algorithm_not_found_endpoint(controller_client):
    payload = AlgorithmCreateFormDTO(name="Ghost", type="UNSUPERVISED").model_dump()
    response = await controller_client.put("/algorithms/999999", json=payload)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_algorithm_endpoint(controller_client):
    payload = AlgorithmCreateFormDTO(name="ToDelete", type="SUPERVISED").model_dump()
    create_res = await controller_client.post("/algorithms", json=payload)
    algorithm_id = create_res.json()["algorithm_id"]
    
    response = await controller_client.delete(f"/algorithms/{algorithm_id}")
    assert response.status_code == 200
    
    get_response = await controller_client.get(f"/algorithms/{algorithm_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_get_algorithm_parameters_endpoint(controller_client):
    algo_payload = AlgorithmCreateFormDTO(name="SVMAlgo", type="SUPERVISED").model_dump()
    create_res = await controller_client.post("/algorithms", json=algo_payload)
    algorithm_id = create_res.json()["algorithm_id"]

    await controller_client.post("/numeric-parameters", json=NumericParameterCreateFormDTO(
        algorithm_id=algorithm_id, name="C", type="FLOAT", default_value=1.0, max_value=10.0
    ).model_dump())

    await controller_client.post("/string-parameters", json=StringParameterCreateFormDTO(
        algorithm_id=algorithm_id, name="kernel", default_value="rbf"
    ).model_dump())

    response = await controller_client.get(f"/algorithms/{algorithm_id}/parameters")
    assert response.status_code == 200
    data = response.json()
    assert len(data["numeric_parameters"]) == 1
    assert data["numeric_parameters"][0]["name"] == "C"

@pytest.mark.asyncio
async def test_get_algorithm_parameters_not_found_endpoint(controller_client):
    response = await controller_client.get("/algorithms/999999/parameters")
    assert response.status_code == 404