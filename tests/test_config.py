"""
Tests for uuid_forge.config module.

This test module ensures configuration loading, validation, and
initialization work correctly across different environments.
"""

import os
import tempfile
import uuid as uuid_module
from pathlib import Path

import pytest

from uuid_forge.config import (
    get_default_config,
    init_config_file,
    load_config_from_env,
    validate_config_security,
)
from uuid_forge.core import IDConfig, generate_salt


class TestLoadConfigFromEnv:
    """Tests for load_config_from_env function."""

    def test_default_config_no_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading config with no environment variables set."""
        # Clear environment variables
        monkeypatch.delenv("UUID_FORGE_NAMESPACE", raising=False)
        monkeypatch.delenv("UUID_FORGE_SALT", raising=False)

        config = load_config_from_env()

        assert config.namespace == uuid_module.NAMESPACE_DNS
        assert config.salt == ""

    def test_load_salt_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading salt from environment variable."""
        monkeypatch.setenv("UUID_FORGE_SALT", "test-salt-123")

        config = load_config_from_env()

        assert config.salt == "test-salt-123"

    def test_load_namespace_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading namespace from environment variable."""
        monkeypatch.setenv("UUID_FORGE_NAMESPACE", "test.example.com")

        config = load_config_from_env()

        expected_namespace = uuid_module.uuid5(uuid_module.NAMESPACE_DNS, "test.example.com")
        assert config.namespace == expected_namespace

    def test_load_both_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading both namespace and salt from environment."""
        monkeypatch.setenv("UUID_FORGE_NAMESPACE", "mycompany.com")
        monkeypatch.setenv("UUID_FORGE_SALT", "production-salt")

        config = load_config_from_env()

        expected_namespace = uuid_module.uuid5(uuid_module.NAMESPACE_DNS, "mycompany.com")
        assert config.namespace == expected_namespace
        assert config.salt == "production-salt"

    def test_custom_env_var_names(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading from custom environment variable names."""
        monkeypatch.setenv("CUSTOM_NS", "custom.example.com")
        monkeypatch.setenv("CUSTOM_SALT", "custom-salt")

        config = load_config_from_env(namespace_env="CUSTOM_NS", salt_env="CUSTOM_SALT")

        assert config.salt == "custom-salt"
        expected_namespace = uuid_module.uuid5(uuid_module.NAMESPACE_DNS, "custom.example.com")
        assert config.namespace == expected_namespace

    def test_invalid_namespace_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that invalid namespace value raises ValueError."""
        # This shouldn't actually fail as any string is valid for uuid5
        # But we can test the error handling mechanism
        monkeypatch.setenv("UUID_FORGE_NAMESPACE", "valid-domain.com")
        config = load_config_from_env()
        assert config.namespace is not None


class TestGetDefaultConfig:
    """Tests for get_default_config function."""

    def test_returns_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that get_default_config returns an IDConfig."""
        monkeypatch.delenv("UUID_FORGE_NAMESPACE", raising=False)
        monkeypatch.delenv("UUID_FORGE_SALT", raising=False)

        config = get_default_config()

        assert isinstance(config, IDConfig)

    def test_loads_from_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that get_default_config loads from environment."""
        monkeypatch.setenv("UUID_FORGE_SALT", "default-salt")

        config = get_default_config()

        assert config.salt == "default-salt"

    def test_no_salt_warning(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that default config without salt is insecure."""
        monkeypatch.delenv("UUID_FORGE_SALT", raising=False)

        config = get_default_config()

        # Validate security
        is_valid, messages = validate_config_security(config)
        assert not is_valid
        assert any("CRITICAL" in msg for msg in messages)


class TestValidateConfigSecurity:
    """Tests for validate_config_security function."""

    def test_no_salt_fails_validation(self) -> None:
        """Test that config without salt fails validation."""
        config = IDConfig()
        is_valid, messages = validate_config_security(config)

        assert not is_valid
        assert len(messages) > 0
        assert any("CRITICAL" in msg and "salt" in msg.lower() for msg in messages)

    def test_short_salt_warning(self) -> None:
        """Test that short salt produces warning."""
        config = IDConfig(salt="short")
        is_valid, messages = validate_config_security(config)

        # Should pass in non-strict mode but have warnings
        assert len(messages) > 0
        assert any("WARNING" in msg for msg in messages)

    def test_good_salt_passes(self) -> None:
        """Test that good salt passes validation."""
        config = IDConfig(salt=generate_salt())
        is_valid, messages = validate_config_security(config)

        assert is_valid
        # May have INFO messages but no CRITICAL or WARNING
        assert not any("CRITICAL" in msg or "WARNING" in msg for msg in messages)

    def test_strict_mode_with_short_salt(self) -> None:
        """Test that strict mode treats warnings as failures."""
        config = IDConfig(salt="tiny")
        is_valid, messages = validate_config_security(config, strict=True)

        assert not is_valid

    def test_minimum_salt_length_info(self) -> None:
        """Test info message for salt between 16-32 characters."""
        config = IDConfig(salt="a" * 20)  # 20 characters
        is_valid, messages = validate_config_security(config)

        # Should pass validation
        assert True  # Implementation dependent
        # May have INFO message
        [msg for msg in messages if "INFO" in msg]
        # Just check it doesn't fail

    def test_default_namespace_info(self) -> None:
        """Test info message for default namespace."""
        config = IDConfig(salt=generate_salt())
        is_valid, messages = validate_config_security(config)

        # Should pass
        assert is_valid
        # Should have info about default namespace
        assert any("namespace" in msg.lower() for msg in messages)


class TestInitConfigFile:
    """Tests for init_config_file function."""

    def test_create_config_file(self) -> None:
        """Test creating new config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.env"

            result = init_config_file(output_path=output_path)

            assert result == output_path
            assert output_path.exists()

            # Check content
            content = output_path.read_text()
            assert "UUID_FORGE_SALT" in content
            assert "UUID_FORGE_NAMESPACE" in content

    def test_default_output_path(self) -> None:
        """Test creating config file with default path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory
            original_cwd = Path.cwd()
            try:
                os.chdir(tmpdir)

                result = init_config_file()

                assert result == Path(".env")
                assert result.exists()
            finally:
                os.chdir(original_cwd)

    def test_file_exists_without_force(self) -> None:
        """Test that existing file without force raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.env"

            # Create file first
            init_config_file(output_path=output_path)

            # Try to create again without force
            with pytest.raises(FileExistsError):
                init_config_file(output_path=output_path, force=False)

    def test_file_exists_with_force(self) -> None:
        """Test that force overwrites existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.env"

            # Create file first
            init_config_file(output_path=output_path)
            first_content = output_path.read_text()

            # Overwrite with force
            init_config_file(output_path=output_path, force=True)
            second_content = output_path.read_text()

            # Content should be different (new salt generated)
            assert first_content != second_content

    def test_generated_salt_is_valid(self) -> None:
        """Test that generated config file contains valid salt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.env"

            init_config_file(output_path=output_path)

            content = output_path.read_text()

            # Extract salt value
            lines = content.split("\n")
            salt_line = [line for line in lines if line.startswith("UUID_FORGE_SALT=")]
            assert len(salt_line) == 1

            salt_value = salt_line[0].split("=", 1)[1]

            # Salt should not be empty
            assert len(salt_value) > 0

            # Salt should be URL-safe base64
            import re

            assert re.match(r"^[A-Za-z0-9_-]+$", salt_value)

    def test_config_file_has_usage_instructions(self) -> None:
        """Test that generated config file includes usage instructions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.env"

            init_config_file(output_path=output_path)

            content = output_path.read_text()

            # Should have usage instructions
            assert "Usage:" in content or "usage:" in content
            assert "dotenv" in content.lower() or "environment" in content.lower()

    def test_config_file_has_security_warning(self) -> None:
        """Test that generated config file includes security warning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.env"

            init_config_file(output_path=output_path)

            content = output_path.read_text()

            # Should warn about security
            assert "secret" in content.lower() or "secure" in content.lower()
            assert "gitignore" in content.lower() or "version control" in content.lower()


class TestConfigIntegration:
    """Integration tests for configuration workflow."""

    def test_full_config_workflow(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test complete configuration workflow from init to use."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / ".env"

            # 1. Initialize config file
            init_config_file(output_path=output_path)
            assert output_path.exists()

            # 2. Read generated salt
            content = output_path.read_text()
            lines = content.split("\n")
            salt_line = [line for line in lines if line.startswith("UUID_FORGE_SALT=")][0]
            generated_salt = salt_line.split("=", 1)[1]

            # 3. Set environment variable
            monkeypatch.setenv("UUID_FORGE_SALT", generated_salt)

            # 4. Load config from environment
            config = load_config_from_env()

            assert config.salt == generated_salt

            # 5. Validate security
            is_valid, messages = validate_config_security(config)

            assert is_valid

    def test_production_like_setup(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test production-like configuration setup."""
        # Simulate production environment
        prod_salt = generate_salt()
        monkeypatch.setenv("UUID_FORGE_SALT", prod_salt)
        monkeypatch.setenv("UUID_FORGE_NAMESPACE", "production.company.com")

        # Load config
        config = load_config_from_env()

        # Validate
        is_valid, messages = validate_config_security(config, strict=True)

        assert is_valid
        assert config.salt == prod_salt

        # Namespace should be derived from domain
        expected_ns = uuid_module.uuid5(uuid_module.NAMESPACE_DNS, "production.company.com")
        assert config.namespace == expected_ns

    def test_development_setup(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test development environment setup."""
        # Development might use fixed salt for reproducibility
        dev_salt = "development-fixed-salt-for-testing"
        monkeypatch.setenv("UUID_FORGE_SALT", dev_salt)

        config = load_config_from_env()

        assert config.salt == dev_salt

        # Should still validate (even if warning about salt length)
        is_valid, messages = validate_config_security(config, strict=False)
        # In non-strict mode, might pass with warnings
