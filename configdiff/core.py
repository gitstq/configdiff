"""
ConfigDiff Core - orchestrates file loading, format detection, and diff generation.
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .types import FileData, DiffResult, DiffHunk
from .engines import get_engine
from .formatters import get_formatter


class ConfigDiff:
    """
    Main ConfigDiff orchestrator.

    Usage:
        cd = ConfigDiff()
        result = cd.diff_file("config_a.yaml", "config_b.yaml")
        print(cd.format(result, format="color"))
    """

    def __init__(self, ignore_order: bool = False, ignore_comments: bool = False):
        """
        Args:
            ignore_order: Ignore ordering differences in arrays/lists (useful for JSON)
            ignore_comments: Ignore comment lines when comparing
        """
        self.ignore_order = ignore_order
        self.ignore_comments = ignore_comments

    def load_file(self, path: Union[str, Path]) -> FileData:
        """Load a file and detect its format."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        with open(path, encoding="utf-8", errors="replace") as f:
            raw = f.read()
        fmt = self._detect_format(path.name, raw)
        lines = raw.splitlines(keepends=False)
        return FileData(str(path), raw, fmt, lines)

    def load_string(self, content: str, format_hint: str = None) -> FileData:
        """Load content from a string."""
        fmt = format_hint or self._detect_format("config", content)
        lines = content.splitlines(keepends=False)
        return FileData("stdin", content, fmt, lines)

    def _detect_format(self, filename: str, content: str) -> str:
        """Detect the format of a file based on extension and content."""
        ext = Path(filename).suffix.lower()
        if ext in (".yaml", ".yml"):
            return "yaml"
        elif ext == ".json":
            return "json"
        elif ext in (".toml", ".tml"):
            return "toml"
        elif ext == ".env" or filename.startswith(".env") or ".env." in filename:
            return "env"
        elif ext in (".ini", ".conf", ".cfg"):
            return "ini"
        elif ext == ".xml":
            return "xml"
        elif ext in (".properties", ".props"):
            return "properties"
        else:
            stripped = content.strip()
            if stripped.startswith("{") or stripped.startswith("["):
                return "json"
            if any(line.strip().startswith("#") or line.strip().startswith("//")
                   for line in content.splitlines()[:10]):
                return "yaml"
            return "text"

    def diff_file(self, left_path: Union[str, Path], right_path: Union[str, Path],
                  context: int = 3) -> DiffResult:
        """Diff two files and return structured result."""
        left = self.load_file(left_path)
        right = self.load_file(right_path)
        return self.diff(left, right, context=context)

    def diff(self, left: FileData, right: FileData, context: int = 3) -> DiffResult:
        """Diff two FileData objects."""
        engine = get_engine(left.format, right.format)
        return engine.diff(self, left, right, context=context)

    def diff_strings(self, left_content: str, right_content: str,
                     left_format: str = None, right_format: str = None,
                     context: int = 3) -> DiffResult:
        """Diff two content strings."""
        left = self.load_string(left_content, left_format)
        right = self.load_string(right_content, right_format)
        return self.diff(left, right, context=context)

    def format(self, result: DiffResult, format: str = "color") -> str:
        """Format a diff result for display."""
        fmt = get_formatter(format)
        return fmt.format_diff(result)

    def print_diff(self, result: DiffResult, format: str = "color"):
        """Print a diff result to stdout."""
        print(self.format(result, format=format))

    def diff_dir(self, left_dir: Union[str, Path], right_dir: Union[str, Path],
                 pattern: str = "*", recursive: bool = True,
                 format: str = "color") -> Dict[str, DiffResult]:
        """Diff all matching files in two directories."""
        left_dir = Path(left_dir)
        right_dir = Path(right_dir)
        results = {}
        if recursive:
            left_files = {p.relative_to(left_dir): p for p in left_dir.rglob(pattern)
                          if p.is_file() and not self._is_ignored(p)}
            right_files = {p.relative_to(right_dir): p for p in right_dir.rglob(pattern)
                           if p.is_file() and not self._is_ignored(p)}
        else:
            left_files = {p.relative_to(left_dir): p for p in left_dir.glob(pattern)
                          if p.is_file() and not self._is_ignored(p)}
            right_files = {p.relative_to(right_dir): p for p in right_dir.glob(pattern)
                           if p.is_file() and not self._is_ignored(p)}
        all_keys = set(left_files.keys()) | set(right_files.keys())
        for rel_path in sorted(all_keys):
            left_path = left_files.get(rel_path)
            right_path = right_files.get(rel_path)
            try:
                if left_path and right_path:
                    result = self.diff_file(left_path, right_path)
                    if result.changed:
                        results[str(rel_path)] = result
                elif left_path:
                    results[str(rel_path)] = DiffResult(
                        str(left_path), "(deleted)", "text", [],
                        {'added': 0, 'removed': self._count_lines(left_path), 'changed': 0}
                    )
                else:
                    results[str(rel_path)] = DiffResult(
                        "(added)", str(right_path), "text", [],
                        {'added': self._count_lines(right_path), 'removed': 0, 'changed': 0}
                    )
            except Exception as e:
                results[str(rel_path)] = None
        return results

    def _is_ignored(self, path: Path) -> bool:
        """Check if a file should be ignored."""
        name = path.name
        return name.startswith(".") or name.endswith("~") or name.endswith(".swp") or "__pycache__" in str(path)

    def _count_lines(self, path: Path) -> int:
        """Count lines in a file."""
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
