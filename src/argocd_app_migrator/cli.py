"""CLI interface for ArgoCD Application migrator."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from argocd_app_migrator.parser import Parser, ParserError
from argocd_app_migrator.scanner import Scanner, ScannerError
from argocd_app_migrator.version import __version__

# Initialize Typer app
app = typer.Typer(
    name="argocd-app-migrator",
    help=(
        "Migrate ArgoCD Application YAML manifests to JSON configs "
        "for ApplicationSets"
    ),
    add_completion=False,
)

# Initialize Rich console for styled output
console = Console()


def version_callback(value: bool) -> None:
    """Display version and exit."""
    if value:
        console.print(
            f"[bold blue]argocd-app-migrator[/bold blue] version {__version__}"
        )
        raise typer.Exit()


@app.command()
def migrate(
    input_dir: Path = typer.Option(
        ...,
        "--input-dir",
        "-i",
        help="Directory containing ArgoCD Application YAML files",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory for generated JSON files (default: current directory)",
        file_okay=False,
        dir_okay=True,
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Scan directories recursively for YAML files",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Print output to terminal without writing files",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """
    Migrate ArgoCD Application YAML manifests to ApplicationSet JSON configs.

    This command scans the specified input directory for ArgoCD Application
    YAML files, extracts relevant information, and generates JSON configuration
    files for new ApplicationSets using Git Generators.

    Examples:

        Basic migration:

        $ argocd-app-migrator --input-dir /path/to/apps

        Using short flags:

        $ argocd-app-migrator -i /path/to/apps

        Recursive scan with dry-run:

        $ argocd-app-migrator -i /path/to/apps --recursive --dry-run

        Custom output directory:

        $ argocd-app-migrator -i /path/to/apps -o /path/to/output
    """
    # Display welcome message
    console.print(
        Panel.fit(
            f"[bold blue]ArgoCD Application Migrator[/bold blue] v{__version__}",
            border_style="blue",
        )
    )

    # Validate and set output directory
    if output_dir is None:
        output_dir = Path.cwd()

    # Display configuration
    console.print("\n[bold]Configuration:[/bold]")
    console.print(f"  Input Directory: [cyan]{input_dir}[/cyan]")
    console.print(f"  Recursive Scan: [cyan]{recursive}[/cyan]")
    console.print(f"  Dry Run: [cyan]{dry_run}[/cyan]")
    console.print(f"  Output Directory: [cyan]{output_dir}[/cyan]")

    # Scanner: Find YAML files
    try:
        scanner = Scanner()
        yaml_files = scanner.scan(input_dir=input_dir, recursive=recursive)

        console.print("\n[bold]Scan Results:[/bold]")
        console.print(f"  Found {len(yaml_files)} YAML file(s)")

        if len(yaml_files) == 0:
            console.print(
                "[yellow]Warning:[/yellow] No YAML files found in input directory"
            )
            return

        # Display files in dry-run mode
        if dry_run:
            console.print("\n[bold]YAML Files Found:[/bold]")
            for yaml_file in yaml_files:
                console.print(f"  - {yaml_file}")

        # Parser: Extract Application data
        parser = Parser()
        parse_results = parser.parse_batch(yaml_files)

        # Separate successful and failed parses
        successful = [r for r in parse_results if r.success]
        failed = [r for r in parse_results if not r.success]

        console.print("\n[bold]Parse Results:[/bold]")
        console.print(f"  Successfully parsed: {len(successful)}")
        console.print(f"  Failed to parse: {len(failed)}")

        # Display failed files
        if failed:
            console.print("\n[bold yellow]Failed Files:[/bold yellow]")
            for result in failed:
                console.print(f"  - {result.file_path.name}")
                if dry_run:
                    console.print(f"    Error: {result.error_message}")

        # Display successful parses in dry-run mode
        if successful and dry_run:
            console.print("\n[bold green]Successfully Parsed:[/bold green]")
            for result in successful:
                console.print(f"  - {result.file_path.name}")
                console.print(f"    App: {result.data.metadata.name}")
                console.print(f"    Project: {result.data.project}")

        # Stop if no valid applications found
        if len(successful) == 0:
            console.print("\n[yellow]No valid ArgoCD Applications found[/yellow]")
            return

        # Placeholder for Migrator stage
        console.print("\n[yellow]Note:[/yellow] Migrator implementation coming next!")
        console.print("  - Migrator: Generate JSON configs")
        console.print("  - Validator: Validate against schema")

    except (ScannerError, ParserError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
