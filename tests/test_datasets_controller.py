import io
import pytest
from httpx import AsyncClient, ASGITransport
from calpulli.server import app
from calpulli.dtos import AlgorithmCreateFormDTO

@pytest.mark.asyncio
async def test_upload_dataset_endpoint(get_user_clean_and_get_client):
    user, client = get_user_clean_and_get_client
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}

    file_content = b"col1,col2\n1,2\n3,4"
    file = {"file": ("customers.csv", io.BytesIO(file_content), "text/csv")}

    response = await client.post("/datasets", files=file, headers=headers)
    assert response.status_code == 200, response.json()
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "customers"
    assert data["extension"] == "csv"
    assert "dataset_id" in data


@pytest.mark.asyncio
async def test_upload_dataset_duplicate_endpoint(get_user_clean_and_get_client):
    user, client = get_user_clean_and_get_client
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}

    file_content = b"col1,col2\n1,2"
    file = {"file": ("duplicate.csv", io.BytesIO(file_content), "text/csv")}

    first = await client.post("/datasets", files=file, headers=headers)
    assert first.status_code == 200

    file = {"file": ("duplicate.csv", io.BytesIO(file_content), "text/csv")}
    second = await client.post("/datasets", files=file, headers=headers)
    assert second.status_code == 500


@pytest.mark.asyncio
async def test_get_user_datasets_endpoint(get_user_clean_and_get_client):
    user, client = get_user_clean_and_get_client
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}

    for filename in ["dataset_a.csv", "dataset_b.json"]:
        name, ext = filename.rsplit(".", 1)
        file = {"file": (filename, io.BytesIO(b"data"), "application/octet-stream")}
        await client.post("/datasets", files=file, headers=headers)

    response = await client.get("/datasets", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert all("dataset_id" in d for d in data)
    assert all("name" in d for d in data)
    assert all("extension" in d for d in data)


@pytest.mark.asyncio
async def test_get_user_datasets_only_own(get_user_clean_and_get_client):
    user, client = get_user_clean_and_get_client
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}

    file = {"file": ("mydata.csv", io.BytesIO(b"data"), "text/csv")}
    await client.post("/datasets", files=file, headers=headers)

    response = await client.get("/datasets", headers=headers)
    data = response.json()
    assert all(d["name"] != "other_user_data" for d in data)


@pytest.mark.asyncio
async def test_delete_dataset_endpoint(get_user_clean_and_get_client):
    user, client = get_user_clean_and_get_client
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}

    file = {"file": ("to_delete.csv", io.BytesIO(b"data"), "text/csv")}
    create_response = await client.post("/datasets", files=file, headers=headers)
    assert create_response.status_code == 200
    dataset_id = create_response.json()["dataset_id"]

    response = await client.delete(f"/datasets/{dataset_id}", headers=headers)
    assert response.status_code == 200, response.json()
    assert response.status_code == 200
    assert response.json()["message"] == "Dataset deleted successfully"


@pytest.mark.asyncio
async def test_delete_dataset_not_found_endpoint(get_user_clean_and_get_client):
    user, client = get_user_clean_and_get_client
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}

    response = await client.delete("/datasets/999999", headers=headers)
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_get_datasets_empty_endpoint(get_user_clean_and_get_client):
    user, client = get_user_clean_and_get_client
    headers = {"Authorization": f"Bearer {user.access_token}", "Temporal-Secret-Key": user.temporal_secret}

    response = await client.get("/datasets", headers=headers)
    assert response.status_code == 200
    assert response.json() == []