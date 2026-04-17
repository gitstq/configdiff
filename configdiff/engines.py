"""
ConfigDiff Engines - format-specific diff implementations.
"""
import difflib
import json
from typing import Any, Dict, List

from .types import DiffResult, DiffHunk, FileData


def get_engine(left_format: str, right_format: str):
    """Get the appropriate diff engine for the given formats."""
    if left_format == right_format:
        return _ENGINES.get(left_format, TextEngine())()
    return TextEngine()


class TextEngine:
    """Text-based diff engine using difflib.unified_diff."""

    def diff(self, cd, left: FileData, right: FileData, context: int = 3) -> DiffResult:
        lines_l = left.raw_lines
        lines_r = right.raw_lines
        matcher = difflib.SequenceMatcher(None, lines_l, lines_r)
        hunks = self._build_hunks(matcher, lines_l, lines_r, context=context)
        added = sum(1 for h in hunks for tag, _ in h.lines if tag == '+')
        removed = sum(1 for h in hunks for tag, _ in h.lines if tag == '-')
        return DiffResult(
            left.path, right.path, left.format, hunks,
            {'added': added, 'removed': removed, 'changed': len(hunks)}
        )

    def _build_hunks(self, matcher, lines_l, lines_r, context: int) -> List[DiffHunk]:
        hunks = []
        opcodes = matcher.get_opcodes()
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                continue
            current_lines = []
            for idx in range(max(i1 - context, 0), i1):
                current_lines.append((' ', lines_l[idx]))
            for idx in range(i1, i2):
                current_lines.append(('-', lines_l[idx]))
            for idx in range(j1, j2):
                current_lines.append(('+', lines_r[idx]))
            # Trailing context
            for idx in range(i2, min(len(lines_l), i2 + context)):
                current_lines.append((' ', lines_l[idx]))
            if current_lines:
                left_nums = [i + 1 for i, (tag, _) in enumerate(current_lines) if tag != '+']
                right_nums = [j + 1 for j, (tag, _) in enumerate(current_lines) if tag != '-']
                ls = min(left_nums) if left_nums else 1
                rs = min(right_nums) if right_nums else 1
                hunks.append(DiffHunk(ls, len(left_nums), rs, len(right_nums), list(current_lines)))
        return hunks


class JsonEngine:
    """JSON-aware structured diff engine."""

    def diff(self, cd, left: FileData, right: FileData, context: int = 3) -> DiffResult:
        try:
            data_l = json.loads(left.content)
            data_r = json.loads(right.content)
        except json.JSONDecodeError:
            return TextEngine().diff(cd, left, right, context=context)
        changes = self._deep_diff("", data_l, data_r, ignore_order=cd.ignore_order)
        hunks = self._build_hunks_from_changes(changes)
        added = sum(1 for c in changes if c['type'] == 'added')
        removed = sum(1 for c in changes if c['type'] == 'removed')
        changed = sum(1 for c in changes if c['type'] == 'changed')
        return DiffResult(
            left.path, right.path, "json", hunks,
            {'added': added, 'removed': removed, 'changed': changed}
        )

    def _deep_diff(self, path: str, left: Any, right: Any, ignore_order: bool = False) -> List[Dict]:
        changes = []
        if type(left) != type(right):
            changes.append({'type': 'changed', 'path': path, 'old': left, 'new': right})
            return changes
        if isinstance(left, dict):
            all_keys = set(left.keys()) | set(right.keys())
            for k in sorted(all_keys):
                child_path = f"{path}.{k}" if path else k
                if k not in left:
                    changes.append({'type': 'added', 'path': child_path, 'value': right[k]})
                elif k not in right:
                    changes.append({'type': 'removed', 'path': child_path, 'value': left[k]})
                elif left[k] != right[k]:
                    changes.extend(self._deep_diff(child_path, left[k], right[k], ignore_order))
        elif isinstance(left, list):
            if ignore_order:
                l_sorted, r_sorted = sorted(left, key=str), sorted(right, key=str)
                if l_sorted != r_sorted:
                    changes.append({'type': 'changed', 'path': path, 'old': left, 'new': right})
            else:
                max_len = max(len(left), len(right))
                for i in range(max_len):
                    child_path = f"{path}[{i}]" if path else f"[{i}]"
                    if i >= len(left):
                        changes.append({'type': 'added', 'path': child_path, 'value': right[i]})
                    elif i >= len(right):
                        changes.append({'type': 'removed', 'path': child_path, 'value': left[i]})
                    elif left[i] != right[i]:
                        changes.extend(self._deep_diff(child_path, left[i], right[i], ignore_order))
        else:
            if left != right:
                changes.append({'type': 'changed', 'path': path, 'old': left, 'new': right})
        return changes

    def _build_hunks_from_changes(self, changes: List[Dict]) -> List[DiffHunk]:
        lines = []
        for c in changes:
            if c['type'] == 'changed':
                lines.append(('!', f"  {c['path']}:"))
                lines.append(('-', f"    old: {repr(c['old'])}"))
                lines.append(('+', f"    new: {repr(c['new'])}"))
            elif c['type'] == 'added':
                lines.append(('+', f"  + {c['path']}: {repr(c['value'])}"))
            elif c['type'] == 'removed':
                lines.append(('-', f"  - {c['path']}: {repr(c['value'])}"))
        if lines:
            return [DiffHunk(1, 1, 1, 1, lines)]
        return []


class YamlEngine:
    """YAML-aware diff engine."""

    def __init__(self):
        self._json_engine = JsonEngine()

    def diff(self, cd, left: FileData, right: FileData, context: int = 3) -> DiffResult:
        try:
            import yaml
            data_l = yaml.safe_load(left.content)
            data_r = yaml.safe_load(right.content)
            left_norm = json.dumps(data_l, sort_keys=True, ensure_ascii=False)
            right_norm = json.dumps(data_r, sort_keys=True, ensure_ascii=False)
            fake_left = FileData(left.path, left_norm, "json", left_norm.splitlines())
            fake_right = FileData(right.path, right_norm, "json", right_norm.splitlines())
            return self._json_engine.diff(cd, fake_left, fake_right, context=context)
        except ImportError:
            return TextEngine().diff(cd, left, right, context=context)
        except Exception:
            return TextEngine().diff(cd, left, right, context=context)


class EnvEngine:
    """Dotenv (.env) file diff engine."""

    def diff(self, cd, left: FileData, right: FileData, context: int = 3) -> DiffResult:
        lines_l = self._parse_env(left.raw_lines)
        lines_r = self._parse_env(right.raw_lines)
        all_keys = set(lines_l.keys()) | set(lines_r.keys())
        hunks = []
        added = removed = changed = 0
        for k in sorted(all_keys):
            if k not in lines_l:
                hunks.append(DiffHunk(0, 0, 1, 1, [('+', f"{k}={lines_r[k]}")]))
                added += 1
            elif k not in lines_r:
                hunks.append(DiffHunk(1, 1, 0, 0, [('-', f"{k}={lines_l[k]}")]))
                removed += 1
            elif lines_l[k] != lines_r[k]:
                hunks.append(DiffHunk(1, 1, 1, 1, [('-', f"{k}={lines_l[k]}"), ('+', f"{k}={lines_r[k]}")]))
                changed += 1
        return DiffResult(left.path, right.path, "env", hunks,
                          {'added': added, 'removed': removed, 'changed': changed})

    def _parse_env(self, lines: List[str]) -> Dict[str, str]:
        result = {}
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                result[key.strip()] = val.strip().strip('"').strip("'")
        return result


class TomlEngine:
    """TOML diff engine - falls back to text diff for now."""

    def diff(self, cd, left: FileData, right: FileData, context: int = 3) -> DiffResult:
        try:
            import tomli
            import json
            data_l = tomli.loads(left.content)
            data_r = tomli.loads(right.content)
            left_norm = json.dumps(data_l, sort_keys=True, ensure_ascii=False)
            right_norm = json.dumps(data_r, sort_keys=True, ensure_ascii=False)
            fake_left = FileData(left.path, left_norm, "json", left_norm.splitlines())
            fake_right = FileData(right.path, right_norm, "json", right_norm.splitlines())
            return JsonEngine().diff(cd, fake_left, fake_right, context=context)
        except ImportError:
            return TextEngine().diff(cd, left, right, context=context)
        except Exception:
            return TextEngine().diff(cd, left, right, context=context)


_ENGINES = {
    "text": TextEngine,
    "json": JsonEngine,
    "yaml": YamlEngine,
    "yml": YamlEngine,
    "env": EnvEngine,
    "toml": TomlEngine,
    "ini": TextEngine,
    "xml": TextEngine,
    "properties": TextEngine,
}
