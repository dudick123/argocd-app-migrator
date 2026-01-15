"""Tests for CLI interface."""

from pathlib import Path

from typer.testing import CliRunner

from argocd_app_migrator.cli import app
from argocd_app_migrator.version import __version__


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_version_flag(self, cli_runner: CliRunner) -> None:
        """Test --version flag displays version and exits."""
        result = cli_runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert __version__ in result.stdout
        assert "argocd-app-migrator" in result.stdout

    def test_help_flag(self, cli_runner: CliRunner) -> None:
        """Test --help flag displays help message."""
        result = cli_runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "ArgoCD Application" in result.stdout
        assert "--input-dir" in result.stdout
        assert "--recursive" in result.stdout
        assert "--dry-run" in result.stdout
        assert "--output-dir" in result.stdout

    def test_no_arguments_fails(self, cli_runner: CliRunner) -> None:
        """Test that CLI fails without required --input-dir option."""
        result = cli_runner.invoke(app, [])

        assert result.exit_code != 0
        # Typer sends error messages to output
        error_output = result.output
        assert "input-dir" in error_output.lower() or "required" in error_output.lower()


class TestInputValidation:
    """Test input directory validation."""

    def test_valid_input_directory(
        self, cli_runner: CliRunner, sample_input_dir: Path
    ) -> None:
        """Test CLI accepts valid input directory with --input-dir."""
        result = cli_runner.invoke(app, ["--input-dir", str(sample_input_dir)])

        assert result.exit_code == 0
        assert "Input Directory" in result.stdout
        # Path may be wrapped across lines by Rich, so check for the directory name
        assert sample_input_dir.name in result.stdout

    def test_nonexistent_directory_fails(self, cli_runner: CliRunner) -> None:
        """Test CLI fails with nonexistent directory."""
        result = cli_runner.invoke(app, ["--input-dir", "/nonexistent/path"])

        assert result.exit_code != 0
        # Typer sends error messages to output (combined stdout/stderr)
        error_output = result.output
        assert (
            "does not exist" in error_output.lower()
            or "invalid" in error_output.lower()
        )

    def test_file_instead_of_directory_fails(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test CLI fails when given a file instead of directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        result = cli_runner.invoke(app, ["-i", str(test_file)])

        assert result.exit_code != 0


class TestFlags:
    """Test CLI flags and options."""

    def test_recursive_flag(
        self, cli_runner: CliRunner, sample_input_dir: Path
    ) -> None:
        """Test --recursive flag is recognized."""
        result = cli_runner.invoke(
            app, ["--input-dir", str(sample_input_dir), "--recursive"]
        )

        assert result.exit_code == 0
        assert (
            "Recursive Scan: True" in result.stdout
            or "Recursive Scan: [cyan]True" in result.stdout
        )

    def test_recursive_short_flag(
        self, cli_runner: CliRunner, sample_input_dir: Path
    ) -> None:
        """Test -r short flag works, also test -i short flag for input."""
        result = cli_runner.invoke(app, ["-i", str(sample_input_dir), "-r"])

        assert result.exit_code == 0

    def test_dry_run_flag(self, cli_runner: CliRunner, sample_input_dir: Path) -> None:
        """Test --dry-run flag is recognized."""
        result = cli_runner.invoke(app, ["-i", str(sample_input_dir), "--dry-run"])

        assert result.exit_code == 0
        assert (
            "Dry Run: True" in result.stdout or "Dry Run: [cyan]True" in result.stdout
        )

    def test_output_dir_option(
        self, cli_runner: CliRunner, sample_input_dir: Path, sample_output_dir: Path
    ) -> None:
        """Test --output-dir option accepts path."""
        result = cli_runner.invoke(
            app,
            [
                "--input-dir",
                str(sample_input_dir),
                "--output-dir",
                str(sample_output_dir),
            ],
        )

        assert result.exit_code == 0
        assert "Output Directory" in result.stdout
        # Path may be wrapped across lines by Rich, so check for the directory name
        assert sample_output_dir.name in result.stdout

    def test_output_dir_short_option(
        self, cli_runner: CliRunner, sample_input_dir: Path, sample_output_dir: Path
    ) -> None:
        """Test -o short option works."""
        result = cli_runner.invoke(
            app, ["-i", str(sample_input_dir), "-o", str(sample_output_dir)]
        )

        assert result.exit_code == 0

    def test_combined_flags(
        self,
        cli_runner: CliRunner,
        sample_input_dir: Path,
        sample_output_dir: Path,
    ) -> None:
        """Test multiple flags can be combined."""
        result = cli_runner.invoke(
            app,
            [
                "-i",
                str(sample_input_dir),
                "--recursive",
                "--dry-run",
                "--output-dir",
                str(sample_output_dir),
            ],
        )

        assert result.exit_code == 0
        assert (
            "Recursive Scan: True" in result.stdout
            or "Recursive Scan: [cyan]True" in result.stdout
        )
        assert (
            "Dry Run: True" in result.stdout or "Dry Run: [cyan]True" in result.stdout
        )


class TestOutputMessages:
    """Test CLI output messages and formatting."""

    def test_welcome_message_displayed(
        self, cli_runner: CliRunner, sample_input_dir: Path
    ) -> None:
        """Test welcome message is displayed."""
        result = cli_runner.invoke(app, ["--input-dir", str(sample_input_dir)])

        assert result.exit_code == 0
        assert "ArgoCD Application Migrator" in result.stdout
        assert __version__ in result.stdout

    def test_configuration_displayed(
        self, cli_runner: CliRunner, sample_input_dir: Path
    ) -> None:
        """Test configuration summary is displayed."""
        result = cli_runner.invoke(app, ["-i", str(sample_input_dir)])

        assert result.exit_code == 0
        assert "Configuration:" in result.stdout
        assert "Input Directory" in result.stdout
        assert "Recursive Scan" in result.stdout
        assert "Dry Run" in result.stdout
        assert "Output Directory" in result.stdout

    def test_success_message_displayed(
        self, cli_runner: CliRunner, sample_input_dir: Path
    ) -> None:
        """Test success message is displayed."""
        result = cli_runner.invoke(app, ["--input-dir", str(sample_input_dir)])

        assert result.exit_code == 0
        assert "initialized successfully" in result.stdout or "✓" in result.stdout
