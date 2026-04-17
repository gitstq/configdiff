"""
ConfigDiff Shared Types - no circular imports.
"""
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class FileData:
    """Container for loaded file content."""
    path: str
    content: str
    format: str
    raw_lines: List[str]


@dataclass
class DiffHunk:
    """A single diff hunk with line ranges."""
    left_start: int
    left_count: int
    right_start: int
    right_count: int
    lines: List  # List[Tuple[str, str]] — (tag, line)


@dataclass
class DiffResult:
    """Complete diff result for a file pair."""
    left_path: str
    right_path: str
    format: str
    hunks: List
    stats: Dict  # {'added': N, 'removed': N, 'changed': N}

    @property
    def has_changes(self) -> bool:
        return self.stats['added'] > 0 or self.stats['removed'] > 0 or self.stats['changed'] > 0

    @property
    def changed(self) -> bool:
        return self.has_changes
