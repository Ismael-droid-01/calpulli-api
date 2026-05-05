import os
from dotenv import load_dotenv

ENV_FILE_PATH = os.environ.get("CALPULLI_ENV_FILE_PATH", ".env")

if os.path.exists(ENV_FILE_PATH):
    load_dotenv(ENV_FILE_PATH)

CALPULLI_APP_TITLE               = os.environ.get("CALPULLI_APP_TITLE", "Calpulli: Privacy-Preserving Machine Learning Platform")
CALPULLI_APP_VERSION             = os.environ.get("CALPULLI_APP_VERSION", "0.1.0")
CALPULLI_APP_ORIGINS             = os.environ.get("CALPULLI_APP_ORIGINS", "http://localhost:4200").split(",")
CALPULLI_APP_CREDENTIALS         = os.environ.get("CALPULLI_APP_CREDENTIALS", "true").lower() == "true"
CALPULLI_APP_METHODS             = os.environ.get("CALPULLI_APP_METHODS", "*").split(",")
CALPULLI_APP_HEADERS             = os.environ.get("CALPULLI_APP_HEADERS", "*").split(",")
CALPULLI_DB_URL                  = os.environ.get("CALPULLI_DB_URL", "mysql://samuel_user:samuel_password@localhost:3306/calpulli_database")
CALPULLI_LOG_PATH                = os.environ.get("CALPULLI_LOG_PATH","./logs/")
CALPULLI_SCOPE                   = os.environ.get("CALPULLI_SCOPE", "calpulli")
CALPULLI_LOAD_BALANCING_STRATEGY = os.environ.get("CALPULLI_LOAD_BALANCING_STRATEGY", "round_robin")
CALPULLI_WORKERS_COUNT           = int(os.environ.get("CALPULLI_WORKERS", 4))
CALPULLI_WORKER_QUEUE_SIZE       = int(os.environ.get("CALPULLI_WORKER_QUEUE_SIZE", 100))
CALPULLI_DATASET_SINK_PATH       = os.environ.get("CALPULLI_DATASET_SINK_PATH", "/calpulli/datasets/")
XOLO_API_URL                     = os.environ.get("CALPULLI_XOLO_API_URL","http://localhost:10000/api/v4")
XOLO_SECRET_KEY                  = os.environ.get("XOLO_SECRET_KEY","default_secret_key")
RORY_HOSTNAME                    = os.environ.get("RORY_HOSTNAME", "localhost")
RORY_PORT                        = int(os.environ.get("RORY_PORT", 3001))
RORY_TIMEOUT                     = int(os.environ.get("RORY_TIMEOUT", 5))
XOLO_ACCOUNT_ID         = os.environ.get("XOLO_ACCOUNT_ID","calpulli-2eeaaade566b762cfaaa28e9a3318bc0")
XOLO_API_KEY            = os.environ.get("XOLO_API_KEY","XOLO_USERS_AG1Q9JDIBZ4_SJLYX4KQW5KLCHHSF1MPBRGZJCEINDW")
XOLO_ADMIN_TOKEN         = os.environ.get("XOLO_ADMIN_TOKEN","XOLO_USERS_AG1Q9JDIBZ4_SJLYX4KQW5KLCHHSF1MPBRGZJCEINDW")
