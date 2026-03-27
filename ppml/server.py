from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import ppml.config as Cfg
from ppml.controllers import ppml_router,users_profile_router
from tortoise import Tortoise
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print("Starting up...")
    await Tortoise.init(
        db_url=Cfg.DB_URL,
        modules={"models": ["ppml.models"]},
    )
    await Tortoise.generate_schemas()
    yield
    # Shutdown code
    await Tortoise.close_connections()
    print("Shutting down...")



app = FastAPI(
    title   = Cfg.APP_TITLE,
    version = Cfg.APP_VERSION,
    lifespan=lifespan
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
