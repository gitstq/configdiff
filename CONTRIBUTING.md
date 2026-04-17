# Contributing to ConfigDiff

Thank you for your interest in contributing to ConfigDiff!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/configdiff.git`
3. Install in development mode: `pip install -e ".[dev]"`
4. Run tests: `python tests/test_configdiff.py`

## Development Guidelines

- Python 3.8+ compatibility
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation for API changes

## Commit Messages

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions/changes

## Adding a New Format Engine

1. Create engine class in `configdiff/engines.py`
2. Register in `_ENGINES` dict
3. Add format detection in `core.py`
4. Add tests in `tests/test_configdiff.py`

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
