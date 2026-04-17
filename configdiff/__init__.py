"""
ConfigDiff - Multi-format configuration file diff and merge tool.
Zero-dependency Python stdlib implementation.
"""
__version__ = "1.0.0"
__author__ = "gitstq"
__license__ = "MIT"

from .types import FileData, DiffResult, DiffHunk
from .core import ConfigDiff
from .engines import get_engine

__all__ = ["ConfigDiff", "FileData", "DiffResult", "DiffHunk", "get_engine", "__version__"]
