from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database.db import init_db

from app.api.router_page import router as router_page
from app.api.router_socket import router as router_socket
from app.api.router_tasks import router as router_tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.mount('/static', StaticFiles(directory='app/static'), 'static')

app.include_router(router_page)
app.include_router(router_socket)
app.include_router(router_tasks)

