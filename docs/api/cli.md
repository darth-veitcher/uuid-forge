# CLI API Reference

Complete reference for UUID-Forge command-line interface.

## CLI Functions

The UUID-Forge CLI provides command-line access to UUID generation functionality.

::: uuid_forge.cli.app
options:
show_root_heading: true
show_source: false
heading_level: 3

## Main Commands

### generate

Generate UUIDs from input data.

```bash
uuid-forge generate [OPTIONS] [INPUTS]...
```

**Arguments:**

- `INPUTS`: Input data for UUID generation (strings, files, etc.)

**Options:**

- `--namespace TEXT`: Namespace to use for generation
- `--version {3,4,5}`: UUID version (default: 5)
- `--format {hex,urn,bytes}`: Output format (default: hex)
- `--case {upper,lower}`: Case for hex output (default: lower)
- `--separator TEXT`: Separator for hex format (default: -)
- `--input-file PATH`: Read inputs from file
- `--output PATH`: Write output to file
- `--stdin`: Read from standard input
- `--verbose`: Verbose output
- `--help`: Show help message

**Examples:**

```bash
# Generate single UUID
uuid-forge generate "user@example.com"

# Generate with custom namespace
uuid-forge generate "user@example.com" --namespace users

# Generate multiple UUIDs
uuid-forge generate "user1" "user2" "user3"

# From file
uuid-forge generate --input-file users.txt

# From stdin
echo "test-data" | uuid-forge generate --stdin

# Custom format
uuid-forge generate "test" --format urn --case upper
```

### config

Manage configuration settings.

```bash
uuid-forge config [SUBCOMMAND] [OPTIONS]
```

**Subcommands:**

- `show`: Display current configuration
- `get KEY`: Get specific configuration value
- `set KEY VALUE`: Set configuration value
- `init`: Create default configuration file
- `validate`: Validate configuration

**Examples:**

```bash
# Show all configuration
uuid-forge config show

# Get specific setting
uuid-forge config get namespace

# Set configuration
uuid-forge config set namespace "my-app"
uuid-forge config set version 5

# Create config file
uuid-forge config init

# Validate configuration
uuid-forge config validate
```

### validate

Validate UUIDs and check deterministic generation.

```bash
uuid-forge validate [OPTIONS] [UUIDS]...
```

**Options:**

- `--input-file PATH`: Read UUIDs from file
- `--check-deterministic INPUT UUID`: Check if UUID matches expected for input
- `--format {hex,urn}`: Expected UUID format
- `--verbose`: Verbose validation output

**Examples:**

```bash
# Validate single UUID
uuid-forge validate 550e8400-e29b-41d4-a716-446655440000

# Validate multiple UUIDs
uuid-forge validate uuid1 uuid2 uuid3

# Validate from file
uuid-forge validate --input-file uuids.txt

# Check deterministic generation
uuid-forge validate --check-deterministic "test-input" 550e8400-e29b-41d4-a716-446655440000
```

### namespace

Manage namespaces for UUID generation.

```bash
uuid-forge namespace [SUBCOMMAND] [OPTIONS]
```

**Subcommands:**

- `list`: List available namespaces
- `create NAME`: Create new namespace
- `delete NAME`: Delete namespace
- `show NAME`: Show namespace details

**Examples:**

```bash
# List namespaces
uuid-forge namespace list

# Create namespace
uuid-forge namespace create "my-service"

# Show namespace details
uuid-forge namespace show "my-service"

# Delete namespace
uuid-forge namespace delete "my-service"
```

## Global Options

Available for all commands:

- `--config PATH`: Configuration file path
- `--verbose`: Enable verbose logging
- `--quiet`: Suppress output except errors
- `--debug`: Enable debug mode
- `--version`: Show version information
- `--help`: Show help message

## Configuration

### Configuration File

The CLI looks for configuration in:

1. Path specified by `--config` option
2. `uuid_forge.yaml` in current directory
3. `~/.uuid_forge.yaml` in user home
4. `/etc/uuid_forge.yaml` system-wide

### Environment Variables

All CLI options can be set via environment variables:

```bash
export UUID_FORGE_NAMESPACE="my-app"
export UUID_FORGE_VERSION=5
export UUID_FORGE_FORMAT="hex"
export UUID_FORGE_CASE="lower"
export UUID_FORGE_CONFIG_FILE="/path/to/config.yaml"
```

## Output Formats

### Standard Output

Default output format for generated UUIDs:

```bash
$ uuid-forge generate "test1" "test2"
550e8400-e29b-41d4-a716-446655440000
550e8400-e29b-41d4-a716-446655440001
```

### JSON Output

Use `--format-output json` for structured output:

```bash
$ uuid-forge generate "test1" "test2" --format-output json
[
  {
    "input": "test1",
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "namespace": "default",
    "version": 5
  },
  {
    "input": "test2",
    "uuid": "550e8400-e29b-41d4-a716-446655440001",
    "namespace": "default",
    "version": 5
  }
]
```

### CSV Output

Use `--format-output csv` for CSV format:

```bash
$ uuid-forge generate "test1" "test2" --format-output csv
input,uuid,namespace,version
test1,550e8400-e29b-41d4-a716-446655440000,default,5
test2,550e8400-e29b-41d4-a716-446655440001,default,5
```

## Error Handling

### Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid arguments
- `3`: Configuration error
- `4`: Validation error

### Error Messages

```bash
$ uuid-forge generate --version 99
Error: Invalid UUID version: 99. Must be 3, 4, or 5.

$ uuid-forge validate "invalid-uuid"
Error: Invalid UUID format: invalid-uuid

$ uuid-forge config get nonexistent
Error: Configuration key 'nonexistent' not found.
```

## Batch Processing

### Large Datasets

For processing large datasets efficiently:

```bash
# Process in batches
uuid-forge generate --input-file large-dataset.txt --batch-size 1000

# Parallel processing
cat users.txt | xargs -P 4 -I {} uuid-forge generate "{}" --namespace users
```

### Input File Formats

Supported input file formats:

**Plain text (one input per line):**

```
user1@example.com
user2@example.com
user3@example.com
```

**JSON lines:**

```json
{"email": "user1@example.com", "name": "User 1"}
{"email": "user2@example.com", "name": "User 2"}
```

**CSV:**

```csv
email,name
user1@example.com,User 1
user2@example.com,User 2
```

## Integration Examples

### Shell Scripts

```bash
#!/bin/bash

# Generate UUID and use in script
USER_UUID=$(uuid-forge generate "$USER_EMAIL" --namespace users)
echo "Generated UUID for $USER_EMAIL: $USER_UUID"

# Validate UUIDs in file
if uuid-forge validate --input-file production-uuids.txt; then
    echo "All UUIDs are valid"
else
    echo "Some UUIDs are invalid"
    exit 1
fi
```

### Makefile Integration

```makefile
# Generate test UUIDs
generate-test-data:
	uuid-forge generate --input-file test-users.txt --output test-uuids.txt

# Validate production UUIDs
validate-prod:
	uuid-forge validate --input-file prod-uuids.txt

# Clean up generated files
clean:
	rm -f test-uuids.txt generated-*.txt
```

### CI/CD Pipelines

```yaml
# GitHub Actions
name: UUID Validation
on: [push, pull_request]

jobs:
  validate-uuids:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install UUID-Forge
        run: pip install uuid-forge

      - name: Generate test UUIDs
        run: |
          uuid-forge generate --input-file test-data.txt --output test-uuids.txt

      - name: Validate UUIDs
        run: |
          uuid-forge validate --input-file test-uuids.txt
```

## Debugging and Troubleshooting

### Verbose Mode

Use `--verbose` for detailed output:

```bash
$ uuid-forge generate "test" --verbose
INFO: Using namespace: default
INFO: UUID version: 5
INFO: Input data: test
INFO: Generated UUID: 550e8400-e29b-41d4-a716-446655440000
```

### Debug Mode

Use `--debug` for maximum detail:

```bash
$ uuid-forge generate "test" --debug
DEBUG: Configuration loaded from: /home/user/.uuid_forge.yaml
DEBUG: Namespace resolved to: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
DEBUG: Input preprocessing: test -> test
DEBUG: Hash algorithm: SHA-1
DEBUG: Generated UUID: 550e8400-e29b-41d4-a716-446655440000
```

### Common Issues

**Issue: "Command not found"**

```bash
# Solution: Ensure UUID-Forge is installed and in PATH
pip install uuid-forge
which uuid-forge
```

**Issue: "Invalid UUID version"**

```bash
# Solution: Use valid version (3, 4, or 5)
uuid-forge generate "test" --version 5
```

**Issue: "Configuration file not found"**

```bash
# Solution: Create configuration or specify path
uuid-forge config init
# or
uuid-forge --config /path/to/config.yaml generate "test"
```

## Performance Considerations

### Optimization Tips

1. **Reuse configuration**: Use config files instead of passing options repeatedly
2. **Batch processing**: Process multiple inputs in single command
3. **Output to file**: Use `--output` instead of shell redirection for large datasets
4. **Parallel processing**: Use `xargs -P` for CPU-intensive operations

### Benchmarking

```bash
# Time single generation
time uuid-forge generate "test"

# Time batch generation
time uuid-forge generate --input-file large-dataset.txt

# Memory usage
/usr/bin/time -v uuid-forge generate --input-file large-dataset.txt
```
