from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.documents import router as documents_router
from elastic.client import create_documents_index, es_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_documents_index()

    yield

    await es_client.close()


app = FastAPI(
    title="Document Search Service",
    lifespan=lifespan,
)

app.include_router(documents_router)
