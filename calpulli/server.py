from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import calpulli.config as Cfg
from calpulli.controllers import calpulli_routers,users_profile_router, algorithms_router, numeric_parameters_router, string_parameters_router, tasks_router, results_router
from tortoise.contrib.fastapi import register_tortoise
from contextlib import asynccontextmanager

from calpulli.core.worker.consumer import TaskConsumer




@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    task_consumer = TaskConsumer(n_workers=Cfg.CALPULLI_WORKERS_COUNT, max_queue_size=Cfg.CALPULLI_WORKER_QUEUE_SIZE)
    app.state.task_consumer = task_consumer

    await app.state.task_consumer.start()
    yield
    print("Shutting down...")
    await app.state.task_consumer.stop()





app = FastAPI(
    title   = Cfg.CALPULLI_APP_TITLE,
    version = Cfg.CALPULLI_APP_VERSION,
    lifespan=lifespan
)
register_tortoise(
    app,
    db_url=Cfg.CALPULLI_DB_URL,
    modules={"models": ["calpulli.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = Cfg.CALPULLI_APP_ORIGINS,
    allow_credentials = Cfg.CALPULLI_APP_CREDENTIALS,
    allow_methods     = Cfg.CALPULLI_APP_METHODS,
    allow_headers     = Cfg.CALPULLI_APP_HEADERS,
)

app.include_router(calpulli_routers,tags=["calpulli"])
app.include_router(users_profile_router,tags=["users_profile"])
app.include_router(algorithms_router,tags=["algorithms"])
app.include_router(numeric_parameters_router,tags=["numeric_parameters"])
app.include_router(string_parameters_router, tags=["string_parameters"])
app.include_router(tasks_router, tags=["tasks"])
app.include_router(results_router, tags=["results"])