from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Document
from db.schemas import DocumentResponse
from elastic.client import (
    search_document_ids,
    delete_document as delete_document_from_index,
)


async def search_documents(
    query: str,
    session: AsyncSession,
) -> list[DocumentResponse]:
    document_ids = await search_document_ids(query)

    if not document_ids:
        return []

    stmt = (
        select(Document)
        .where(Document.id.in_(document_ids))
        .order_by(Document.created_date.desc())
    )

    result = await session.execute(stmt)
    documents = result.scalars().all()

    return [
        DocumentResponse.model_validate(document)
        for document in documents
    ]


async def delete_document(
    document_id: int,
    session: AsyncSession,
) -> None:
    stmt = select(Document).where(
        Document.id == document_id
    )

    result = await session.execute(stmt)
    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    await delete_document_from_index(document_id)

    await session.delete(document)
    await session.commit()
