import os
from dotenv import load_dotenv

ENV_FILE_PATH = os.environ.get("CALPULLI_ENV_FILE_PATH", ".env")

if os.path.exists(ENV_FILE_PATH):
    load_dotenv(ENV_FILE_PATH)

CALPULLI_APP_TITLE       = os.environ.get("CALPULLI_APP_TITLE", "Calpulli: Privacy-Preserving Machine Learning Platform")
CALPULLI_APP_VERSION     = os.environ.get("CALPULLI_APP_VERSION", "0.1.0")
CALPULLI_APP_ORIGINS     = os.environ.get("CALPULLI_APP_ORIGINS", "http://localhost:4200").split(",")
CALPULLI_APP_CREDENTIALS = os.environ.get("CALPULLI_APP_CREDENTIALS", "true").lower() == "true"
CALPULLI_APP_METHODS     = os.environ.get("CALPULLI_APP_METHODS", "*").split(",")
CALPULLI_APP_HEADERS     = os.environ.get("CALPULLI_APP_HEADERS", "*").split(",")
CALPULLI_DB_URL          = os.environ.get("CALPULLI_DB_URL", "mysql://samuel_user:samuel_password@localhost:3306/calpulli_database")
CALPULLI_LOG_PATH       = os.environ.get("CALPULLI_LOG_PATH","./logs/")
CALPULLI_SCOPE  = os.environ.get("CALPULLI_SCOPE", "calpulli")
XOLO_API_URL    = os.environ.get("XOLO_API_URL","http://localhost:10000/api/v4")
XOLO_SECRET_KEY = os.environ.get("XOLO_SECRET_KEY","default_secret_key")