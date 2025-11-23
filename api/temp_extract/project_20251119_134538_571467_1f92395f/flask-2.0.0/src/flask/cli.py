import ast
import inspect
import os
import platform
import re
import sys
import traceback
import warnings
from functools import update_wrapper
from operator import attrgetter
from threading import Lock
from threading import Thread

import click
from werkzeug.utils import import_string

from .globals import current_app
from .globals import _app_ctx_stack
from .helpers import get_debug_flag
from .helpers import get_env
from .helpers import get_load_dotenv

try:
    import dotenv
except ImportError:
    dotenv = None

try:
    import ssl
except ImportError:
    ssl = None

try:
    import pkg_resources
except ImportError:
    pkg_resources = None
try:
    import wsgi
except ImportError:
    wsgi = None


def get_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"Flask {__version__}")
    ctx.exit()

class ScriptInfo:
    def __init__(self, app_import_path=None, create_app=None, set_debug_flag=True):
        self.app_import_path = app_import_path
        self.create_app = create_app
        self.set_debug_flag = set_debug_flag
        self._loaded_app = None

    def load_app(self):
        if self._loaded_app is not None:
            return self._loaded_app

        app = None

        if self.create_app is not None:
            app = self.create_app()
        else:
            if self.app_import_path:
                path, name = (self.app_import_path.split(":", 1) + [None])[:2]
                app = import_string(path)
                if name is not None:
                    app = getattr(app, name)
            else:
                if wsgi is not None:
                    app = wsgi.application

        if not app:
            raise click.NoSuchOptionException(
                "Could not locate a Flask application. Use the "
                "'FLASK_APP' environment variable to specify one."
            )

        if self.set_debug_flag:
            app.debug = get_debug_flag()

        self._loaded_app = app
        return app

def with_appcontext(file_obj):
    @click.pass_context
    def decorator(ctx, *args, **kwargs):
        with ctx.ensure_object(ScriptInfo).load_app().app_context():
            return ctx.invoke(file_obj, *args, **kwargs)
    return update_wrapper(decorator, file_obj)

class FlaskGroup(click.Group):
    def __init__(self, add_default_commands=True, create_app=None, add_version_option=True, **extra):
        params = list(extra.pop("params", None) or ())
        
        if add_version_option:
            params.append(click.Option(
                ["--version"],
                help="Show the flask version",
                is_flag=True,
                callback=get_version,
                expose_value=False,
                is_eager=True,
            ))
        
        super(FlaskGroup, self).__init__(params=params, **extra)
        
        self.create_app = create_app
        
        if add_default_commands:
            self.add_command(run)
    
    def get_command(self, ctx, cmd_name):
        rv = super(FlaskGroup, self).get_command(ctx, cmd_name)
        if rv is not None:
            return rv
        
        info = ctx.ensure_object(ScriptInfo)
        try:
            app = info.load_app()
        except Exception:
            return None
        
        return app.cli.get_command(ctx, cmd_name)
    
    def list_commands(self, ctx):
        rv = set(super(FlaskGroup, self).list_commands(ctx))
        info = ctx.ensure_object(ScriptInfo)
        try:
            app = info.load_app()
            rv.update(app.cli.list_commands(ctx))
        except Exception:
            pass
        
        return sorted(rv)
    
    def main(self, *args, **kwargs):
        obj = kwargs.get("obj")
        if obj is None:
            obj = ScriptInfo(create_app=self.create_app)
        kwargs["obj"] = obj
        return super(FlaskGroup, self).main(*args, **kwargs)

@click.group(cls=FlaskGroup, add_default_commands=False, add_version_option=False)
@click.option("--version", help="Show the flask version", expose_value=False, is_flag=True, callback=get_version, is_eager=True)
@click.pass_context
def cli(ctx):
    pass

@cli.command()
@click.option("--host", "-h", default="127.0.0.1", help="The interface to bind to.")
@click.option("--port", "-p", default=5000, help="The port to bind to.")
@click.option("--cert", help="Specify a certificate file to use HTTPS.")
@click.option("--key", help="The key file to use when specifying a certificate.")
@click.option("--reload/--no-reload", default=None, help="Enable or disable the reloader.")
@click.option("--debugger/--no-debugger", default=None, help="Enable or disable the debugger.")
@click.option("--eager-loading/--lazy-loading", default=None, help="Enable or disable eager loading.")
@click.option("--with-threads/--without-threads", default=True, help="Enable or disable multithreading.")
@with_appcontext
def run(host, port, cert, key, reload, debugger, eager_loading, with_threads):
    """Run a local development server.

    This command runs a local development server for the Flask application.
    It handles command-line arguments for host, port, SSL certificates, and
    development options like reloading and debugging.
    """
    from . import __version__
    
    app = current_app
    debug = get_debug_flag()
    
    if reload is None:
        reload = debug
    
    if debugger is None:
        debugger = debug
    
    if eager_loading is None:
        eager_loading = debug
    
    use_reloader = reload
    use_debugger = debugger
    
    if cert and key:
        if ssl is None:
            raise click.ClickException("SSL is not available.")
        ssl_context = (cert, key)
    elif cert:
        ssl_context = cert
    else:
        ssl_context = None
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_debugger=use_debugger,
        use_reloader=use_reloader,
        threaded=with_threads,
        ssl_context=ssl_context
    )

def main():
    cli()

if __name__ == "__main__":
    main()
