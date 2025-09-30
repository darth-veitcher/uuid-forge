# CLI Reference

UUID-Forge provides a powerful command-line interface for generating UUIDs and managing configurations.

## Installation and Setup

The CLI is installed automatically with UUID-Forge:

```bash
pip install uuid-forge
```

Verify installation:

```bash
uuid-forge --version
```

## Basic Usage

### Generate Single UUID

```bash
# Generate UUID from string
uuid-forge generate "user@example.com"

# Generate with custom namespace
uuid-forge generate "user@example.com" --namespace "users"

# Generate with specific version
uuid-forge generate "user@example.com" --version 5
```

### Output Formats

```bash
# Default hex format
uuid-forge generate "test"
# Output: 550e8400-e29b-41d4-a716-446655440000

# URN format
uuid-forge generate "test" --format urn
# Output: urn:uuid:550e8400-e29b-41d4-a716-446655440000

# Raw hex (no separators)
uuid-forge generate "test" --format hex --no-separators
# Output: 550e8400e29b41d4a716446655440000

# Uppercase
uuid-forge generate "test" --case upper
# Output: 550E8400-E29B-41D4-A716-446655440000
```

## Batch Operations

### Generate Multiple UUIDs

```bash
# From multiple arguments
uuid-forge generate "user1" "user2" "user3"

# From file (one input per line)
uuid-forge generate --input-file users.txt

# From stdin
echo -e "user1\nuser2\nuser3" | uuid-forge generate --stdin
```

### Output to File

```bash
# Save to file
uuid-forge generate "user1" "user2" --output results.txt

# Append to existing file
uuid-forge generate "user3" --output results.txt --append

# JSON output format
uuid-forge generate "user1" "user2" --output results.json --format-output json
```

## Configuration Management

### View Current Configuration

```bash
# Show all configuration
uuid-forge config show

# Show specific setting
uuid-forge config get namespace
```

### Set Configuration

```bash
# Set default namespace
uuid-forge config set namespace "my-app"

# Set default version
uuid-forge config set version 5

# Set output format
uuid-forge config set format hex
```

### Configuration Files

```bash
# Create configuration file
uuid-forge config init

# Use specific config file
uuid-forge --config /path/to/config.yaml generate "test"

# Validate configuration
uuid-forge config validate
```

## Advanced Features

### Namespace Management

```bash
# List available namespaces
uuid-forge namespace list

# Create custom namespace
uuid-forge namespace create "my-service" --parent users

# Generate with custom namespace
uuid-forge generate "test" --namespace-id 550e8400-e29b-41d4-a716-446655440000
```

### Templates and Presets

```bash
# Create preset
uuid-forge preset create "users" --namespace "users" --version 5 --format hex

# Use preset
uuid-forge generate "john@example.com" --preset users

# List presets
uuid-forge preset list

# Delete preset
uuid-forge preset delete "users"
```

## Validation and Testing

### Validate UUIDs

```bash
# Validate single UUID
uuid-forge validate 550e8400-e29b-41d4-a716-446655440000

# Validate multiple UUIDs
uuid-forge validate --input-file uuids.txt

# Check if UUID is deterministic
uuid-forge validate --check-deterministic "test-input" 550e8400-e29b-41d4-a716-446655440000
```

### Testing and Debugging

```bash
# Dry run (show what would be generated)
uuid-forge generate "test" --dry-run

# Verbose output
uuid-forge generate "test" --verbose

# Debug mode
uuid-forge generate "test" --debug
```

## Integration Examples

### Shell Scripts

```bash
#!/bin/bash

# Generate user UUID and store in variable
USER_UUID=$(uuid-forge generate "$USER_EMAIL" --namespace users)

# Use in database insert
psql -c "INSERT INTO users (id, email) VALUES ('$USER_UUID', '$USER_EMAIL')"
```

### Make Integration

```makefile
# Makefile
generate-test-uuids:
	uuid-forge generate --input-file test-users.txt --output test-uuids.txt

validate-uuids:
	uuid-forge validate --input-file production-uuids.txt
```

### CI/CD Pipeline

```yaml
# GitHub Actions
steps:
  - name: Generate UUIDs for testing
    run: |
      uuid-forge generate \
        --input-file test-data.txt \
        --output test-uuids.json \
        --format-output json \
        --namespace testing
```

## Command Reference

### Global Options

```bash
--config PATH          # Configuration file path
--namespace NAME       # Default namespace
--version {3,4,5}      # UUID version
--format {hex,urn,bytes} # Output format
--case {upper,lower}   # Case for hex output
--no-separators        # Remove separators from hex
--verbose              # Verbose output
--debug                # Debug mode
--help                 # Show help
```

### Subcommands

- `generate` - Generate UUIDs
- `config` - Manage configuration
- `namespace` - Manage namespaces
- `preset` - Manage presets
- `validate` - Validate UUIDs
- `version` - Show version information

## Environment Variables

```bash
# Configuration via environment
export UUID_FORGE_NAMESPACE="my-app"
export UUID_FORGE_VERSION=5
export UUID_FORGE_FORMAT="hex"
export UUID_FORGE_CASE="lower"
export UUID_FORGE_CONFIG_FILE="/path/to/config.yaml"
```

## Tips and Tricks

### Performance Optimization

```bash
# Use batch processing for large datasets
uuid-forge generate --input-file large-dataset.txt --batch-size 1000

# Parallel processing
cat users.txt | xargs -P 4 -I {} uuid-forge generate "{}" --namespace users
```

### Scripting

```bash
# Generate and format for SQL
uuid-forge generate "user@example.com" --format hex --case upper | \
sed "s/.*/INSERT INTO users (id) VALUES ('&');/"

# Check for duplicates
uuid-forge generate --input-file data.txt | sort | uniq -d
```

## Next Steps

- [Best Practices](best-practices.md) - Optimize your UUID generation
- [Use Cases](../use-cases/microservices.md) - Real-world applications
- [API Reference](../api/core.md) - Programmatic usage
