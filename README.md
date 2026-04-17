# ConfigDiff

**[English](README.md)** | **[简体中文](README_zh-CN.md)**

<p align="center">
  <strong>Multi-format configuration file diff and merge tool</strong><br>
  Zero-dependency Python CLI - diff JSON, YAML, TOML, .env, and more
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Dependencies-Zero-success.svg" alt="Zero Dependencies">
</p>

---

## What is ConfigDiff?

ConfigDiff is a lightweight, zero-dependency Python CLI tool for comparing configuration files across multiple formats. It provides intelligent, format-aware diffs that understand the structure of JSON, YAML, TOML, .env, and other config files.

**Key difference from `diff`**: Standard `diff` compares line-by-line. ConfigDiff understands your file's structure and shows meaningful differences at the semantic level.

## Features

- **Multi-format support**: JSON, YAML, TOML, .env, INI, XML, Properties, plain text
- **Structured diff**: Understands nested objects, arrays, key-value pairs
- **6 output formats**: Color terminal, plain text, JSON, Markdown, Git-style
- **Directory diff**: Compare entire config directories recursively
- **Zero dependencies**: Only Python 3.8+ stdlib (optional PyYAML for enhanced YAML)
- **CLI + Python API**: Use from command line or import as a library

## Quick Start

### Install

```bash
pip install configdiff
```

### Compare two config files

```bash
# YAML comparison
configdiff config_dev.yaml config_prod.yaml

# JSON comparison with JSON output
configdiff app.json app_new.json --format=json

# .env file comparison
configdiff .env.development .env.production

# Directory comparison
configdiff configs/staging/ configs/production/ --recursive
```

### Example output

```
--- config_dev.yaml
+++ config_prod.yaml
@@ -1,1 +1,1 @@
!  app.debug:
-    old: True
+    new: False
!  app.port:
-    old: 3000
+    new: 8080
+  + monitoring: {'enabled': True, 'endpoint': 'https://metrics.example.com'}

Summary: +1 added  ~2 changed
```

## CLI Reference

```bash
configdiff <left> <right> [options]

Options:
  -f, --format {color,plain,json,markdown,git}  Output format
  -o, --output FILE                             Write to file instead of stdout
  -c, --context N                               Context lines (default: 3)
  --ignore-order                                 Ignore array ordering
  --color {auto,always,never}                   Color output control
  -r, --recursive                               Recursively compare directories
  -q, --quiet                                   Only show summary
```

## Python API

```python
from configdiff import ConfigDiff

cd = ConfigDiff()

# Compare two files
result = cd.diff_file("config_a.yaml", "config_b.yaml")
print(result.changed)  # True if differences found
print(result.stats)    # {'added': 1, 'removed': 0, 'changed': 2}

# Format output
print(cd.format(result, format="color"))   # Terminal colors
print(cd.format(result, format="json"))    # JSON output
print(cd.format(result, format="markdown")) # Markdown report
```

## Supported Formats

| Format | Extension | Features |
|--------|-----------|----------|
| JSON | .json | Deep diff, array ordering options |
| YAML | .yaml, .yml | Structured diff (requires PyYAML) |
| TOML | .toml | Structured diff (requires tomli) |
| Environment | .env | Key-value diff, ignores comments |
| INI | .ini, .conf | Section-aware diff |
| XML | .xml | Text diff (structured coming soon) |
| Properties | .properties | Key-value diff |
| Text | any | Line-by-line diff |

## Design Philosophy

1. **Config-first**: Built specifically for configuration files, not general text
2. **Zero friction**: Works out of the box with no dependencies
3. **CI/CD ready**: JSON/Markdown output for automated reports
4. **Developer friendly**: Colored terminal output with clear visual hierarchy

## Roadmap

- [ ] 3-way merge support
- [ ] Interactive merge resolution
- [ ] XML structured diff
- [ ] Config validation against schema
- [ ] Web UI for visual diff

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file.

---

Made with ❤️ by [gitstq](https://github.com/gitstq)
