from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("ce-ui")
except PackageNotFoundError:
    __version__ = "unknown"
