import os
from dotenv import load_dotenv

ENV_FILE_PATH = os.environ.get("PPML_ENV_FILE_PATH", ".env")

if os.path.exists(ENV_FILE_PATH):
    load_dotenv(ENV_FILE_PATH)

APP_TITLE       = os.environ.get("PPML_APP_TITLE", "Preprocess Server")
APP_VERSION     = os.environ.get("PPML_APP_VERSION", "0.1.0")
APP_ORIGINS     = os.environ.get("PPML_APP_ORIGINS", "http://localhost:4200").split(",")
APP_CREDENTIALS = os.environ.get("PPML_APP_CREDENTIALS", "true").lower() == "true"
APP_METHODS     = os.environ.get("PPML_APP_METHODS", "*").split(",")
APP_HEADERS     = os.environ.get("PPML_APP_HEADERS", "*").split(",")
DB_URL          = os.environ.get("PPML_DB_URL", "mysql://samuel_user:samuel_password@localhost:3306/ppml_database")
XOLO_API_URL    = os.environ.get("PPML_XOLO_API_URL","http://localhost:10000/api/v4")
XOLO_SECRET_KEY = os.environ.get("PPML_XOLO_SECRET_KEY","default_secret_key")
LOG_PATH       = os.environ.get("PPML_LOG_PATH","./logs/")