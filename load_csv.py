import ast
import asyncio
import csv
from datetime import datetime

from db.models import Document
from db.session import AsyncSessionLocal
from elastic.client import (
    create_documents_index,
    index_document,
    es_client,
)


CSV_PATH = "posts.csv"


async def load_csv() -> None:
    await create_documents_index()

    async with AsyncSessionLocal() as session:
        with open(
            CSV_PATH,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                document = Document(
                    text=row["text"],
                    created_date=datetime.fromisoformat(
                        row["created_date"]
                    ),
                    rubrics=ast.literal_eval(
                        row["rubrics"]
                    ),
                )

                session.add(document)

                await session.flush()

                await index_document(
                    document_id=document.id,
                    text=document.text,
                    created_date=document.created_date,
                )

        await session.commit()

    await es_client.close()


if __name__ == "__main__":
    asyncio.run(load_csv())
