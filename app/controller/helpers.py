from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents import Document

text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)


def chunk_document(content: str) -> list[Document]:
    document = Document(content)
    chunks = text_splitter.split_documents([document])
    return chunks
