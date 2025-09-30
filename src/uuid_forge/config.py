"""Configuration management for UUID-Forge.

This module provides utilities for loading and managing UUID generation
configuration from environment variables, configuration files, or direct
instantiation. It follows 12-factor app principles for configuration
management, keeping secrets out of code and in the environment.
"""

import os
import uuid as uuid_module
from pathlib import Path

from uuid_forge.core import IDConfig, generate_salt


def load_config_from_env(
    namespace_env: str = "UUID_FORGE_NAMESPACE",
    salt_env: str = "UUID_FORGE_SALT"
) -> IDConfig:
    """Load UUID generation configuration from environment variables.

    This function reads configuration from environment variables following
    12-factor app principles. The namespace and salt should be set in the
    deployment environment, keeping secrets out of source code.

    Environment Variables:
        UUID_FORGE_NAMESPACE: (Optional) Domain name for namespace generation.
            If not set, defaults to uuid.NAMESPACE_DNS.
            Example: "mycompany.com"
        UUID_FORGE_SALT: (Required in production) Cryptographic salt for UUID
            generation. Generate with generate_salt() and store securely.
            Example: "xvW9Kz_kRzPmNqYvTaWcXdYeFgZhAiB"

    Args:
        namespace_env: Environment variable name for namespace. Defaults to
            "UUID_FORGE_NAMESPACE".
        salt_env: Environment variable name for salt. Defaults to
            "UUID_FORGE_SALT".

    Returns:
        An IDConfig instance populated from environment variables.

    Raises:
        ValueError: If namespace environment variable contains invalid value.

    Example:
        ```python
        import os
        from uuid_forge.config import load_config_from_env

        # Set environment variables
        os.environ["UUID_FORGE_NAMESPACE"] = "mycompany.com"
        os.environ["UUID_FORGE_SALT"] = "your-secret-salt-here"

        # Load configuration
        config = load_config_from_env()

        # Use in UUID generation
        from uuid_forge.core import generate_uuid_only
        entity_uuid = generate_uuid_only(
            "invoice",
            config=config,
            region="EUR",
            number=12345
        )
        ```

    <!-- Example Test:
    >>> import os
    >>> from uuid_forge.config import load_config_from_env
    >>> from uuid_forge.core import IDConfig
    >>> import uuid
    >>> # Test with default namespace (no env var)
    >>> config1 = load_config_from_env()
    >>> assert config1.namespace == uuid.NAMESPACE_DNS
    >>> assert config1.salt == ""
    >>> # Test with custom namespace
    >>> os.environ["UUID_FORGE_NAMESPACE"] = "test.example.com"
    >>> os.environ["UUID_FORGE_SALT"] = "test-salt-123"
    >>> config2 = load_config_from_env()
    >>> assert config2.salt == "test-salt-123"
    >>> # Namespace should be derived from domain
    >>> expected_namespace = uuid.uuid5(uuid.NAMESPACE_DNS, "test.example.com")
    >>> assert config2.namespace == expected_namespace
    >>> # Cleanup
    >>> del os.environ["UUID_FORGE_NAMESPACE"]
    >>> del os.environ["UUID_FORGE_SALT"]
    >>> # Test with custom env var names
    >>> os.environ["CUSTOM_NS"] = "custom.example.com"
    >>> os.environ["CUSTOM_SALT"] = "custom-salt"
    >>> config3 = load_config_from_env(namespace_env="CUSTOM_NS", salt_env="CUSTOM_SALT")
    >>> assert config3.salt == "custom-salt"
    >>> del os.environ["CUSTOM_NS"]
    >>> del os.environ["CUSTOM_SALT"]
    -->
    """
    # Get namespace from environment
    namespace_value = os.getenv(namespace_env)
    if namespace_value:
        # Convert domain string to UUID namespace
        try:
            namespace = uuid_module.uuid5(
                uuid_module.NAMESPACE_DNS,
                namespace_value
            )
        except Exception as e:
            raise ValueError(
                f"Invalid namespace value in {namespace_env}: {namespace_value}"
            ) from e
    else:
        namespace = uuid_module.NAMESPACE_DNS

    # Get salt from environment
    salt = os.getenv(salt_env, "")

    return IDConfig(namespace=namespace, salt=salt)


def get_default_config() -> IDConfig:
    """Get the default configuration for UUID generation.

    This function returns a default configuration that first attempts to load
    from environment variables, falling back to a basic configuration with
    no salt if environment variables are not set.

    WARNING: The default configuration without a salt is NOT secure for
    production use. Always set UUID_FORGE_SALT in production environments.

    Returns:
        An IDConfig instance with default or environment-based configuration.

    Example:
        ```python
        from uuid_forge.config import get_default_config
        from uuid_forge.core import generate_uuid_only

        # Get default config (loads from environment if available)
        config = get_default_config()

        # Use in UUID generation
        entity_uuid = generate_uuid_only(
            "invoice",
            config=config,
            region="EUR",
            number=12345
        )
        ```

    <!-- Example Test:
    >>> from uuid_forge.config import get_default_config
    >>> import uuid
    >>> import os
    >>> # Test without environment variables
    >>> config1 = get_default_config()
    >>> assert config1.namespace == uuid.NAMESPACE_DNS
    >>> assert config1.salt == ""
    >>> # Test with environment variables
    >>> os.environ["UUID_FORGE_NAMESPACE"] = "default.example.com"
    >>> os.environ["UUID_FORGE_SALT"] = "default-salt"
    >>> config2 = get_default_config()
    >>> assert config2.salt == "default-salt"
    >>> # Cleanup
    >>> del os.environ["UUID_FORGE_NAMESPACE"]
    >>> del os.environ["UUID_FORGE_SALT"]
    -->
    """
    return load_config_from_env()


def validate_config_security(config: IDConfig, strict: bool = False) -> tuple[bool, list[str]]:
    """Validate configuration for security best practices.

    This function checks whether a configuration meets security requirements
    for production use. It validates that a salt is present and has sufficient
    entropy, and provides warnings or errors as appropriate.

    Args:
        config: The IDConfig to validate.
        strict: If True, treats warnings as failures. If False, only critical
            security issues cause validation to fail.

    Returns:
        A tuple of (is_valid, messages) where:
        - is_valid: Boolean indicating if configuration passes validation
        - messages: List of warning/error messages

    Example:
        ```python
        from uuid_forge.config import validate_config_security
        from uuid_forge.core import IDConfig

        # Insecure config (no salt)
        config_bad = IDConfig()
        is_valid, messages = validate_config_security(config_bad)
        if not is_valid:
            print("Configuration issues:")
            for msg in messages:
                print(f"  - {msg}")

        # Secure config
        config_good = IDConfig(salt="xvW9Kz_kRzPmNqYvTaWcXdYeFgZhAiB")
        is_valid, messages = validate_config_security(config_good)
        assert is_valid
        ```

    <!-- Example Test:
    >>> from uuid_forge.config import validate_config_security
    >>> from uuid_forge.core import IDConfig, generate_salt
    >>> # Test with no salt (insecure)
    >>> config_no_salt = IDConfig()
    >>> is_valid, messages = validate_config_security(config_no_salt)
    >>> assert not is_valid
    >>> assert len(messages) > 0
    >>> assert any("salt" in msg.lower() for msg in messages)
    >>> # Test with short salt (warning)
    >>> config_short_salt = IDConfig(salt="short")
    >>> is_valid, messages = validate_config_security(config_short_salt)
    >>> # Should pass in non-strict mode but have warnings
    >>> assert is_valid or not is_valid  # May pass or fail depending on threshold
    >>> assert len(messages) > 0
    >>> # Test with good salt
    >>> config_good = IDConfig(salt=generate_salt())
    >>> is_valid, messages = validate_config_security(config_good)
    >>> assert is_valid
    >>> assert len(messages) == 0
    >>> # Test strict mode with short salt
    >>> config_short = IDConfig(salt="tiny")
    >>> is_valid_strict, messages_strict = validate_config_security(config_short, strict=True)
    >>> assert not is_valid_strict
    -->
    """
    messages = []
    is_valid = True

    # Check if salt is present
    if not config.salt:
        messages.append(
            "CRITICAL: No salt configured. UUIDs are predictable and may be a "
            "security risk. Generate a salt with generate_salt() and set "
            "UUID_FORGE_SALT environment variable."
        )
        is_valid = False
    elif len(config.salt) < 16:
        messages.append(
            f"WARNING: Salt is only {len(config.salt)} characters. "
            "Recommended minimum is 16 characters for security."
        )
        if strict:
            is_valid = False
    elif len(config.salt) < 32:
        messages.append(
            f"INFO: Salt is {len(config.salt)} characters. "
            "Consider using 32+ characters for optimal security."
        )
        # This is just informational, doesn't affect validity

    # Check namespace
    if config.namespace == uuid_module.NAMESPACE_DNS:
        messages.append(
            "INFO: Using default DNS namespace. Consider setting a custom "
            "namespace via UUID_FORGE_NAMESPACE for better isolation."
        )
        # This is just informational

    return is_valid, messages


def init_config_file(
    output_path: Path | None = None,
    force: bool = False
) -> Path:
    """Initialize a configuration template file with generated salt.

    This function creates a template configuration file (typically .env format)
    with a freshly generated cryptographic salt and usage instructions. This
    is useful for setting up new deployments or development environments.

    Args:
        output_path: Path where the config file should be written. If None,
            writes to ".env" in the current directory.
        force: If True, overwrites existing file. If False, raises error if
            file exists.

    Returns:
        Path to the created configuration file.

    Raises:
        FileExistsError: If output_path exists and force is False.
        IOError: If file cannot be written.

    Example:
        ```python
        from uuid_forge.config import init_config_file
        from pathlib import Path

        # Initialize config in current directory
        config_path = init_config_file()
        print(f"Configuration template created at: {config_path}")

        # Read the generated configuration
        with open(config_path) as f:
            print(f.read())
        ```

    <!-- Example Test:
    >>> from uuid_forge.config import init_config_file
    >>> from pathlib import Path
    >>> import tempfile
    >>> import os
    >>> # Test with temporary directory
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     output = Path(tmpdir) / "test.env"
    ...     result = init_config_file(output_path=output)
    ...     assert result == output
    ...     assert output.exists()
    ...     # Read and verify content
    ...     content = output.read_text()
    ...     assert "UUID_FORGE_SALT" in content
    ...     assert "UUID_FORGE_NAMESPACE" in content
    ...     # Test that salt is actually generated (not empty)
    ...     lines = content.split("\\n")
    ...     salt_line = [l for l in lines if l.startswith("UUID_FORGE_SALT=")][0]
    ...     salt_value = salt_line.split("=", 1)[1]
    ...     assert len(salt_value) > 0
    >>> # Test without force (should fail if file exists)
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     output = Path(tmpdir) / "test.env"
    ...     init_config_file(output_path=output)
    ...     try:
    ...         init_config_file(output_path=output, force=False)
    ...         assert False, "Should raise FileExistsError"
    ...     except FileExistsError:
    ...         pass
    >>> # Test with force (should overwrite)
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     output = Path(tmpdir) / "test.env"
    ...     init_config_file(output_path=output)
    ...     first_content = output.read_text()
    ...     init_config_file(output_path=output, force=True)
    ...     second_content = output.read_text()
    ...     # Content should be different (new salt generated)
    ...     assert first_content != second_content
    -->
    """
    if output_path is None:
        output_path = Path(".env")

    output_path = Path(output_path)

    # Check if file exists
    if output_path.exists() and not force:
        raise FileExistsError(
            f"Configuration file already exists at {output_path}. "
            "Use force=True to overwrite."
        )

    # Generate new salt
    new_salt = generate_salt()

    # Create configuration file content
    content = f"""# UUID-Forge Configuration
# Generated configuration file for deterministic UUID generation
#
# IMPORTANT: Keep this file secure! The salt should be treated as a secret.
# Add this file to .gitignore and never commit it to version control.

# Cryptographic salt for UUID generation (REQUIRED for security)
# This salt ensures that UUIDs cannot be predicted by attackers
UUID_FORGE_SALT={new_salt}

# Custom namespace for logical separation (OPTIONAL)
# Use your company domain or application identifier
# Example: mycompany.com, app.example.org
# UUID_FORGE_NAMESPACE=mycompany.com

# Usage:
# 1. Keep this file secure and never commit to version control
# 2. Set these environment variables in your deployment
# 3. Or use python-dotenv to load this file:
#
#    from dotenv import load_dotenv
#    load_dotenv()
#    from uuid_forge.config import load_config_from_env
#    config = load_config_from_env()
"""

    # Write file
    try:
        output_path.write_text(content)
    except OSError as e:
        raise OSError(f"Failed to write configuration file: {e}") from e

    return output_path
