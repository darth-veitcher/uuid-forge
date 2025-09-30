"""Nox configuration for UUID-Forge.

This file defines automated testing, linting, and documentation tasks
that can be run across multiple Python versions. Nox ensures consistency
across development environments and CI/CD pipelines.
"""

import nox

# Supported Python versions
PYTHON_VERSIONS = ["3.11", "3.12"]

# Default sessions to run when just calling 'nox'
nox.options.sessions = ["tests", "lint", "type_check"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the test suite with pytest.

    This session runs tests across all supported Python versions with
    coverage reporting. Coverage must remain above 80%.

    Args:
        session: The Nox session object.

    Example:
        Run tests for all Python versions:
        $ nox -s tests

        Run tests for specific Python version:
        $ nox -s tests-3.11
    """
    session.install(".[test]")
    session.run(
        "pytest",
        "--cov=uuid_forge",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-report=xml",
        "--cov-fail-under=80",
        *session.posargs,
    )


@nox.session(python="3.11")
def lint(session: nox.Session) -> None:
    """Run ruff linter to check code quality.

    This session checks for code style issues, potential bugs, and
    adherence to PEP-8 standards using ruff.

    Args:
        session: The Nox session object.

    Example:
        $ nox -s lint

        Auto-fix issues:
        $ nox -s lint -- --fix
    """
    session.install(".[dev]")
    session.run("ruff", "check", "src", "tests", *session.posargs)


@nox.session(python="3.11")
def type_check(session: nox.Session) -> None:
    """Run mypy for static type checking.

    This session ensures type safety across the codebase using mypy
    with strict mode enabled.

    Args:
        session: The Nox session object.

    Example:
        $ nox -s type_check
    """
    session.install(".[dev]")
    session.run("mypy", "src", *session.posargs)


@nox.session(python="3.11")
def format(session: nox.Session) -> None:
    """Format code with black.

    This session automatically formats all Python code to adhere to
    black's opinionated style.

    Args:
        session: The Nox session object.

    Example:
        $ nox -s format

        Check formatting without changes:
        $ nox -s format -- --check
    """
    session.install(".[dev]")
    session.run("black", "src", "tests", "noxfile.py", *session.posargs)


@nox.session(python="3.11")
def format_check(session: nox.Session) -> None:
    """Check code formatting without making changes.

    This session verifies that all code is properly formatted according
    to black's style without modifying any files.

    Args:
        session: The Nox session object.

    Example:
        $ nox -s format_check
    """
    session.install(".[dev]")
    session.run("black", "--check", "src", "tests", "noxfile.py")


@nox.session(python="3.11")
def docs(session: nox.Session) -> None:
    """Build documentation with MkDocs.

    This session builds the documentation site using MkDocs with the
    Material theme and mkdocstrings for API documentation.

    Args:
        session: The Nox session object.

    Example:
        $ nox -s docs
    """
    session.install(".[docs]")
    session.run("mkdocs", "build", "--strict", *session.posargs)


@nox.session(python="3.11")
def docs_serve(session: nox.Session) -> None:
    """Serve documentation locally with live reloading.

    This session starts a local development server for the documentation
    with automatic reloading when files change.

    Args:
        session: The Nox session object.

    Example:
        $ nox -s docs_serve

        Then open http://localhost:8000 in your browser.
    """
    session.install(".[docs]")
    session.run("mkdocs", "serve", *session.posargs)


@nox.session(python="3.11")
def coverage_report(session: nox.Session) -> None:
    """Generate and display coverage report.

    This session generates a detailed coverage report and opens it in
    the default browser.

    Args:
        session: The Nox session object.

    Example:
        $ nox -s coverage_report
    """
    session.install(".[test]")
    session.run(
        "pytest",
        "--cov=uuid_forge",
        "--cov-report=html",
        "--cov-report=term-missing",
    )
    session.run("python", "-m", "webbrowser", "htmlcov/index.html")


@nox.session(python="3.11")
def build(session: nox.Session) -> None:
    """Build distribution packages.

    This session builds both wheel and source distribution packages
    for publication to PyPI.

    Args:
        session: The Nox session object.

    Example:
        $ nox -s build
    """
    session.install("build")
    session.run("python", "-m", "build")


@nox.session(python="3.11")
def clean(session: nox.Session) -> None:
    """Clean up build artifacts and cache directories.

    This session removes all generated files including build artifacts,
    cache directories, and coverage reports.

    Args:
        session: The Nox session object.

    Example:
        $ nox -s clean
    """
    import shutil
    from pathlib import Path

    dirs_to_remove = [
        "build",
        "dist",
        "htmlcov",
        ".coverage",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "*.egg-info",
    ]

    for pattern in dirs_to_remove:
        for path in Path().glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                session.log(f"Removed directory: {path}")
            elif path.is_file():
                path.unlink()
                session.log(f"Removed file: {path}")

    # Remove __pycache__ directories
    for pycache in Path().rglob("__pycache__"):
        shutil.rmtree(pycache)
        session.log(f"Removed cache: {pycache}")


@nox.session(python=PYTHON_VERSIONS)
def integration_tests(session: nox.Session) -> None:
    """Run integration tests across multiple Python versions.

    This session runs integration tests that verify cross-system
    coordination scenarios.

    Args:
        session: The Nox session object.

    Example:
        $ nox -s integration_tests
    """
    session.install(".[test]")
    session.run("pytest", "-m", "integration", "--cov=uuid_forge", *session.posargs)


@nox.session(python="3.11")
def security_check(session: nox.Session) -> None:
    """Run security vulnerability checks.

    This session checks for known security vulnerabilities in
    dependencies using safety.

    Args:
        session: The Nox session object.

    Example:
        $ nox -s security_check
    """
    session.install("safety")
    session.run("safety", "check", "--json")


@nox.session(python="3.11")
def doctests(session: nox.Session) -> None:
    """Run doctests from docstrings.

    This session extracts and runs all doctests found in docstrings
    throughout the codebase.

    Args:
        session: The Nox session object.

    Example:
        $ nox -s doctests
    """
    session.install(".[test]")
    session.run("pytest", "--doctest-modules", "src/uuid_forge", *session.posargs)
