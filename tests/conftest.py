import os
from dotenv import load_dotenv

def pytest_configure(config):
    if os.path.exists(".env.test"):
        load_dotenv(dotenv_path=".env.test")