from datetime import datetime

from elasticsearch import AsyncElasticsearch

from config import settings


es_client = AsyncElasticsearch(
    settings.ELASTICSEARCH_URL
)


async def check_connection() -> bool:
    return await es_client.ping()


async def create_documents_index() -> None:
    exists = await es_client.indices.exists(
        index=settings.ELASTICSEARCH_INDEX
    )

    if exists:
        return

    await es_client.indices.create(
        index=settings.ELASTICSEARCH_INDEX,
        mappings={
            "properties": {
                "id": {
                    "type": "integer"
                },
                "text": {
                    "type": "text"
                },
                "created_date": {
                    "type": "date"
                },
            }
        }
    )


async def index_document(
    document_id: int,
    text: str,
    created_date: datetime,
) -> None:
    await es_client.index(
        index=settings.ELASTICSEARCH_INDEX,
        id=str(document_id),
        document={
            "id": document_id,
            "text": text,
            "created_date": created_date.isoformat(),
        },
    )


async def search_document_ids(query: str) -> list[int]:
    response = await es_client.search(
        index=settings.ELASTICSEARCH_INDEX,
        query={
            "match": {
                "text": query
            }
        },
        sort=[
            {"created_date": {"order": "desc"}}
        ],
        size=20,
    )

    return [int(hit["_id"]) for hit in response["hits"]["hits"]]


async def delete_document(document_id: int) -> None:
    await es_client.delete(
        index=settings.ELASTICSEARCH_INDEX,
        id=str(document_id),
    )
