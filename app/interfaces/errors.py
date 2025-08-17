class TooManyRequestsError(Exception):
    status_code: int = 429
    content: any

    def __init__(self, content: any = None):
        self.content = content


class EmbeddingAPILimitError(Exception):
    """Raised when the embedding API limit is reached during document upload"""
    status_code: int = 429
    content: any

    def __init__(self, content: any = None, chunks_uploaded: int = 0):
        self.content = content
        self.chunks_uploaded = chunks_uploaded
