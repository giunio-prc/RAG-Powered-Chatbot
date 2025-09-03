import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SessionCookieMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, cookie_name: str = "SESSION"):
        super().__init__(app)
        self.cookie_name = cookie_name

    async def dispatch(self, request: Request, call_next):
        session_cookie = request.cookies.get(self.cookie_name)

        valid_session = session_cookie and session_cookie in request.state.cookies

        if not valid_session:
            new_session = str(uuid.uuid4())
            request.state.cookies.add(new_session)
            request.cookies[self.cookie_name] = new_session

        response = await call_next(request)

        if not valid_session:
            response.set_cookie(
                key=self.cookie_name,
                value=request.cookies[self.cookie_name],
                httponly=True,
                expires=3600,
            )

        return response
