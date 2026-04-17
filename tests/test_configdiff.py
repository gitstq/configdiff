"""
ConfigDiff Test Suite.
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from configdiff import ConfigDiff
from configdiff.engines import get_engine, TextEngine, JsonEngine, EnvEngine
from configdiff.core import FileData


def test_import():
    from configdiff import __version__
    assert __version__ == "1.0.0"
    print(f"import OK - ConfigDiff v{__version__}")


def test_text_engine():
    eng = TextEngine()
    left = FileData("a.txt", "hello\nworld\nfoo", "text", ["hello","world","foo"])
    right = FileData("b.txt", "hello\nplanet\nfoo\nbar", "text", ["hello","planet","foo","bar"])
    cd = ConfigDiff()
    result = eng.diff(cd, left, right)
    assert result.changed == True
    assert result.stats['added'] >= 1
    assert result.stats['removed'] >= 1
    print(f"text_engine OK - added:{result.stats['added']} removed:{result.stats['removed']}")


def test_json_engine():
    eng = JsonEngine()
    left = FileData("a.json", '{"a":1,"b":2}', "json", ['{"a":1,"b":2}'])
    right = FileData("b.json", '{"a":1,"b":3,"c":4}', "json", ['{"a":1,"b":3,"c":4}'])
    cd = ConfigDiff()
    result = eng.diff(cd, left, right)
    assert result.changed == True
    assert result.stats['changed'] >= 1
    print(f"json_engine OK - changed:{result.stats['changed']}")


def test_json_deep_diff():
    eng = JsonEngine()
    cd = ConfigDiff()
    left = FileData("a.json", json.dumps({"user":{"name":"Alice","age":30,"email":"alice@example.com"}}), "json", [])
    right = FileData("b.json", json.dumps({"user":{"name":"Alice","age":31,"email":"alice@new.com"}}), "json", [])
    result = eng.diff(cd, left, right)
    assert result.changed == True
    print(f"json_deep_diff OK - {result.stats}")


def test_env_engine():
    eng = EnvEngine()
    left = FileData("a.env", "DEBUG=true\nPORT=3000\nDB=localhost", "env",
                    ["DEBUG=true","PORT=3000","DB=localhost"])
    right = FileData("b.env", "DEBUG=false\nPORT=8080\nDB=prod.db\nTZ=UTC", "env",
                    ["DEBUG=false","PORT=8080","DB=prod.db","TZ=UTC"])
    cd = ConfigDiff()
    result = eng.diff(cd, left, right)
    assert result.changed == True
    print(f"env_engine OK - {result.stats}")


def test_env_no_comments():
    eng = EnvEngine()
    cd = ConfigDiff()
    lines_l = ["DEBUG=true", "PORT=3000"]
    lines_r = ["DEBUG=false", "PORT=8080"]
    left = FileData("a.env", "\n".join(lines_l), "env", lines_l)
    right = FileData("b.env", "\n".join(lines_r), "env", lines_r)
    result = eng.diff(cd, left, right)
    assert result.changed == True
    print(f"env_no_comments OK")


def test_format_no_changes():
    cd = ConfigDiff()
    left = FileData("a.txt", "same\ncontent", "text", ["same","content"])
    right = FileData("b.txt", "same\ncontent", "text", ["same","content"])
    result = cd.diff(left, right)
    assert result.changed == False
    assert result.stats['added'] == 0
    assert result.stats['removed'] == 0
    print(f"format_no_changes OK")


def test_format_plain():
    cd = ConfigDiff()
    left = FileData("a.txt", "hello", "text", ["hello"])
    right = FileData("b.txt", "world", "text", ["world"])
    result = cd.diff(left, right)
    plain = cd.format(result, format="plain")
    assert "hello" in plain or "world" in plain
    assert "No differences" not in plain
    print(f"format_plain OK")


def test_format_json():
    cd = ConfigDiff()
    left = FileData("a.json", '{"key":"a"}', "json", ['{"key":"a"}'])
    right = FileData("b.json", '{"key":"b"}', "json", ['{"key":"b"}'])
    result = cd.diff(left, right)
    json_out = cd.format(result, format="json")
    data = json.loads(json_out)
    assert data["changed"] == True
    assert "key" in json_out
    print(f"format_json OK")


def test_format_markdown():
    cd = ConfigDiff()
    left = FileData("a.json", '{"v":1}', "json", ['{"v":1}'])
    right = FileData("b.json", '{"v":2}', "json", ['{"v":2}'])
    result = cd.diff(left, right)
    md = cd.format(result, format="markdown")
    assert "Diff:" in md
    assert result.stats['changed'] >= 1
    print(f"format_markdown OK")


def test_format_color():
    cd = ConfigDiff()
    left = FileData("a.txt", "old", "text", ["old"])
    right = FileData("b.txt", "new", "text", ["new"])
    result = cd.diff(left, right)
    color_out = cd.format(result, format="color")
    assert "\033[" in color_out  # ANSI codes
    print(f"format_color OK")


def test_format_markdown_no_changes():
    cd = ConfigDiff()
    left = FileData("a.json", '{"same":true}', "json", ['{"same":true}'])
    right = FileData("b.json", '{"same":true}', "json", ['{"same":true}'])
    result = cd.diff(left, right)
    md = cd.format(result, format="markdown")
    assert "No differences" in md
    print(f"format_markdown_no_changes OK")


def test_engine_registry():
    assert isinstance(get_engine("json", "json"), JsonEngine)
    assert isinstance(get_engine("text", "text"), TextEngine)
    assert isinstance(get_engine("env", "env"), EnvEngine)
    # Cross-format falls back to text
    t = get_engine("json", "yaml")
    assert isinstance(t, TextEngine)
    print(f"engine_registry OK")


def test_format_detect():
    cd = ConfigDiff()
    assert cd._detect_format("config.yaml", "a: 1\nb: 2") == "yaml"
    assert cd._detect_format("data.json", '{"x":1}') == "json"
    assert cd._detect_format(".env", "KEY=value") == "env"
    assert cd._detect_format(".env.local", "KEY=value") == "env"
    assert cd._detect_format("app.toml", "[section]") == "toml"
    assert cd._detect_format("app.ini", "[section]") == "ini"
    assert cd._detect_format("config.xml", "<config>") == "xml"
    print(f"format_detect OK")


def test_ignore_order():
    cd = ConfigDiff(ignore_order=True)
    left = FileData("a.json", json.dumps({"items":[1,2,3]}), "json", [])
    right = FileData("b.json", json.dumps({"items":[3,1,2]}), "json", [])
    # With ignore_order, same values in different order should be equal
    # The JsonEngine does deep diff
    result = cd.diff(left, right)
    print(f"ignore_order test - stats: {result.stats}")


def test_no_change_summary():
    cd = ConfigDiff()
    left = FileData("a.json", '{"a":1,"b":2}', "json", [])
    right = FileData("b.json", '{"b":2,"a":1}', "json", [])  # same keys/values, different order
    result = cd.diff(left, right)
    # Should report changes since order differs in text but same in json
    print(f"no_change_summary OK - stats: {result.stats}")


def test_dummy_file():
    """Verify we can diff file pairs from disk."""
    cd = ConfigDiff()
    base = Path(r"C:\Users\26979\AppData\Local\Temp\configdiff_dev\examples")
    left = FileData("examples/config_dev.yaml",
                    (base / "config_dev.yaml").read_text(encoding="utf-8"),
                    "yaml", [])
    right = FileData("examples/config_prod.yaml",
                     (base / "config_prod.yaml").read_text(encoding="utf-8"),
                     "yaml", [])
    result = cd.diff(left, right)
    assert result.changed == True
    assert result.stats['added'] >= 1
    # At least one change detected
    assert result.stats['changed'] >= 1 or result.stats['added'] >= 1 or result.stats['removed'] >= 1
    plain = cd.format(result, format="plain")
    assert "myapp" in plain or "debug" in plain.lower()
    print(f"yaml_file_diff OK - added:{result.stats['added']} removed:{result.stats['removed']} changed:{result.stats['changed']}")


def run_all():
    print("\n" + "="*50)
    print("  ConfigDiff Test Suite")
    print("="*50 + "\n")
    tests = [
        test_import,
        test_text_engine,
        test_json_engine,
        test_json_deep_diff,
        test_env_engine,
        test_env_no_comments,
        test_format_no_changes,
        test_format_plain,
        test_format_json,
        test_format_markdown,
        test_format_color,
        test_format_markdown_no_changes,
        test_engine_registry,
        test_format_detect,
        test_ignore_order,
        test_no_change_summary,
        test_dummy_file,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"FAIL {t.__name__}: {e}")
            import traceback; traceback.print_exc()
            failed += 1
    print(f"\n{'='*50}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'='*50}\n")
    return failed == 0


if __name__ == "__main__":
    ok = run_all()
    sys.exit(0 if ok else 1)
