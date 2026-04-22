import pytest
from calpulli.models import UserProfile
from calpulli.repositories import ResultsRepository
from tests.conftest import create_test_task, register_and_login_user

@pytest.mark.asyncio
async def test_get_result_endpoint_success(get_user_clean_and_get_client, task, algorithm):
    user_dto, client = get_user_clean_and_get_client
    headers = {
        "Authorization": f"Bearer {user_dto.access_token}", 
        "Temporal-Secret-Key": user_dto.temporal_secret
    }

    user_profile = await UserProfile.get(username=user_dto.username)
    
    task = await create_test_task(
        user_id=user_profile.id,
        algorithm_id=algorithm.algorithm_id
    )
    
    repo = ResultsRepository()
    res_created = await repo.create(
        task_id=task.task_id, 
        format="json", 
        url="http://storage.com/res.json"
    )
    result_id = res_created.unwrap().result_id

    response = await client.get(f"/results/{result_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["result_id"] == result_id
    assert data["format"] == "json"

@pytest.mark.asyncio
async def test_get_result_endpoint_not_owned(get_user_clean_and_get_client, algorithm):
    user_a_dto, client = get_user_clean_and_get_client
    
    user_a_profile = await UserProfile.get(username=user_a_dto.username)
    
    task_a = await create_test_task(
        user_id=user_a_profile.id, 
        algorithm_id=algorithm.algorithm_id
    )
    
    repo = ResultsRepository()
    res_created = await repo.create(
        task_id=task_a.task_id, 
        format="csv", 
        url="http://b.com"
    )
    result_id = res_created.unwrap().result_id

    user_b_dto = await register_and_login_user(client, "userB")
    
    headers_b = {
        "Authorization": f"Bearer {user_b_dto.access_token}", 
        "Temporal-Secret-Key": user_b_dto.temporal_secret
    }
    
    response = await client.get(f"/results/{result_id}", headers=headers_b)
    
    assert response.status_code == 404

from calpulli.models import UserProfile
from calpulli.repositories import ResultsRepository
from tests.conftest import create_test_task

@pytest.mark.asyncio
async def test_delete_result_endpoint_success(get_user_clean_and_get_client, algorithm):
    user_dto, client = get_user_clean_and_get_client
    headers = {
        "Authorization": f"Bearer {user_dto.access_token}", 
        "Temporal-Secret-Key": user_dto.temporal_secret
    }

    user_profile = await UserProfile.get(username=user_dto.username)

    task = await create_test_task(
        user_id=user_profile.id, 
        algorithm_id=algorithm.algorithm_id
    )

    repo = ResultsRepository()
    res = await repo.create(task_id=task.task_id, format="json", url="http://del.json")
    result_id = res.unwrap().result_id

    response = await client.delete(f"/results/{result_id}", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Result deleted successfully."

@pytest.mark.asyncio
async def test_delete_result_unauthorized(get_user_clean_and_get_client, algorithm):
    user_a_dto, client = get_user_clean_and_get_client

    user_a_profile = await UserProfile.get(username=user_a_dto.username)

    task_a = await create_test_task(
        user_id=user_a_profile.id,
        algorithm_id=algorithm.algorithm_id
    )
    
    repo = ResultsRepository()
    res = await repo.create(task_id=task_a.task_id, format="json", url="http://safe.json")
    result_id = res.unwrap().result_id

    user_b_dto = await register_and_login_user(client, "hacker")
    headers_b = {
        "Authorization": f"Bearer {user_b_dto.access_token}", 
        "Temporal-Secret-Key": user_b_dto.temporal_secret
    }
    
    response = await client.delete(f"/results/{result_id}", headers=headers_b)
    
    assert response.status_code == 404