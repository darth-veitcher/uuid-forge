"""Command-line interface for UUID-Forge.

This module provides a comprehensive CLI for generating deterministic UUIDs,
managing configuration, and validating security settings. The CLI is designed
as a first-class interface to the library, suitable for both interactive use
and automation in scripts and CI/CD pipelines.
"""

import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from uuid_forge.config import (
    init_config_file,
    load_config_from_env,
    validate_config_security,
)
from uuid_forge.core import (
    IDConfig,
    extract_uuid_from_prefixed,
    generate_salt,
    generate_uuid_only,
    generate_uuid_with_prefix,
)

# Initialize Typer app and Rich console
app = typer.Typer(
    name="uuid-forge",
    help="Deterministic UUID generation for cross-system coordination",
    add_completion=False,
)
console = Console()


@app.command()
def generate(
    entity_type: str = typer.Argument(
        ..., help="Type of entity (e.g., 'invoice', 'order', 'user')"
    ),
    prefix: str | None = typer.Option(
        None, "--prefix", "-p", help="Human-readable prefix for the UUID"
    ),
    separator: str = typer.Option(
        "-", "--separator", "-s", help="Separator between prefix and UUID"
    ),
    namespace: str | None = typer.Option(
        None, "--namespace", "-n", help="Custom namespace domain (e.g., 'mycompany.com')"
    ),
    salt: str | None = typer.Option(
        None, "--salt", help="Cryptographic salt (leave empty to use env var)"
    ),
    use_env: bool = typer.Option(
        True, "--env/--no-env", help="Load configuration from environment variables"
    ),
    attributes: list[str] | None = typer.Option(
        None, "--attr", "-a", help="Attributes in key=value format (can be used multiple times)"
    ),
) -> None:
    """Generate a deterministic UUID for an entity.

    This command generates a UUID that will be identical for the same inputs
    and configuration. Perfect for coordinating IDs across multiple storage
    systems (Postgres, S3, Redis, etc.) without requiring inter-service
    communication.

    Examples:
        # Simple generation with environment config
        $ uuid-forge generate invoice --attr region=EUR --attr number=12345

        # With human-readable prefix
        $ uuid-forge generate invoice --prefix INV-EUR --attr region=EUR --attr number=12345

        # Custom namespace and salt
        $ uuid-forge generate user --namespace mycompany.com --salt "my-secret" --attr email=user@example.com

        # Using environment variables only
        $ export UUID_FORGE_SALT="xvW9Kz_kRzPmNqYvTaWcXdYeFgZhAiB"
        $ export UUID_FORGE_NAMESPACE="mycompany.com"
        $ uuid-forge generate invoice --attr region=EUR --attr number=12345
    """
    try:
        # Parse attributes
        kwargs = {}
        if attributes:
            for attr in attributes:
                if "=" not in attr:
                    console.print(
                        f"[red]Error:[/red] Invalid attribute format: {attr}. Use key=value format."
                    )
                    raise typer.Exit(code=1)
                key, value = attr.split("=", 1)
                kwargs[key.strip()] = value.strip()

        # Build configuration
        if use_env and not namespace and not salt:
            # Load from environment
            config = load_config_from_env()
        else:
            # Build custom config
            import uuid as uuid_module

            ns = (
                uuid_module.uuid5(uuid_module.NAMESPACE_DNS, namespace)
                if namespace
                else uuid_module.NAMESPACE_DNS
            )
            config = IDConfig(namespace=ns, salt=salt or "")

        # Validate configuration security
        is_valid, messages = validate_config_security(config, strict=False)
        if not is_valid:
            console.print("[yellow]⚠ Security Warning:[/yellow]")
            for msg in messages:
                console.print(f"  {msg}")
            console.print()

        # Generate UUID
        if prefix:
            result = generate_uuid_with_prefix(
                entity_type, config=config, prefix=prefix, separator=separator, **kwargs
            )
        else:
            uuid_obj = generate_uuid_only(entity_type, config=config, **kwargs)
            result = str(uuid_obj)

        # Display result
        console.print(
            Panel(
                f"[green bold]{result}[/green bold]",
                title=f"Generated UUID for [cyan]{entity_type}[/cyan]",
                border_style="green",
            )
        )

        # Show reproducibility info
        console.print("\n[dim]Reproducibility:[/dim]")
        console.print(f"  Entity Type: {entity_type}")
        if kwargs:
            console.print("  Attributes:")
            for key, value in kwargs.items():
                console.print(f"    {key} = {value}")
        console.print(f"  Namespace: {config.namespace}")
        console.print(f"  Salt: {'<set>' if config.salt else '<not set>'}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def extract(
    prefixed_id: str = typer.Argument(..., help="Prefixed UUID to extract from"),
    separator: str = typer.Option(
        "-", "--separator", "-s", help="Separator between prefix and UUID"
    ),
) -> None:
    """Extract the UUID from a prefixed identifier.

    This command parses a prefixed UUID (created with --prefix option) and
    extracts just the UUID portion. Useful for database queries or API calls
    that require the pure UUID.

    Examples:
        # Extract from prefixed UUID
        $ uuid-forge extract "INV-EUR-550e8400-e29b-41d4-a716-446655440000"

        # With custom separator
        $ uuid-forge extract "INV_EUR_550e8400-e29b-41d4-a716-446655440000" --separator "_"
    """
    try:
        extracted = extract_uuid_from_prefixed(prefixed_id, separator=separator)

        console.print(
            Panel(
                f"[green bold]{extracted}[/green bold]",
                title="Extracted UUID",
                border_style="green",
            )
        )

        console.print("\n[dim]Input:[/dim]")
        console.print(f"  Prefixed ID: {prefixed_id}")
        console.print(f"  Separator: {separator}")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def new_salt(
    length: int = typer.Option(32, "--length", "-l", help="Length of salt in bytes (minimum 16)"),
) -> None:
    """Generate a new cryptographic salt for UUID generation.

    This command creates a secure random salt that should be used in production
    environments. The salt should be generated once per deployment and stored
    securely in environment variables or secret management systems.

    WARNING: Keep the salt secret! Anyone with the salt can predict your UUIDs.

    Examples:
        # Generate standard 32-byte salt
        $ uuid-forge new-salt

        # Generate longer salt for extra security
        $ uuid-forge new-salt --length 64
    """
    try:
        salt = generate_salt(length=length)

        console.print(
            Panel(f"[green bold]{salt}[/green bold]", title="Generated Salt", border_style="green")
        )

        console.print("\n[yellow]⚠ Important Security Notes:[/yellow]")
        console.print("  1. Keep this salt SECRET - never commit to version control")
        console.print("  2. Store in environment variable: UUID_FORGE_SALT")
        console.print("  3. Use the same salt across all services for consistency")
        console.print("  4. Anyone with this salt can predict your UUIDs")

        console.print("\n[dim]Quick Setup:[/dim]")
        console.print(f"  export UUID_FORGE_SALT='{salt}'")
        console.print("  # Or add to .env file:")
        console.print(f"  echo 'UUID_FORGE_SALT={salt}' >> .env")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def init(
    output: Path = typer.Option(
        Path(".env"), "--output", "-o", help="Output path for configuration file"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file"),
) -> None:
    """Initialize a new configuration file with generated salt.

    This command creates a template configuration file (.env format) with a
    freshly generated salt and usage instructions. Perfect for setting up new
    projects or deployments.

    Examples:
        # Create .env in current directory
        $ uuid-forge init

        # Create in custom location
        $ uuid-forge init --output config/uuid.env

        # Overwrite existing file
        $ uuid-forge init --force
    """
    try:
        output_path = init_config_file(output_path=output, force=force)

        console.print(
            Panel(
                f"[green]Configuration file created successfully![/green]\n\n"
                f"Location: [cyan]{output_path.absolute()}[/cyan]",
                title="✓ Initialization Complete",
                border_style="green",
            )
        )

        console.print("\n[yellow]Next Steps:[/yellow]")
        console.print("  1. Review the generated configuration file")
        console.print("  2. Add the file to .gitignore if not already present")
        console.print("  3. Load environment variables:")
        console.print(f"     source {output_path}")
        console.print("  4. Or use python-dotenv in your application:")

        code = """from dotenv import load_dotenv
load_dotenv()

from uuid_forge.config import load_config_from_env
config = load_config_from_env()"""

        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        console.print(syntax)

    except FileExistsError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("\n[dim]Use --force to overwrite the existing file.[/dim]")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def validate(
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as errors"),
) -> None:
    """Validate current configuration for security best practices.

    This command checks your current configuration (loaded from environment
    variables) against security best practices. Use this in CI/CD pipelines
    to ensure production deployments have secure configurations.

    Examples:
        # Validate current config
        $ uuid-forge validate

        # Strict mode (warnings cause failure)
        $ uuid-forge validate --strict
    """
    try:
        config = load_config_from_env()
        is_valid, messages = validate_config_security(config, strict=strict)

        if is_valid and not messages:
            console.print(
                Panel(
                    "[green]✓ Configuration is secure and follows best practices![/green]",
                    border_style="green",
                )
            )
        else:
            # Create results table
            table = Table(title="Configuration Validation Results")
            table.add_column("Status", style="cyan")
            table.add_column("Message")

            for msg in messages:
                if "CRITICAL" in msg:
                    table.add_row("❌ FAIL", msg)
                elif "WARNING" in msg:
                    table.add_row("⚠ WARN", msg)
                else:
                    table.add_row("ℹ INFO", msg)

            console.print(table)

            if not is_valid:
                console.print("\n[red bold]Validation Failed[/red bold]")
                console.print("\nRecommended actions:")
                console.print("  1. Generate a salt: uuid-forge new-salt")
                console.print(
                    "  2. Set environment variable: export UUID_FORGE_SALT='<generated-salt>'"
                )
                console.print("  3. Or initialize config file: uuid-forge init")
                raise typer.Exit(code=1)
            else:
                console.print("\n[yellow]Validation passed with warnings[/yellow]")
                if strict:
                    console.print("[red]Strict mode enabled - treating as failure[/red]")
                    raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def info() -> None:
    """Display information about current configuration and usage.

    This command shows the current configuration loaded from environment
    variables, system information, and usage examples. Useful for debugging
    configuration issues.
    """
    try:
        config = load_config_from_env()

        # Configuration info
        console.print(Panel("[bold]Current Configuration[/bold]", style="cyan"))

        info_table = Table(show_header=False, box=None)
        info_table.add_column("Key", style="cyan")
        info_table.add_column("Value")

        info_table.add_row("Namespace", str(config.namespace))
        info_table.add_row("Salt", "<set>" if config.salt else "[red]<not set>[/red]")
        info_table.add_row("Salt Length", str(len(config.salt)) if config.salt else "0")

        console.print(info_table)

        # Security status
        is_valid, messages = validate_config_security(config, strict=False)
        if is_valid and not messages:
            console.print("\n[green]✓ Configuration is secure[/green]")
        else:
            console.print(f"\n[yellow]⚠ {len(messages)} issue(s) found[/yellow]")

        # Usage example
        console.print("\n[bold]Quick Example:[/bold]")
        example_code = """# Generate UUID
from uuid_forge.core import generate_uuid_only
from uuid_forge.config import load_config_from_env

config = load_config_from_env()
uuid = generate_uuid_only(
    "invoice",
    config=config,
    region="EUR",
    number=12345
)
# UUID: {uuid}"""

        syntax = Syntax(example_code, "python", theme="monokai")
        console.print(syntax)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def docs(
    serve: bool = typer.Option(
        True, "--serve/--build", help="Serve docs with live reload or just build"
    ),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to serve on"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to serve on"),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Open browser automatically"),
) -> None:
    """Build or serve the documentation locally.

    This command builds the MkDocs documentation and optionally serves it
    with live reload. Perfect for local development and documentation preview.
    No Docker required!

    Examples:
        # Serve docs with live reload (default)
        $ uuid-forge docs

        # Serve on different port
        $ uuid-forge docs --port 8080

        # Build without serving
        $ uuid-forge docs --build

        # Serve on all interfaces
        $ uuid-forge docs --host 0.0.0.0 --port 8000
    """
    try:
        # Check if mkdocs is installed
        result = subprocess.run(
            ["mkdocs", "--version"], check=False, capture_output=True, text=True
        )

        if result.returncode != 0:
            console.print("[red]Error:[/red] mkdocs not installed")
            console.print("\n[yellow]Install documentation dependencies:[/yellow]")
            console.print('  uv pip install -e ".[docs]"')
            console.print("  # or")
            console.print('  pip install "uuid-forge[docs]"')
            raise typer.Exit(code=1)
    except FileNotFoundError:
        console.print("[red]Error:[/red] mkdocs not found")
        console.print("\n[yellow]Install documentation dependencies:[/yellow]")
        console.print('  uv pip install -e ".[docs]"')
        console.print("  # or")
        console.print('  pip install mkdocs mkdocs-material "mkdocstrings[python]"')
        raise typer.Exit(code=1) from None

    # Find docs directory
    docs_dir = Path("docs")
    mkdocs_yml = Path("mkdocs.yml")

    if not docs_dir.exists() or not mkdocs_yml.exists():
        console.print("[red]Error:[/red] Documentation files not found")
        console.print("\n[yellow]Expected project structure:[/yellow]")
        console.print("  project-root/")
        console.print("    ├── docs/")
        console.print("    ├── mkdocs.yml")
        console.print("    └── src/")
        console.print(f"\nCurrent directory: [cyan]{Path.cwd()}[/cyan]")
        raise typer.Exit(code=1)

    if serve:
        console.print(
            Panel(
                f"[green]Starting documentation server...[/green]\n\n"
                f"Host: [cyan]{host}[/cyan]\n"
                f"Port: [cyan]{port}[/cyan]\n"
                f"URL: [cyan]http://{host}:{port}[/cyan]\n\n"
                f"[dim]Press Ctrl+C to stop[/dim]",
                title="📚 Documentation Server",
                border_style="green",
            )
        )

        # Build command
        cmd = [
            "mkdocs",
            "serve",
            "--dev-addr",
            f"{host}:{port}",
        ]

        if not open_browser:
            cmd.append("--no-livereload")

        try:
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Documentation server stopped[/yellow]")
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            console.print("\n[red]Error:[/red] Failed to serve docs")
            console.print(f"[dim]{e}[/dim]")
            raise typer.Exit(code=1) from e
    else:
        console.print("[cyan]Building documentation...[/cyan]")

        try:
            result = subprocess.run(
                ["mkdocs", "build", "--strict"], check=True, capture_output=True, text=True
            )

            console.print(
                Panel(
                    "[green]Documentation built successfully![/green]\n\n"
                    "Output: [cyan]docs/site/[/cyan]\n\n"
                    "[dim]Open docs/site/index.html in your browser[/dim]",
                    title="✓ Build Complete",
                    border_style="green",
                )
            )
        except subprocess.CalledProcessError as e:
            console.print("[red]Error:[/red] Failed to build docs")
            if e.stderr:
                console.print(f"\n[dim]{e.stderr}[/dim]")
            raise typer.Exit(code=1) from e


@app.command()
def test(
    coverage: bool = typer.Option(
        True, "--coverage/--no-coverage", help="Run with coverage reporting"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose test output"),
    pattern: str | None = typer.Option(
        None, "--pattern", "-k", help="Only run tests matching pattern"
    ),
    fail_fast: bool = typer.Option(False, "--fail-fast", "-x", help="Stop on first test failure"),
    parallel: bool = typer.Option(False, "--parallel", "-n", help="Run tests in parallel"),
) -> None:
    """Run the test suite with pytest.

    This command runs the project's test suite using pytest with various options
    for coverage, verbosity, and test selection. Perfect for local development
    and CI/CD pipelines.

    Examples:
        # Run all tests with coverage (default)
        $ uuid-forge test

        # Run tests without coverage
        $ uuid-forge test --no-coverage

        # Run specific test pattern
        $ uuid-forge test --pattern "test_core"

        # Verbose output and fail fast
        $ uuid-forge test --verbose --fail-fast
    """
    console.print("[cyan]Running test suite...[/cyan]")

    # Base pytest command
    cmd = ["pytest"]

    # Add coverage options
    if coverage:
        cmd.extend(
            [
                "--cov=uuid_forge",
                "--cov-report=term-missing",
                "--cov-report=html",
                "--cov-report=xml",
            ]
        )

    # Add verbosity
    if verbose:
        cmd.append("-v")

    # Add pattern matching
    if pattern:
        cmd.extend(["-k", pattern])

    # Add fail fast
    if fail_fast:
        cmd.append("-x")

    # Add parallel execution (requires pytest-xdist)
    if parallel:
        cmd.extend(["-n", "auto"])

    # Add test paths
    cmd.append("tests")

    console.print(f"[dim]Running: {' '.join(cmd)}[/dim]\n")

    try:
        subprocess.run(cmd, check=True)

        if coverage:
            console.print("\n" + "=" * 50)
            console.print("[green]✓ Tests completed successfully![/green]")
            console.print("\n[cyan]Coverage reports generated:[/cyan]")
            console.print("  • Terminal: displayed above")
            console.print("  • HTML: [cyan]htmlcov/index.html[/cyan]")
            console.print("  • XML: [cyan]coverage.xml[/cyan]")
        else:
            console.print("\n[green]✓ Tests completed successfully![/green]")

    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]✗ Tests failed with exit code {e.returncode}[/red]")
        raise typer.Exit(code=e.returncode) from e
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Test run interrupted[/yellow]")
        raise typer.Exit(code=130) from None


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
