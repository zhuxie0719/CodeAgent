import typing as t
from functools import partial

from werkzeug.local import LocalProxy
from werkzeug.local import LocalStack

if t.TYPE_CHECKING:
    from .app import Flask
    from .ctx import AppContext
    from .sessions import SessionMixin
    from .wrappers import Request

_REQUEST_CTX_ERR_MSG = """\
Working outside of request context.

This typically means that you attempted to use functionality that needed
an active HTTP request.  Consult the documentation on testing for
information about how to avoid this problem.\
"""
_APP_CTX_ERR_MSG = """\
Working outside of application context.

This typically means that you attempted to use functionality that needed
to interface with the current application object in some way. To solve
this, set up an application context with app.app_context().  See the
documentation for more information.\
"""


def _lookup_req_object(name):
    top = _REQUEST_CTX_STACK.top
    if top is None:
        raise RuntimeError(_REQUEST_CTX_ERR_MSG)
    return getattr(top, name)


def _lookup_app_object(name):
    top = _APP_CTX_STACK.top
    if top is None:
        raise RuntimeError(_APP_CTX_ERR_MSG)
    return getattr(top, name)


def _find_app():
    top = _APP_CTX_STACK.top
    if top is None:
        raise RuntimeError(_APP_CTX_ERR_MSG)
    return top.app


# context locals
_REQUEST_CTX_STACK = LocalStack()
_APP_CTX_STACK = LocalStack()
current_app: "Flask" = LocalProxy(_find_app)  # type: ignore
request: "Request" = LocalProxy(partial(_lookup_req_object, "request"))  # type: ignore
session: "SessionMixin" = LocalProxy(
    partial(_lookup_req_object, "session"))  # type: ignore  # noqa: B950
g: "AppContext" = LocalProxy(partial(_lookup_app_object, "g"))  # type: ignore
