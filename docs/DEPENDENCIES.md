# FivcGlue Dependencies

This document describes the dependencies used in FivcGlue and how to manage them.

## 📦 Dependency Overview

FivcGlue is designed to be lightweight with minimal required dependencies. Most dependencies are optional and only needed for specific features.

### Required Dependencies

**None** - FivcGlue core has zero required dependencies!

The core functionality works with Python standard library only.

### Optional Dependencies

#### YAML Support
- **PyYAML >= 6.0.1**
- Required for: YAML configuration file support
- Install with: `uv sync --extra yaml` or `pip install fivcglue[yaml]`

### Development Dependencies

Development dependencies are only needed if you're contributing to FivcGlue:

- **pytest >= 8.2.0** - Testing framework
- **pytest-asyncio >= 0.21.0** - Async test support
- **pytest-cov >= 4.1.0** - Code coverage reporting
- **ruff >= 0.4.0** - Linting and formatting

Install with: `make dev` or `uv sync --extra dev`

## 🚀 Installation Methods

### Method 1: UV Package Manager (Recommended)

UV is a fast Python package manager written in Rust.

**Install UV:**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

**Install FivcGlue:**
```bash
# Minimal installation (no dependencies)
uv sync

# With YAML support
uv sync --extra yaml

# With development dependencies
uv sync --extra dev

# With all extras
uv sync --extra dev --extra yaml

# Or use Make commands
make install      # dev + yaml
make install-min  # minimal only
```

### Method 2: pip

**Basic installation:**
```bash
pip install -e .
```

**With optional dependencies:**
```bash
# YAML support
pip install -e ".[yaml]"

# Development dependencies
pip install -e ".[dev]"

# All extras
pip install -e ".[dev,yaml]"
```

## 🔧 Managing Dependencies

### Adding New Dependencies

#### Runtime Dependencies

If adding a new **required** dependency (avoid if possible):

```toml
# pyproject.toml
[project]
dependencies = [
  "new-package>=1.0.0",
]
```

If adding an **optional** dependency:

```toml
# pyproject.toml
[project.optional-dependencies]
feature-name = ["new-package>=1.0.0"]
```

#### Development Dependencies

```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
  "pytest>=8.2.0",
  "new-dev-tool>=1.0.0",  # Add here
]
```

### Updating Dependencies

**With UV:**
```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv pip install --upgrade package-name
```

**With pip:**
```bash
pip install --upgrade package-name
```

### Checking Dependencies

```bash
# List installed packages
uv pip list

# Show dependency tree
uv pip tree

# Check for outdated packages
uv pip list --outdated
```

## 🎯 Dependency Philosophy

FivcGlue follows these principles for dependency management:

### 1. Minimal Core Dependencies

The core package should work with **zero external dependencies** when possible. This:
- Reduces installation size
- Minimizes security vulnerabilities
- Improves compatibility
- Speeds up installation

### 2. Optional Features

Features requiring external packages should be **optional**:

```python
# Good: Optional import with fallback
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

class YAMLFileConfig:
    def __init__(self, path):
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required. Install with: pip install fivcglue[yaml]")
        # Implementation
```

### 3. Conservative Version Pinning

Use **minimum version constraints** rather than exact versions:

```toml
# Good: Allows newer compatible versions
dependencies = ["package>=1.0.0"]

# Avoid: Too restrictive
dependencies = ["package==1.0.0"]
```

### 4. Development vs Runtime

Keep development dependencies separate:
- **Runtime**: Only what users need to use the package
- **Development**: Testing, linting, documentation tools

## 🔍 Dependency Details

### PyYAML (Optional)

**Purpose**: YAML file parsing for configuration

**Why optional**: Not all users need YAML support. JSON is available in stdlib.

**Usage:**
```python
from fivcglue.implements import YAMLFileConfig

config = YAMLFileConfig("config.yml")
```

**Alternatives**: Use `JSONFileConfig` if you don't want to install PyYAML.

### pytest (Dev)

**Purpose**: Testing framework

**Why needed**: Running the test suite

**Usage:**
```bash
make test
# or
uv run pytest
```

### ruff (Dev)

**Purpose**: Fast Python linter and formatter

**Why needed**: Code quality and consistency

**Usage:**
```bash
make lint    # Check code
make format  # Format code
```

## 🐛 Troubleshooting

### UV Installation Issues

**Problem**: UV not found after installation

**Solution**:
```bash
# Add to PATH (macOS/Linux)
export PATH="$HOME/.cargo/bin:$PATH"

# Or reinstall
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### PyYAML Import Error

**Problem**: `ImportError: No module named 'yaml'`

**Solution**:
```bash
# Install YAML support
uv sync --extra yaml
# or
pip install "fivcglue[yaml]"
```

### Dependency Conflicts

**Problem**: Package version conflicts

**Solution**:
```bash
# Clear cache and reinstall
uv cache clean
uv sync --reinstall
```

## 📚 Further Reading

- [UV Documentation](https://github.com/astral-sh/uv)
- [Python Packaging Guide](https://packaging.python.org/)
- [PEP 621 - Project Metadata](https://peps.python.org/pep-0621/)
- [Semantic Versioning](https://semver.org/)

