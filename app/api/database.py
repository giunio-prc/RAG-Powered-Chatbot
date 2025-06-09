from fastapi import APIRouter, HTTPException, Request, UploadFile

from app.controller.controller import add_content_into_db
from app.interfaces.database import DatabaseManagerInterface

router = APIRouter()


@router.post("/add-document")
async def add_document(request: Request, file: UploadFile):
    if file.content_type != "text/plain":
        raise HTTPException(
            status_code=400, detail="Invalid file. The app only supprt text files"
        )
    db: DatabaseManagerInterface = request.state.db
    await add_content_into_db(db, file.file.read())
