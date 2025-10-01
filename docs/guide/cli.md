# CLI Reference

UUID-Forge provides a powerful command-line interface for generating deterministic UUIDs, managing configuration, and validating security settings.

## Installation

The CLI is installed automatically with UUID-Forge:

```bash
pip install uuid-forge
```

or with uv:

```bash
uv add uuid-forge
```

## Available Commands

UUID-Forge CLI provides the following commands:

- `generate` - Generate deterministic UUIDs
- `extract` - Extract UUID from prefixed identifiers
- `new-salt` - Generate cryptographic salt
- `init` - Initialize configuration file
- `validate` - Validate security configuration
- `info` - Display configuration information
- `docs` - Build or serve documentation
- `test` - Run test suite

## Generate Command

Generate a deterministic UUID for an entity.

### Basic Usage

```bash
uuid-forge generate ENTITY_TYPE --attr key=value
```

### Arguments

- `ENTITY_TYPE` - Type of entity (e.g., 'invoice', 'order', 'user') **[required]**

### Options

- `--attr, -a` - Attributes in key=value format (can be used multiple times)
- `--prefix, -p` - Human-readable prefix for the UUID
- `--separator, -s` - Separator between prefix and UUID (default: -)
- `--namespace, -n` - Custom namespace domain (e.g., 'mycompany.com')
- `--salt` - Cryptographic salt (leave empty to use environment variable)
- `--env/--no-env` - Load configuration from environment variables (default: env)

### Examples

#### Simple Generation

```bash
# Generate user UUID from email
uuid-forge generate user --attr email=alice@example.com

# Generate invoice UUID with multiple attributes
uuid-forge generate invoice --attr region=EUR --attr number=12345
```

#### With Prefix

```bash
# Generate with human-readable prefix
uuid-forge generate invoice --prefix INV-EUR --attr region=EUR --attr number=12345
# Output: INV-EUR-550e8400-e29b-41d4-a716-446655440000
```

#### Custom Configuration

```bash
# Custom namespace and salt
uuid-forge generate user \
  --namespace mycompany.com \
  --salt "my-secret" \
  --attr email=user@example.com
```

#### Using Environment Variables

```bash
# Set configuration via environment
export UUID_FORGE_SALT="xvW9Kz_kRzPmNqYvTaWcXdYeFgZhAiB"
export UUID_FORGE_NAMESPACE="mycompany.com"

# Generate using environment config
uuid-forge generate invoice --attr region=EUR --attr number=12345
```

## Extract Command

Extract the UUID portion from a prefixed identifier.

### Usage

```bash
uuid-forge extract PREFIXED_ID
```

### Example

```bash
uuid-forge extract "INV-EUR-550e8400-e29b-41d4-a716-446655440000"
# Output: 550e8400-e29b-41d4-a716-446655440000
```

## New-Salt Command

Generate a new cryptographically secure salt.

### Usage

```bash
uuid-forge new-salt
```

### Example

```bash
# Generate a new salt
uuid-forge new-salt
# Output: xvW9Kz_kRzPmNqYvTaWcXdYeFgZhAiB

# Save to environment variable
export UUID_FORGE_SALT=$(uuid-forge new-salt)
```

## Init Command

Initialize a new configuration file with a generated salt.

### Usage

```bash
uuid-forge init
```

### Example

```bash
# Create .env file with UUID_FORGE_SALT
uuid-forge init

# Or specify custom file
uuid-forge init --file config/.env
```

## Validate Command

Validate your current configuration for security best practices.

### Usage

```bash
uuid-forge validate
```

### Example

```bash
# Validate environment configuration
export UUID_FORGE_SALT="xvW9Kz_kRzPmNqYvTaWcXdYeFgZhAiB"
export UUID_FORGE_NAMESPACE="mycompany.com"
uuid-forge validate

# Output will show:
# ✅ Salt is set and has adequate entropy
# ✅ Namespace is configured
# ✅ Configuration is secure
```

## Info Command

Display information about your current configuration and usage.

### Usage

```bash
uuid-forge info
```

### Example

```bash
uuid-forge info
# Output:
# UUID-Forge Configuration
# ------------------------
# Namespace: mycompany.com
# Salt: ***configured***
# Version: 0.1.0
```

## Docs Command

Build or serve the documentation locally.

### Usage

```bash
uuid-forge docs [serve|build]
```

### Examples

```bash
# Serve docs locally at http://127.0.0.1:8000
uuid-forge docs serve

# Build docs to site/ directory
uuid-forge docs build
```

## Test Command

Run the test suite with pytest.

### Usage

```bash
uuid-forge test
```

### Examples

```bash
# Run all tests
uuid-forge test

# Run with coverage
uuid-forge test --cov

# Run specific test file
uuid-forge test tests/test_core.py
```

## Environment Variables

UUID-Forge supports configuration via environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `UUID_FORGE_SALT` | Cryptographic salt for UUID generation | `xvW9Kz_kRzPmNqYvTaWcXdYeFgZhAiB` |
| `UUID_FORGE_NAMESPACE` | Default namespace domain | `mycompany.com` |

### Setting Environment Variables

```bash
# Linux/macOS
export UUID_FORGE_SALT="your-salt-here"
export UUID_FORGE_NAMESPACE="mycompany.com"

# Windows (PowerShell)
$env:UUID_FORGE_SALT="your-salt-here"
$env:UUID_FORGE_NAMESPACE="mycompany.com"

# Or use a .env file
echo "UUID_FORGE_SALT=your-salt-here" > .env
echo "UUID_FORGE_NAMESPACE=mycompany.com" >> .env
```

## Common Workflows

### First-Time Setup

```bash
# 1. Generate a secure salt
uuid-forge new-salt

# 2. Initialize configuration
uuid-forge init

# 3. Validate setup
uuid-forge validate

# 4. Generate your first UUID
uuid-forge generate user --attr email=test@example.com
```

### CI/CD Pipeline

```bash
# Set configuration in CI environment
export UUID_FORGE_SALT="${SECRET_SALT}"
export UUID_FORGE_NAMESPACE="mycompany.com"

# Generate UUIDs in pipeline
uuid-forge generate deployment \
  --attr branch="${CI_BRANCH}" \
  --attr commit="${CI_COMMIT_SHA}" \
  --attr timestamp="$(date -Iseconds)"
```

### Development Workflow

```bash
# Use environment-specific configuration
export UUID_FORGE_NAMESPACE="dev.mycompany.com"
export UUID_FORGE_SALT="${DEV_SALT}"

# Generate test data
uuid-forge generate user --attr email=dev@example.com
uuid-forge generate order --attr id=12345 --attr region=test
```

## Error Handling

### Missing Configuration

```bash
$ uuid-forge generate user --attr email=test@example.com
Error: UUID_FORGE_SALT environment variable not set
Solution: Run 'uuid-forge init' or set UUID_FORGE_SALT manually
```

### Invalid Attribute Format

```bash
$ uuid-forge generate user --attr email:test@example.com
Error: Invalid attribute format: email:test@example.com
Use key=value format.
```

## Tips and Tricks

### 1. Use Shell Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias uuid='uuid-forge generate'

# Usage
uuid user --attr email=alice@example.com
```

### 2. Batch Generation with xargs

```bash
# Generate UUIDs for multiple emails
cat emails.txt | xargs -I {} uuid-forge generate user --attr email={}
```

### 3. Integration with jq

```bash
# Generate UUID and create JSON
USER_UUID=$(uuid-forge generate user --attr email=alice@example.com)
echo "{\"id\": \"$USER_UUID\", \"email\": \"alice@example.com\"}" | jq .
```

## Next Steps

- [Basic Usage Guide](basic-usage.md) - Learn the Python API
- [Best Practices](best-practices.md) - Production configuration
- [Configuration Guide](../getting-started/configuration.md) - Detailed setup
