

class TooManyRequestsError(Exception):
    status_code: int = 429
    content: object

    def __init__(self, content: object = None):
        self.content = content


class EmbeddingAPILimitError(Exception):
    """Raised when the embedding API limit is reached during document upload"""

    status_code: int = 429
    content: object

    def __init__(self, content: object = None, chunks_uploaded: int = 0):
        self.content = content
        self.chunks_uploaded = chunks_uploaded
