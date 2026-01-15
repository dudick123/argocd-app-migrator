"""
Scanner module for finding YAML files in directories.

This module provides the Scanner class, which is responsible for locating
ArgoCD Application YAML manifest files in a given directory. It supports
both top-level and recursive directory scanning.

Example:
    Basic usage with non-recursive scan:

    >>> from pathlib import Path
    >>> from argocd_app_migrator.scanner import Scanner
    >>>
    >>> scanner = Scanner()
    >>> files = scanner.scan(Path("/path/to/apps"), recursive=False)
    >>> print(f"Found {len(files)} YAML files")

    Recursive scan:

    >>> files = scanner.scan(Path("/path/to/apps"), recursive=True)

Classes:
    Scanner: Main class for scanning directories for YAML files.
    ScannerError: Exception raised when scanning fails.
"""

from pathlib import Path


class ScannerError(Exception):
    """Exception raised when directory scanning fails.

    This exception is raised when the scanner encounters an error while
    attempting to scan a directory, such as permission errors or I/O errors.

    Args:
        message: Description of the error that occurred.

    Example:
        >>> raise ScannerError("Failed to scan directory: Permission denied")
    """

    pass


class Scanner:
    """Scan directories for YAML files.

    The Scanner class provides functionality to find all YAML files
    (with .yaml or .yml extensions) in a directory. It supports both
    shallow (top-level only) and recursive (including subdirectories) scans.

    Attributes:
        None (stateless class)

    Example:
        >>> scanner = Scanner()
        >>> yaml_files = scanner.scan(Path("/apps"), recursive=True)
        >>> for file in yaml_files:
        ...     print(file)
    """

    def __init__(self) -> None:
        """Initialize the Scanner.

        The Scanner is stateless and requires no initialization parameters.
        """
        pass

    def scan(self, input_dir: Path, recursive: bool = False) -> list[Path]:
        """
        Find all YAML files in the specified directory.

        Scans the input directory for files with .yaml or .yml extensions.
        Returns a sorted list of absolute paths to all YAML files found.

        Args:
            input_dir: Directory to scan. Must exist and be readable.
                      This is pre-validated by the CLI.
            recursive: If True, scans all subdirectories recursively.
                      If False, only scans the top-level directory.
                      Defaults to False.

        Returns:
            A sorted list of absolute Path objects pointing to YAML files.
            Returns an empty list if no YAML files are found.

        Raises:
            ScannerError: If the directory becomes inaccessible during
                         scanning due to permission errors or I/O errors.

        Example:
            >>> scanner = Scanner()
            >>> # Non-recursive scan
            >>> files = scanner.scan(Path("/apps"), recursive=False)
            >>> # Recursive scan
            >>> all_files = scanner.scan(Path("/apps"), recursive=True)

        Note:
            - Both .yaml and .yml extensions are recognized
            - Hidden files (starting with .) are included
            - Symlinks are followed and included if they resolve to files
            - Directories matching *.yaml/*.yml are filtered out
            - Results are always sorted alphabetically for deterministic behavior
        """
        yaml_files: list[Path] = []

        try:
            if recursive:
                # Use rglob for recursive search through all subdirectories
                yaml_files.extend(input_dir.rglob("*.yaml"))
                yaml_files.extend(input_dir.rglob("*.yml"))
            else:
                # Use glob for top-level directory only
                yaml_files.extend(input_dir.glob("*.yaml"))
                yaml_files.extend(input_dir.glob("*.yml"))
        except (OSError, PermissionError) as e:
            raise ScannerError(f"Failed to scan directory '{input_dir}': {e}") from e

        # Filter to files only (exclude directories) and resolve to absolute paths
        resolved = [f.resolve() for f in yaml_files if f.is_file()]

        # Sort for deterministic behavior
        return sorted(resolved)
