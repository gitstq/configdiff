"""
ConfigDiff Formatters - output diff results in various formats.
"""
import json
from typing import List

from .types import DiffHunk, DiffResult


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    GRAY = "\033[90m"
    DIM = "\033[2m"

    @classmethod
    def strip(cls, text: str) -> str:
        import re
        return re.sub(r'\x1b\[[0-9;]*m', '', text)


class ColorFormatter:
    """Colored terminal output formatter."""

    def format_diff(self, result: DiffResult) -> str:
        if not result.has_changes:
            return f"{Colors.GREEN}{Colors.BOLD}OK - No differences{Colors.RESET}"
        lines = []
        lines.append(self._header(result))
        for hunk in result.hunks:
            lines.append(self._format_hunk(hunk))
        lines.append(self._stats(result))
        return "\n".join(lines)

    def _header(self, result: DiffResult) -> str:
        return f"{Colors.BOLD}--- {result.left_path}{Colors.RESET}\n{Colors.BOLD}+++ {result.right_path}{Colors.RESET}"

    def _format_hunk(self, hunk: DiffHunk) -> str:
        lines = []
        lines.append(f"{Colors.DIM}@@ -{hunk.left_start},{hunk.left_count} +{hunk.right_start},{hunk.right_count} @@{Colors.RESET}")
        for tag, line in hunk.lines:
            if tag == '-':
                lines.append(f"{Colors.RED}-{line}{Colors.RESET}")
            elif tag == '+':
                lines.append(f"{Colors.GREEN}+{line}{Colors.RESET}")
            elif tag == '!':
                lines.append(f"{Colors.YELLOW}!{line}{Colors.RESET}")
            else:
                lines.append(f"{Colors.GRAY} {line}{Colors.RESET}")
        return "\n".join(lines)

    def _stats(self, result: DiffResult) -> str:
        s = result.stats
        parts = []
        if s['added']:
            parts.append(f"{Colors.GREEN}+{s['added']} added{Colors.RESET}")
        if s['removed']:
            parts.append(f"{Colors.RED}-{s['removed']} removed{Colors.RESET}")
        if s['changed']:
            parts.append(f"{Colors.YELLOW}~{s['changed']} changed{Colors.RESET}")
        return f"\n{Colors.BOLD}Summary:{Colors.RESET} " + "  ".join(parts)


class PlainFormatter:
    """Plain text output (no colors)."""

    def format_diff(self, result: DiffResult) -> str:
        if not result.has_changes:
            return "No differences found."
        lines = []
        lines.append(f"--- {result.left_path}")
        lines.append(f"+++ {result.right_path}")
        for hunk in result.hunks:
            lines.append(f"@@ -{hunk.left_start},{hunk.left_count} +{hunk.right_start},{hunk.right_count} @@")
            for tag, line in hunk.lines:
                lines.append(f"{tag}{line}")
        s = result.stats
        parts = []
        if s['added']: parts.append(f"+{s['added']} added")
        if s['removed']: parts.append(f"-{s['removed']} removed")
        if s['changed']: parts.append(f"~{s['changed']} changed")
        lines.append(f"Summary: {'  '.join(parts)}")
        return "\n".join(lines)


class JsonFormatter:
    """JSON output formatter."""

    def format_diff(self, result: DiffResult) -> str:
        data = {
            "left": result.left_path,
            "right": result.right_path,
            "format": result.format,
            "stats": result.stats,
            "changed": result.changed,
            "hunks": []
        }
        for hunk in result.hunks:
            data["hunks"].append({
                "left_start": hunk.left_start,
                "left_count": hunk.left_count,
                "right_start": hunk.right_start,
                "right_count": hunk.right_count,
                "lines": [{"tag": tag, "content": line} for tag, line in hunk.lines]
            })
        return json.dumps(data, ensure_ascii=False, indent=2)


class MarkdownFormatter:
    """Markdown output formatter."""

    def format_diff(self, result: DiffResult) -> str:
        lines = []
        lines.append(f"## Diff: `{result.left_path}` vs `{result.right_path}`")
        lines.append("")
        if not result.has_changes:
            lines.append("**OK - No differences found.**")
            return "\n".join(lines)
        for hunk in result.hunks:
            lines.append(f"### @@ -{hunk.left_start},+{hunk.right_start} @@")
            for tag, line in hunk.lines:
                if tag == '-':
                    lines.append(f"<span style='color:red'>- {line}</span>")
                elif tag == '+':
                    lines.append(f"<span style='color:green'>+ {line}</span>")
                elif tag == '!':
                    lines.append(f"<span style='color:orange'>! {line}</span>")
                else:
                    lines.append(f"  {line}")
            lines.append("")
        s = result.stats
        parts = []
        if s['added']: parts.append(f"+{s['added']} added")
        if s['removed']: parts.append(f"-{s['removed']} removed")
        if s['changed']: parts.append(f"~{s['changed']} changed")
        lines.append(f"**Summary:** {'  '.join(parts)}")
        return "\n".join(lines)


class GitStyleFormatter:
    """Classic git-style diff output."""

    def format_diff(self, result: DiffResult) -> str:
        if not result.has_changes:
            return ""
        lines = []
        lines.append(f"diff --git a/{result.left_path} b/{result.right_path}")
        lines.append(f"--- a/{result.left_path}")
        lines.append(f"+++ b/{result.right_path}")
        for hunk in result.hunks:
            lines.append(f"@@ -{hunk.left_start},{hunk.left_count} +{hunk.right_start},{hunk.right_count} @@")
            for tag, line in hunk.lines:
                lines.append(f"{tag} {line}")
        return "\n".join(lines)


_FORMATS = {
    "color": ColorFormatter,
    "plain": PlainFormatter,
    "text": PlainFormatter,
    "json": JsonFormatter,
    "markdown": MarkdownFormatter,
    "md": MarkdownFormatter,
    "git": GitStyleFormatter,
}


def get_formatter(name: str):
    """Get formatter instance by name."""
    cls = _FORMATS.get(name.lower())
    if cls is None:
        raise ValueError(f"Unknown format: {name}. Available: {list(_FORMATS.keys())}")
    return cls()
