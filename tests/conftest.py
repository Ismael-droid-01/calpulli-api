import asyncio
import os
from dotenv import load_dotenv
import pytest
from tortoise import Tortoise

from ppml.models import UserProfile, Algorithm, NumericParameter, StringParameter

def pytest_configure(config):
    if os.path.exists(".env.test"):
        load_dotenv(dotenv_path=".env.test")

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

@pytest.fixture(autouse=True)
async def clean_database():
    await StringParameter.all().delete()
    await NumericParameter.all().delete()
    await Algorithm.all().delete()
    await UserProfile.all().delete()  
    yield
    await StringParameter.all().delete()
    await NumericParameter.all().delete()
    await Algorithm.all().delete()
    await UserProfile.all().delete()