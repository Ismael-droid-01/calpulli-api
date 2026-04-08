
import asyncio
import os
from dotenv import load_dotenv
import pymysql
import pytest
from tortoise import Tortoise
from tortoise.contrib.test import tortoise_test_context
from ppml.models import Task, UserProfile, Algorithm, NumericParameter, StringParameter

DATABASE_NAME = "ppml_database"
USER= "samuel_user"
PASSWORD = "samuel_password"
TEST_DB_URL = f"mysql://{USER}:{PASSWORD}@localhost:3306/{DATABASE_NAME}" 


def pytest_configure(config):
    if os.path.exists(".env.test"):
        load_dotenv(dotenv_path=".env.test")

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True, scope="session")
async def initialize_tests():
    # Setup: Initialize Tortoise with your models
    connection = pymysql.connect(host='localhost', user=USER, password=PASSWORD)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {DATABASE_NAME}")
    finally:
        connection.close()
    async with tortoise_test_context(
        db_url=TEST_DB_URL, 
        modules=['ppml.models'],

    ) as ctx:
        await Tortoise.generate_schemas()
        yield ctx

@pytest.fixture(autouse=True)
async def clean_database():
    await _clean()
    yield
    await _clean()

async def _clean():
    await Task.all().delete()         
    await NumericParameter.all().delete()
    await StringParameter.all().delete()
    await Algorithm.all().delete()    
    await UserProfile.all().delete()