"""Tests for documentation building.

This module contains tests to ensure that the documentation builds successfully
without errors. This helps catch documentation issues during local testing
rather than discovering them only in CI/CD.
"""

import subprocess
import sys
from pathlib import Path

import pytest


class TestDocumentationBuild:
    """Test cases for documentation building."""

    def test_mkdocs_config_exists(self) -> None:
        """Test that mkdocs.yml configuration file exists."""
        config_path = Path("mkdocs.yml")
        assert config_path.exists(), "mkdocs.yml configuration file is missing"
        assert config_path.is_file(), "mkdocs.yml should be a file"

    def test_docs_directory_exists(self) -> None:
        """Test that the docs directory exists with required files."""
        docs_dir = Path("docs")
        assert docs_dir.exists(), "docs directory is missing"
        assert docs_dir.is_dir(), "docs should be a directory"

        # Check for index.md
        index_path = docs_dir / "index.md"
        assert index_path.exists(), "docs/index.md is missing"

    @pytest.mark.slow
    def test_mkdocs_build_succeeds(self) -> None:
        """Test that mkdocs builds the documentation successfully.

        This test requires the docs dependency group to be installed.
        It's marked as 'slow' because building docs can take time.

        To run this test locally, ensure docs dependencies are installed:
            uv sync --group docs
        """
        try:
            # Try to build the documentation using uv run
            result = subprocess.run(
                ["uv", "run", "mkdocs", "build", "--strict"],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )

            if result.returncode != 0:
                error_msg = f"mkdocs build failed with return code {result.returncode}"
                if result.stdout:
                    error_msg += f"\nSTDOUT:\n{result.stdout}"
                if result.stderr:
                    error_msg += f"\nSTDERR:\n{result.stderr}"
                pytest.fail(error_msg)

        except FileNotFoundError:
            pytest.skip("mkdocs not found. Install docs dependencies with: uv sync --group docs")
        except subprocess.TimeoutExpired:
            pytest.fail("mkdocs build timed out after 2 minutes")

    def test_mkdocs_config_is_valid_yaml(self) -> None:
        """Test that mkdocs.yml is valid YAML and contains required fields."""
        import yaml

        config_path = Path("mkdocs.yml")
        with config_path.open() as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"mkdocs.yml is not valid YAML: {e}")

        # Check for required fields
        required_fields = ["site_name", "site_description"]
        for field in required_fields:
            assert field in config, f"mkdocs.yml is missing required field: {field}"

        # Ensure we have some content structure
        assert "nav" in config or "docs_dir" in config, (
            "mkdocs.yml should have either 'nav' or 'docs_dir' defined"
        )

    def test_api_docs_source_files_exist(self) -> None:
        """Test that source files referenced in API docs exist."""
        # Check that the main source modules exist
        src_dir = Path("src/uuid_forge")
        assert src_dir.exists(), "Source directory src/uuid_forge is missing"

        required_modules = ["__init__.py", "core.py", "config.py", "cli.py"]
        for module in required_modules:
            module_path = src_dir / module
            assert module_path.exists(), f"Required module {module} is missing"

    @pytest.mark.slow
    def test_mkdocs_serve_can_start(self) -> None:
        """Test that mkdocs serve can start without immediate errors.

        This doesn't run a full server, but tests that the serve command
        can initialize without configuration errors.
        """
        try:
            # Start mkdocs serve and kill it quickly to test initialization
            process = subprocess.Popen(
                [sys.executable, "-m", "mkdocs", "serve", "--no-livereload"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Give it a moment to start and detect any immediate errors
            try:
                # Wait briefly for startup
                stdout, stderr = process.communicate(timeout=5)

                # If it exited within 5 seconds, check why
                if process.returncode is not None and process.returncode != 0:
                    error_msg = f"mkdocs serve failed to start (exit code {process.returncode})"
                    if stdout:
                        error_msg += f"\nSTDOUT:\n{stdout}"
                    if stderr:
                        error_msg += f"\nSTDERR:\n{stderr}"
                    pytest.fail(error_msg)

            except subprocess.TimeoutExpired:
                # Good! Server started and didn't exit immediately
                process.terminate()
                process.wait(timeout=5)

        except FileNotFoundError:
            pytest.skip("mkdocs not found. Install docs dependencies with: uv sync --group docs")


class TestDocumentationContent:
    """Test cases for documentation content quality."""

    def test_readme_exists(self) -> None:
        """Test that README.md exists and has content."""
        readme_path = Path("README.md")
        assert readme_path.exists(), "README.md is missing"

        content = readme_path.read_text()
        assert len(content.strip()) > 0, "README.md is empty"
        assert "uuid-forge" in content.lower(), "README.md should mention the project name"

    def test_docs_index_has_content(self) -> None:
        """Test that docs/index.md has meaningful content."""
        index_path = Path("docs/index.md")
        if not index_path.exists():
            pytest.skip("docs/index.md not found")

        content = index_path.read_text()
        assert len(content.strip()) > 100, "docs/index.md should have substantial content"

    def test_api_docs_exist(self) -> None:
        """Test that API documentation files exist."""
        api_dir = Path("docs/api")
        if not api_dir.exists():
            pytest.skip("docs/api directory not found")

        # Look for core API documentation
        core_doc = api_dir / "core.md"
        if core_doc.exists():
            content = core_doc.read_text()
            assert len(content.strip()) > 0, "docs/api/core.md should not be empty"
