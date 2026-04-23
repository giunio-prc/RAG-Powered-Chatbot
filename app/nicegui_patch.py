import gc
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from nicegui import core, helpers, storage
from nicegui.air import Air
from nicegui.logging import log
from nicegui.middlewares import RedirectWithPrefixMiddleware, SetCacheControlMiddleware
from nicegui.nicegui import _shutdown, _startup
from nicegui.server import Server


def _safe_get_server_instance(app) -> uvicorn.Server | None:
    """Safe version that handles ReferenceError during gc.get_objects iteration."""
    try:
        for obj in gc.get_objects():
            try:
                if isinstance(obj, uvicorn.Server):
                    wrapped = obj.config.loaded_app
                    while wrapped is not None:
                        if wrapped is app:
                            return obj
                        wrapped = getattr(wrapped, "app", None)
            except ReferenceError:
                continue
    except ReferenceError:
        pass
    return None


def safe_run_with(
    app: FastAPI,
    *,
    root=None,
    title: str = "NiceGUI",
    viewport: str = "width=device-width, initial-scale=1",
    favicon: str | Path | None = None,
    dark: bool | None = False,
    language="en-US",
    binding_refresh_interval: float | None = 0.1,
    reconnect_timeout: float = 3.0,
    message_history_length: int = 1000,
    cache_control_directives: str = "public, max-age=31536000, immutable, stale-while-revalidate=31536000",
    gzip_middleware_factory=GZipMiddleware,
    mount_path: str = "/",
    on_air: str | Literal[True] | None = None,
    tailwind: bool = True,
    unocss: Literal["mini", "wind3", "wind4"] | None = None,
    prod_js: bool = True,
    storage_secret: str | None = None,
    session_middleware_kwargs: dict[str, Any] | None = None,
    show_welcome_message: bool = True,
) -> None:
    """Safe version of NiceGUI's run_with that handles ReferenceError."""
    if core.script_mode:
        log.warning(
            "NiceGUI elements were created outside of a page context before ui.run_with() was called.\n"
            "This is not supported and the elements will be discarded.\n"
            "Move UI element creation into a @ui.page function or an app.on_startup handler."
        )
        if core.script_client is not None:
            core.script_client.delete()
            core.script_client = None
        core.script_mode = False

    core.app.config.add_run_config(
        reload=False,
        title=title,
        viewport=viewport,
        favicon=favicon,
        dark=dark,
        language=language,
        binding_refresh_interval=binding_refresh_interval,
        reconnect_timeout=reconnect_timeout,
        message_history_length=message_history_length,
        tailwind=tailwind,
        unocss=unocss,
        prod_js=prod_js,
        show_welcome_message=show_welcome_message,
        cache_control_directives=cache_control_directives,
    )
    core.root = root
    storage.set_storage_secret(
        storage_secret, session_middleware_kwargs, parent_app=app
    )
    if not helpers.is_pytest() and gzip_middleware_factory is not None:
        core.app.add_middleware(gzip_middleware_factory)
    core.app.add_middleware(RedirectWithPrefixMiddleware)
    core.app.add_middleware(SetCacheControlMiddleware)

    if on_air:
        core.air = Air("" if on_air is True else on_air)

    app.mount(mount_path, core.app)
    main_app_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def safe_lifespan_wrapper(fastapi_app):
        if (instance := _safe_get_server_instance(fastapi_app)) is not None:
            Server.instance = instance
        await _startup()
        async with main_app_lifespan(fastapi_app) as state:
            yield state
        await _shutdown()

    app.router.lifespan_context = safe_lifespan_wrapper
