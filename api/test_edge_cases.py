import os
import types
import errno
import typing as t
import importlib.util
import sys
from importlib import import_module

def import_string(import_name):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).
    """
    if ':' in import_name:
        module, obj = import_name.split(':', 1)
    elif '.' in import_name:
        module, _, obj = import_name.rpartition('.')
    else:
        return import_module(import_name)
    return getattr(import_module(module), obj)

class Config(dict):
    """Works exactly like a dict but provides ways to fill it from files
    or special dictionaries.  There are two common patterns to populate the
    config.
    Either you can fill the config from a config file::
        app.config.from_pyfile('yourconfig.cfg')
    Or alternatively you can define the configuration options in the
    module that calls :meth:`from_object` or provide an import path to
    a module that should be loaded.  It is also possible to tell it to
    use the same module and with that provide the configuration values
    just before the call::
        DEBUG = True
        SECRET_KEY = 'development key'
        app.config.from_object(__name__)
    """

    def __init__(self, root_path: str, defaults: t.Optional[dict] = None) -> None:
        dict.__init__(self, defaults or {})
        self.root_path = root_path

    def from_pyfile(self, filename: str, silent: bool = False) -> bool:
        """Updates the values in the config from a Python file.  This function
        behaves as if the file was imported as module with the
        :meth:`from_object` function.

        :param filename: the filename of the config.  This can either be an
                         absolute filename or a filename relative to the
                         root path.
        :param silent: set to ``True`` if you want silent failure for missing
                       files.

        .. versionadded:: 0.7
           `silent` parameter.
        """
        filename = os.path.join(self.root_path, filename)
        try:
            spec = importlib.util.spec_from_file_location("config", filename)
            config_module = importlib.util.module_from_spec(spec)
            sys.modules["config"] = config_module
            spec.loader.exec_module(config_module)
        except OSError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR, errno.ENOTDIR):
                return False
            e.strerror = f"Unable to load configuration file ({e.strerror})"
            raise
        self.from_object(config_module)
        return True

    def from_object(self, obj: t.Union[object, str]) -> None:
        """Updates the values from the given object.  An object can be of one
        of the following two types:
        -   a string: in this case the object with that name will be imported
        -   an actual object reference: that object is used directly
        Objects are usually either modules or classes. :meth:`from_object`
        loads only the uppercase attributes of the module/class. A ``dict``
        object will not work with :meth:`from_object` because the keys of a
        ``dict`` are not attributes of the ``dict`` class.
        Example of module-based configuration::
            app.config.from_object('yourapplication.default_config')
            from yourapplication import default_config
            app.config.from_object(default_config)
        You should not use this function to load the actual configuration but
        rather configuration defaults.  The actual config should be loaded
        with :meth:`from_pyfile` and ideally from a location not within the
        package because the package might be installed system wide.
        :param obj: an import name or object
        """
        if isinstance(obj, str):
            obj = import_string(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

print("Testing edge cases...")

# Test 1: Normal case
print("\n1. Testing normal configuration file:")
test_config_content = '''
DEBUG = True
SECRET_KEY = "test_key"
DATABASE_URI = "sqlite:///test.db"
'''
with open("test_config.py", "w") as f:
    f.write(test_config_content)

config = Config(".")
result = config.from_pyfile("test_config.py")
print(f"Success: {result}")
print(f"DEBUG: {config['DEBUG']}")

# Test 2: Silent mode with non-existent file
print("\n2. Testing silent mode with non-existent file:")
config2 = Config(".")
result = config2.from_pyfile("non_existent_config.py", silent=True)
print(f"Silent failure handled correctly: {result}")

# Test 3: Complex configuration with imports and functions
print("\n3. Testing complex configuration:")
complex_config_content = '''
import os
DEBUG = True
SECRET_KEY = "complex_key"
BASE_DIR = os.path.dirname(__file__)
DATABASE_URI = f"sqlite:///{BASE_DIR}/app.db"

def get_database_config():
    return {"uri": DATABASE_URI, "debug": DEBUG}
'''
with open("complex_config.py", "w") as f:
    f.write(complex_config_content)

config3 = Config(".")
result = config3.from_pyfile("complex_config.py")
print(f"Complex config loaded: {result}")
print(f"SECRET_KEY: {config3['SECRET_KEY']}")
print(f"BASE_DIR: {config3['BASE_DIR']}")

# Clean up
os.remove("test_config.py")
os.remove("complex_config.py")
print("\nAll tests completed successfully!")
