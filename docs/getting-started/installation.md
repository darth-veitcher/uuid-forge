# Installation

UUID-Forge can be installed using various package managers. Choose the method that best fits your workflow.

## Requirements

- Python 3.11 or higher
- pip, uv, or poetry (depending on your preferred installation method)

## Installation Methods

### Using uv (Recommended)

```bash
uv add uuid-forge
```

### Using pip

```bash
pip install uuid-forge
```

### Using poetry

```bash
poetry add uuid-forge
```

### Development Installation

If you want to contribute to UUID-Forge or install from source:

```bash
# Clone the repository
git clone https://github.com/yourusername/uuid-forge.git
cd uuid-forge

# Install in development mode
uv sync --dev
```

## Verification

Verify your installation by running:

```bash
python -c "import uuid_forge; print(uuid_forge.__version__)"
```

Or use the CLI:

```bash
uuid-forge --version
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Get up and running in 5 minutes
- [Configuration](configuration.md) - Learn about configuration options
