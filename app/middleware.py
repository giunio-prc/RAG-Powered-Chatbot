import uuid
from http.cookies import SimpleCookie

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SessionCookieMiddleware:
    def __init__(self, app: ASGIApp, cookie_name: str = "SESSION"):
        self.app = app
        self.cookie_name = cookie_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        session_cookie = self._get_cookie_from_scope(scope)
        cookies: set[str] = scope["state"].get("cookies", set())
        valid_session = session_cookie and session_cookie in cookies

        if not valid_session:
            new_session = str(uuid.uuid4())
            cookies.add(new_session)
            scope["state"]["cookies"] = cookies
            self._set_cookie_in_scope(scope, new_session)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start" and not valid_session:
                headers = MutableHeaders(scope=message)
                cookie_value = self._get_cookie_from_scope(scope)
                set_cookie = (
                    f"{self.cookie_name}={cookie_value}; "
                    f"HttpOnly; Max-Age={60 * 60 * 24 * 30}; Path=/"
                )
                headers.append("set-cookie", set_cookie)
            await send(message)

        await self.app(scope, receive, send_wrapper)

    def _get_cookie_from_scope(self, scope: Scope) -> str | None:
        headers = dict(scope.get("headers", []))
        cookie_header = headers.get(b"cookie", b"").decode()
        if not cookie_header:
            return None
        cookie = SimpleCookie()
        cookie.load(cookie_header)
        if self.cookie_name in cookie:
            return cookie[self.cookie_name].value
        return None

    def _set_cookie_in_scope(self, scope: Scope, value: str) -> None:
        headers = list(scope.get("headers", []))
        cookie_header = None
        cookie_index = None
        for i, (name, val) in enumerate(headers):
            if name == b"cookie":
                cookie_header = val.decode()
                cookie_index = i
                break

        new_cookie_part = f"{self.cookie_name}={value}"
        if cookie_header and cookie_index is not None:
            new_cookie_header = f"{cookie_header}; {new_cookie_part}"
            headers[cookie_index] = (b"cookie", new_cookie_header.encode())
        else:
            headers.append((b"cookie", new_cookie_part.encode()))

        scope["headers"] = headers
