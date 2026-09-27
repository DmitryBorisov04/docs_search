from fastAPI import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schema import DocumentResponse
from app.db import get_db