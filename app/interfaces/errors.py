class TooManyRequestsError(Exception):
    status_code: int = 429
    content: any

    def __init__(self, content: any = None):
        self.content = content
