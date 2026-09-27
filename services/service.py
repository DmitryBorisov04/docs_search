from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.schemas.document import DocumentResponse


async def get_document(session: AsyncSession) -> list[DocumentResponse]:
    """Получение списка документов"""

    stmt = select(Document)
    result = await session.execute(stmt)
    documents = result.scalars().all()

    if not documents:
        raise HTTPException(status_code=404, detail="Documents not found")

    return [DocumentResponse.from_orm(doc) for doc in documents]
