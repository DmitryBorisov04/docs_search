from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from db.schemas import DocumentResponse
from services.service import (
    search_documents as search_documents_service,
    delete_document as delete_document_service,
)


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.get(
    "/search",
    response_model=list[DocumentResponse],
)
async def search_documents(
    q: str = Query(..., min_length=1),
    session: AsyncSession = Depends(get_db),
):
    return await search_documents_service(q, session)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id: int,
    session: AsyncSession = Depends(get_db),
):
    await delete_document_service(document_id, session)
