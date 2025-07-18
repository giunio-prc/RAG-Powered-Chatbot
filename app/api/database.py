from fastapi import APIRouter, HTTPException, Request, UploadFile

from app.controller.controller import add_content_into_db
from app.interfaces.database import DatabaseManagerInterface

router = APIRouter()


@router.post("/add-document")
async def add_document_endpoint(request: Request, file: UploadFile):
    if file.content_type != "text/plain":
        raise HTTPException(
            status_code=400, detail="Invalid file. The app only supprt text files"
        )
    db: DatabaseManagerInterface = request.state.db
    await add_content_into_db(db, file.file.read().decode())


@router.get("/get-vectors-data")
async def get_vectors_data(request: Request):
    db: DatabaseManagerInterface = request.state.db
    number_of_vectors = db.get_number_of_vectors()
    longest_vector = db.get_length_of_longest_vector()
    return {"number_of_vectors": number_of_vectors, "longest_vector": longest_vector}
