from fastapi import APIRouter, HTTPException, UploadFile

from app.api.dependencies import get_db_from_state_annotation
from app.controller.controller import add_content_into_db

router = APIRouter()


@router.post("/add-document")
async def add_document_endpoint(db: get_db_from_state_annotation, file: UploadFile):
    if file.content_type != "text/plain":
        raise HTTPException(
            status_code=400, detail="Invalid file. The app only supprt text files"
        )
    await add_content_into_db(db, file.file.read().decode())


@router.get("/get-vectors-data")
async def get_vectors_data(db: get_db_from_state_annotation):
    number_of_vectors = db.get_number_of_vectors()
    longest_vector = db.get_length_of_longest_vector()
    return {"number_of_vectors": number_of_vectors, "longest_vector": longest_vector}
