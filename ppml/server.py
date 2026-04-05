from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import ppml.config as Cfg
from ppml.controllers import ppml_router,users_profile_router, algorithms_router, numeric_parameters_router
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    yield
    print("Shutting down...")





app = FastAPI(
    title   = Cfg.APP_TITLE,
    version = Cfg.APP_VERSION,
    lifespan=lifespan
)
register_tortoise(
    app,
    db_url=Cfg.DB_URL,
    modules={"models": ["ppml.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = Cfg.APP_ORIGINS,
    allow_credentials = Cfg.APP_CREDENTIALS,
    allow_methods     = Cfg.APP_METHODS,
    allow_headers     = Cfg.APP_HEADERS,
)

app.include_router(ppml_router,tags=["ppml"])
app.include_router(users_profile_router,tags=["users_profile"])
app.include_router(algorithms_router,tags=["algorithms"])
app.include_router(numeric_parameters_router,tags=["numeric_parameters"])