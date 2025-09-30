"""Tests for uuid_forge.cli module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from uuid_forge.cli import app

runner = CliRunner()


class TestGenerateCommand:
    """Tests for the generate command."""

    def test_generate_basic(self):
        """Test basic generate command."""
        result = runner.invoke(app, ["generate", "test", "--attr", "key=value"])
        assert result.exit_code == 0
        assert "Generated UUID for test" in result.output

    def test_generate_with_prefix(self):
        """Test generate command with prefix."""
        result = runner.invoke(app, ["generate", "test", "--prefix", "TST", "--attr", "key=value"])
        assert result.exit_code == 0
        assert "TST-" in result.output

    def test_generate_with_separator(self):
        """Test generate command with custom separator."""
        result = runner.invoke(
            app, ["generate", "test", "--prefix", "TST", "--separator", "_", "--attr", "key=value"]
        )
        assert result.exit_code == 0
        assert "TST_" in result.output

    def test_generate_no_attributes(self):
        """Test generate command without attributes."""
        result = runner.invoke(app, ["generate", "test"])
        assert result.exit_code == 0  # Actually works, just generates from entity_type

    def test_generate_multiple_attributes(self):
        """Test generate command with multiple attributes."""
        result = runner.invoke(
            app, ["generate", "test", "--attr", "key1=value1", "--attr", "key2=value2"]
        )
        assert result.exit_code == 0
        assert "Generated UUID for test" in result.output


class TestExtractCommand:
    """Tests for the extract command."""

    def test_extract_prefixed_uuid(self):
        """Test extracting UUID from prefixed string."""
        # First generate a UUID to extract
        gen_result = runner.invoke(
            app, ["generate", "test", "--prefix", "TST", "--attr", "key=value"]
        )
        assert gen_result.exit_code == 0

        # Extract UUID from output
        import re

        uuid_match = re.search(r"TST-([a-f0-9-]{36})", gen_result.output)
        if uuid_match:
            prefixed_uuid = f"TST-{uuid_match.group(1)}"
            result = runner.invoke(app, ["extract", prefixed_uuid])
            assert result.exit_code == 0
            assert "Extracted UUID" in result.output

    def test_extract_invalid_format(self):
        """Test extract with invalid format."""
        result = runner.invoke(app, ["extract", "invalid-uuid"])
        assert result.exit_code == 1


class TestNewSaltCommand:
    """Tests for the new-salt command."""

    def test_new_salt_default_length(self):
        """Test generating new salt with default length."""
        result = runner.invoke(app, ["new-salt"])
        assert result.exit_code == 0
        assert "Generated Salt" in result.output

    def test_new_salt_custom_length(self):
        """Test generating new salt with custom length."""
        result = runner.invoke(app, ["new-salt", "--length", "16"])
        assert result.exit_code == 0
        assert "Generated Salt" in result.output

    def test_new_salt_invalid_length(self):
        """Test new-salt with invalid length."""
        result = runner.invoke(app, ["new-salt", "--length", "0"])
        assert result.exit_code == 1


class TestInitCommand:
    """Tests for the init command."""

    def test_init_creates_config_file(self):
        """Test that init creates a config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / ".env"
            result = runner.invoke(app, ["init", "--output", str(config_path)])
            assert result.exit_code == 0
            assert config_path.exists()
            assert "Configuration file created successfully" in result.output

    def test_init_existing_file_no_force(self):
        """Test init with existing file without force."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / ".env"
            config_path.write_text("existing content")

            result = runner.invoke(app, ["init", "--output", str(config_path)])
            assert result.exit_code == 1
            assert "already exists" in result.output

    def test_init_existing_file_with_force(self):
        """Test init with existing file with force."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / ".env"
            config_path.write_text("existing content")

            result = runner.invoke(app, ["init", "--output", str(config_path), "--force"])
            assert result.exit_code == 0
            assert "Configuration file created successfully" in result.output


class TestValidateCommand:
    """Tests for the validate command."""

    def test_validate_with_env_vars(self, monkeypatch):
        """Test validate with environment variables."""
        monkeypatch.setenv("UUID_FORGE_SALT", "test-salt-with-good-length-over-32-chars")
        monkeypatch.setenv("UUID_FORGE_NAMESPACE", "test.example.com")

        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 0
        assert "secure and follows best practices" in result.output

    def test_validate_weak_salt(self, monkeypatch):
        """Test validate with weak salt."""
        monkeypatch.setenv("UUID_FORGE_SALT", "weak")

        result = runner.invoke(app, ["validate"])
        # Weak salt should still pass with warnings, not fail
        assert result.exit_code == 0
        assert "warning" in result.output.lower() or "info" in result.output.lower()

    def test_validate_no_config(self, monkeypatch):
        """Test validate with no configuration."""
        monkeypatch.delenv("UUID_FORGE_SALT", raising=False)
        monkeypatch.delenv("UUID_FORGE_NAMESPACE", raising=False)

        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 1
        assert "Validation Failed" in result.output


class TestInfoCommand:
    """Tests for the info command."""

    def test_info_displays_version(self):
        """Test that info command displays configuration information."""
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Current Configuration" in result.output

    def test_info_displays_config(self, monkeypatch):
        """Test that info command displays configuration."""
        monkeypatch.setenv("UUID_FORGE_SALT", "test-salt")
        monkeypatch.setenv("UUID_FORGE_NAMESPACE", "test.example.com")

        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Current Configuration" in result.output


class TestDocsCommand:
    """Tests for the docs command."""

    @patch("subprocess.run")
    def test_docs_build_mode(self, mock_run):
        """Test docs command in build mode."""
        mock_run.return_value = Mock(returncode=0)

        result = runner.invoke(app, ["docs", "--build"])
        assert result.exit_code == 0
        assert mock_run.call_count >= 1  # May call mkdocs --version first
        # Check that build was called
        build_called = any("build" in str(call) for call in mock_run.call_args_list)
        assert build_called

    @patch("subprocess.run")
    def test_docs_serve_mode(self, mock_run):
        """Test docs command in serve mode."""

        def side_effect(*args, **kwargs):
            if "--version" in args[0]:
                return Mock(returncode=0)
            raise KeyboardInterrupt()

        mock_run.side_effect = side_effect

        result = runner.invoke(app, ["docs", "--serve"])
        assert result.exit_code == 0

    @patch("subprocess.run")
    def test_docs_custom_port(self, mock_run):
        """Test docs command with custom port."""

        def side_effect(*args, **kwargs):
            if "--version" in args[0]:
                return Mock(returncode=0)
            raise KeyboardInterrupt()

        mock_run.side_effect = side_effect

        result = runner.invoke(app, ["docs", "--port", "9000"])
        assert result.exit_code == 0

    @patch("subprocess.run")
    def test_docs_build_failure(self, mock_run):
        """Test docs command build failure."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, "mkdocs", stderr="build failed")

        result = runner.invoke(app, ["docs", "--build"])
        assert result.exit_code == 1


class TestTestCommand:
    """Tests for the test command."""

    @patch("subprocess.run")
    def test_test_default(self, mock_run):
        """Test test command with defaults."""
        mock_run.return_value = Mock(returncode=0)

        result = runner.invoke(app, ["test"])
        assert result.exit_code == 0
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "pytest" in args
        assert "--cov=uuid_forge" in args

    @patch("subprocess.run")
    def test_test_no_coverage(self, mock_run):
        """Test test command without coverage."""
        mock_run.return_value = Mock(returncode=0)

        result = runner.invoke(app, ["test", "--no-coverage"])
        assert result.exit_code == 0
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "pytest" in args
        assert "--cov=uuid_forge" not in args

    @patch("subprocess.run")
    def test_test_with_pattern(self, mock_run):
        """Test test command with pattern."""
        mock_run.return_value = Mock(returncode=0)

        result = runner.invoke(app, ["test", "--pattern", "test_core"])
        assert result.exit_code == 0
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "-k" in args
        assert "test_core" in args

    @patch("subprocess.run")
    def test_test_verbose_fail_fast(self, mock_run):
        """Test test command with verbose and fail-fast."""
        mock_run.return_value = Mock(returncode=0)

        result = runner.invoke(app, ["test", "--verbose", "--fail-fast"])
        assert result.exit_code == 0
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "-v" in args
        assert "-x" in args

    @patch("subprocess.run")
    def test_test_failure(self, mock_run):
        """Test test command with test failures."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(2, "pytest")

        result = runner.invoke(app, ["test"])
        assert result.exit_code == 2

    @patch("subprocess.run")
    def test_test_keyboard_interrupt(self, mock_run):
        """Test test command with keyboard interrupt."""
        mock_run.side_effect = KeyboardInterrupt()

        result = runner.invoke(app, ["test"])
        assert result.exit_code == 130


class TestMainApp:
    """Tests for the main app and entry point."""

    def test_app_help(self):
        """Test that app displays help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Deterministic UUID generation" in result.output

    def test_invalid_command(self):
        """Test invalid command."""
        result = runner.invoke(app, ["invalid-command"])
        assert result.exit_code != 0
