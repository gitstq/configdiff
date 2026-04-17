# ConfigDiff

**[English](README.md)** | **[简体中文](README_zh-CN.md)**

<p align="center">
  <strong>多格式配置文件比对与合并工具</strong><br>
  零依赖 Python CLI - 支持 JSON、YAML、TOML、.env 等多种格式
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Dependencies-Zero-success.svg" alt="Zero Dependencies">
</p>

---

## 项目介绍

ConfigDiff 是一个轻量级、零依赖的 Python CLI 工具，用于比对多种格式的配置文件。它提供智能、格式感知的差异比对，能够理解 JSON、YAML、TOML、.env 等配置文件的结构。

**与标准 `diff` 的区别**：标准 `diff` 逐行比较。ConfigDiff 理解文件结构，在语义层面展示有意义的差异。

## 核心特性

- **多格式支持**：JSON、YAML、TOML、.env、INI、XML、Properties、纯文本
- **结构化差异**：理解嵌套对象、数组、键值对
- **6 种输出格式**：彩色终端、纯文本、JSON、Markdown、Git 风格
- **目录比对**：递归比对整个配置目录
- **零依赖**：仅需 Python 3.8+ 标准库（可选 PyYAML 增强 YAML 支持）
- **CLI + Python API**：命令行或库两种使用方式

## 快速开始

### 安装

```bash
pip install configdiff
```

### 比对两个配置文件

```bash
# YAML 比对
configdiff config_dev.yaml config_prod.yaml

# JSON 比对，输出 JSON 格式
configdiff app.json app_new.json --format=json

# .env 文件比对
configdiff .env.development .env.production

# 目录比对
configdiff configs/staging/ configs/production/ --recursive
```

### 示例输出

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

## CLI 参考

```bash
configdiff <left> <right> [options]

选项：
  -f, --format {color,plain,json,markdown,git}  输出格式
  -o, --output FILE                             输出到文件而非终端
  -c, --context N                               上下文行数（默认：3）
  --ignore-order                                 忽略数组顺序差异
  --color {auto,always,never}                   颜色输出控制
  -r, --recursive                               递归比对目录
  -q, --quiet                                   仅显示摘要
```

## Python API

```python
from configdiff import ConfigDiff

cd = ConfigDiff()

# 比对两个文件
result = cd.diff_file("config_a.yaml", "config_b.yaml")
print(result.changed)  # 如有差异返回 True
print(result.stats)    # {'added': 1, 'removed': 0, 'changed': 2}

# 格式化输出
print(cd.format(result, format="color"))    # 终端彩色输出
print(cd.format(result, format="json"))     # JSON 输出
print(cd.format(result, format="markdown")) # Markdown 报告
```

## 支持的格式

| 格式 | 扩展名 | 特性 |
|------|--------|------|
| JSON | .json | 深度比对，数组排序选项 |
| YAML | .yaml, .yml | 结构化比对（需要 PyYAML） |
| TOML | .toml | 结构化比对（需要 tomli） |
| 环境变量 | .env | 键值比对，忽略注释 |
| INI | .ini, .conf | 分区感知比对 |
| XML | .xml | 文本比对（结构化即将支持） |
| Properties | .properties | 键值比对 |
| 文本 | 任意 | 逐行比对 |

## 设计思想

1. **配置优先**：专为配置文件设计，非通用文本工具
2. **零摩擦**：开箱即用，无需依赖
3. **CI/CD 就绪**：JSON/Markdown 输出适合自动化报告
4. **开发者友好**：彩色终端输出，清晰的视觉层次

## 迭代规划

- [ ] 三路合并支持
- [ ] 交互式合并解决
- [ ] XML 结构化比对
- [ ] 基于 Schema 的配置校验
- [ ] Web UI 可视化比对

## 贡献指南

参见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 开源协议

MIT 协议 - 详见 [LICENSE](LICENSE) 文件。

---

由 [gitstq](https://github.com/gitstq) 用 ❤️ 制作
