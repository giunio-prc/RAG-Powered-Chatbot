from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_cookie_session, get_db_from_state_annotation
from app.controller.controller import add_content_into_db

router = APIRouter()


@router.post("/add-document")
async def add_document_endpoint(
    db: get_db_from_state_annotation,
    file: UploadFile,
    cookie_session: Annotated[str, Depends(get_cookie_session)],
):
    if file.content_type != "text/plain":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid file. The app only supprt text files",
        )
    try:
        file_content = file.file.read().decode()
    except UnicodeError:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The file cannot be uploaded",
        )
    return StreamingResponse(
        add_content_into_db(db, file_content, cookie_session), media_type="text/plain"
    )


@router.get("/get-vectors-data")
async def get_vectors_data(
    db: get_db_from_state_annotation,
    cookie_session: Annotated[str, Depends(get_cookie_session)],
):
    number_of_vectors = db.get_number_of_vectors(cookie_session)
    longest_vector = db.get_length_of_longest_vector(cookie_session)
    return {"number_of_vectors": number_of_vectors, "longest_vector": longest_vector}
