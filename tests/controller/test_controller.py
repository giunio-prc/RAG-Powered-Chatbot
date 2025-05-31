from pathlib import Path

import pytest

from app.controller.controller import add_content_into_db


@pytest.mark.asyncio
async def test_add_document_into_db():
    folder = Path(__file__).parent / "data"
    await add_content_into_db(folder)
