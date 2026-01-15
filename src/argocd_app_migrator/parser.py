"""
Parser module for extracting ArgoCD Application fields from YAML files.

This module provides the Parser class, which is responsible for parsing
ArgoCD Application YAML manifests, validating their structure, and extracting
relevant fields for migration to ApplicationSet JSON configs.

Example:
    Basic usage with single file:

    >>> from pathlib import Path
    >>> from argocd_app_migrator.parser import Parser
    >>>
    >>> parser = Parser()
    >>> result = parser.parse(Path("/path/to/app.yaml"))
    >>> if result.success:
    ...     print(f"Parsed: {result.data.metadata.name}")

    Batch parsing:

    >>> results = parser.parse_batch([Path("app1.yaml"), Path("app2.yaml")])
    >>> successful = [r for r in results if r.success]
    >>> print(f"Successfully parsed {len(successful)} applications")

Classes:
    ParsedSourceDirectory: Source directory configuration.
    ParsedSource: Source configuration with transformed field names.
    ParsedDestination: Destination configuration.
    ParsedMetadata: Metadata with name, annotations, and labels.
    ParsedApplication: Complete parsed ArgoCD Application.
    ParseResult: Result wrapper for parse operations.
    Parser: Main class for parsing ArgoCD Application YAML files.
    ParserError: Exception raised when parsing operations fail.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, cast

import yaml


class ParserError(Exception):
    """Exception raised when parsing operations fail.

    This exception is raised when the parser encounters a critical error
    that prevents it from continuing, such as an invalid YAML file or
    a missing required field.

    Args:
        message: Description of the error that occurred.

    Example:
        >>> raise ParserError("Failed to parse YAML: Invalid syntax")
    """

    pass


@dataclass(frozen=True)
class ParsedSourceDirectory:
    """Represents source.directory configuration.

    This dataclass holds the directory configuration for an ArgoCD Application
    source, specifically whether the directory should be scanned recursively.

    Attributes:
        recurse: Whether to recursively scan the directory. Defaults to False.

    Example:
        >>> dir_config = ParsedSourceDirectory(recurse=True)
        >>> print(dir_config.recurse)
        True
    """

    recurse: bool = False


@dataclass(frozen=True)
class ParsedSource:
    """Represents the source configuration from an ArgoCD Application.

    This dataclass holds the Git repository source information with transformed
    field names to match the ApplicationSet JSON config format.

    Attributes:
        repo_url: Git repository URL.
        revision: Git revision (branch, tag, or commit). Transformed from
            'targetRevision' in the original Application manifest.
        manifest_path: Path to manifests within the repository. Transformed
            from 'path' in the original Application manifest.
        directory: Optional directory configuration for recursive scanning.

    Example:
        >>> source = ParsedSource(
        ...     repo_url="https://github.com/example/repo.git",
        ...     revision="main",
        ...     manifest_path="./manifests"
        ... )
    """

    repo_url: str
    revision: str
    manifest_path: str
    directory: Optional[ParsedSourceDirectory] = None


@dataclass(frozen=True)
class ParsedDestination:
    """Represents the destination configuration from an ArgoCD Application.

    This dataclass holds the destination cluster and namespace information.
    Either 'server' or 'name' should be present (or both).

    Attributes:
        server: Kubernetes API server URL (e.g., https://kubernetes.default.svc).
        name: Cluster name as registered in ArgoCD.
        namespace: Target namespace for deployment.

    Example:
        >>> dest = ParsedDestination(
        ...     server="https://kubernetes.default.svc",
        ...     namespace="default"
        ... )
    """

    server: Optional[str] = None
    name: Optional[str] = None
    namespace: str = ""


@dataclass(frozen=True)
class ParsedMetadata:
    """Represents metadata from an ArgoCD Application.

    This dataclass holds the application metadata including name, annotations,
    and labels.

    Attributes:
        name: Application name.
        annotations: Dictionary of annotations. Defaults to empty dict.
        labels: Dictionary of labels. Defaults to empty dict.

    Example:
        >>> metadata = ParsedMetadata(
        ...     name="my-app",
        ...     annotations={"argocd.argoproj.io/sync-wave": "40"},
        ...     labels={"environment": "dev"}
        ... )
    """

    name: str
    annotations: dict[str, str]
    labels: dict[str, str]


@dataclass(frozen=True)
class ParsedApplication:
    """Represents a fully parsed ArgoCD Application.

    This dataclass holds all extracted and transformed data from an ArgoCD
    Application manifest, ready for use by the Migrator stage.

    Attributes:
        metadata: Application metadata (name, annotations, labels).
        project: ArgoCD project name.
        source: Source repository configuration.
        destination: Destination cluster and namespace.
        enable_sync_policy: Whether syncPolicy is defined (boolean conversion).

    Example:
        >>> app = ParsedApplication(
        ...     metadata=metadata,
        ...     project="default",
        ...     source=source,
        ...     destination=destination,
        ...     enable_sync_policy=True
        ... )
    """

    metadata: ParsedMetadata
    project: str
    source: ParsedSource
    destination: ParsedDestination
    enable_sync_policy: bool


@dataclass(frozen=True)
class ParseResult:
    """Result of parsing a single YAML file.

    This dataclass wraps the result of a parse operation, indicating success
    or failure and providing either the parsed data or an error message.

    Attributes:
        success: Whether the parse operation succeeded.
        file_path: Path to the file that was parsed.
        data: Parsed application data if successful, None otherwise.
        error_message: Error description if failed, None otherwise.

    Example:
        >>> # Successful parse
        >>> result = ParseResult(
        ...     success=True,
        ...     file_path=Path("app.yaml"),
        ...     data=parsed_app
        ... )
        >>>
        >>> # Failed parse
        >>> result = ParseResult(
        ...     success=False,
        ...     file_path=Path("bad.yaml"),
        ...     error_message="Missing required field: metadata.name"
        ... )
    """

    success: bool
    file_path: Path
    data: Optional[ParsedApplication] = None
    error_message: Optional[str] = None


class Parser:
    """Parse ArgoCD Application YAML files and extract relevant fields.

    The Parser class provides functionality to parse ArgoCD Application YAML
    manifests, validate their structure, extract fields, and transform them
    for use in ApplicationSet JSON configs.

    Attributes:
        None (stateless class)

    Example:
        >>> parser = Parser()
        >>> result = parser.parse(Path("app.yaml"))
        >>> if result.success:
        ...     print(f"Parsed {result.data.metadata.name}")
        ... else:
        ...     print(f"Error: {result.error_message}")
    """

    def __init__(self) -> None:
        """Initialize the Parser.

        The Parser is stateless and requires no initialization parameters.
        """
        pass

    def parse(self, yaml_file: Path) -> ParseResult:
        """
        Parse a single ArgoCD Application YAML file.

        Loads the YAML file, validates it is a valid ArgoCD Application,
        extracts relevant fields, and returns a ParseResult indicating
        success or failure.

        Args:
            yaml_file: Path to the YAML file to parse.

        Returns:
            ParseResult with success=True and data on success, or
            success=False with error_message on failure.

        Example:
            >>> parser = Parser()
            >>> result = parser.parse(Path("app.yaml"))
            >>> if result.success:
            ...     print(f"Project: {result.data.project}")
        """
        try:
            content = self._load_yaml(yaml_file)
            self._validate_structure(content)

            metadata = self._extract_metadata(content)
            source = self._extract_source(content)
            destination = self._extract_destination(content)
            project = content["spec"]["project"]
            enable_sync_policy = self._extract_sync_policy(content)

            app = ParsedApplication(
                metadata=metadata,
                project=project,
                source=source,
                destination=destination,
                enable_sync_policy=enable_sync_policy,
            )

            return ParseResult(success=True, file_path=yaml_file, data=app)

        except Exception as e:
            return ParseResult(
                success=False,
                file_path=yaml_file,
                error_message=str(e),
            )

    def parse_batch(self, yaml_files: list[Path]) -> list[ParseResult]:
        """
        Parse multiple YAML files and return results for all.

        Args:
            yaml_files: List of paths to YAML files to parse.

        Returns:
            List of ParseResult objects, one for each input file.

        Example:
            >>> parser = Parser()
            >>> files = [Path("app1.yaml"), Path("app2.yaml")]
            >>> results = parser.parse_batch(files)
            >>> successful = [r for r in results if r.success]
            >>> print(f"Parsed {len(successful)} of {len(files)} files")
        """
        return [self.parse(f) for f in yaml_files]

    def _load_yaml(self, yaml_file: Path) -> dict[str, Any]:
        """
        Load and parse a YAML file.

        Args:
            yaml_file: Path to the YAML file to load.

        Returns:
            Parsed YAML content as a dictionary.

        Raises:
            FileNotFoundError: If the file does not exist.
            yaml.YAMLError: If the YAML is malformed.
            IOError: If the file cannot be read.
        """
        try:
            with open(yaml_file, "r") as f:
                content = yaml.safe_load(f)
                if content is None:
                    raise ValueError("Empty YAML file")
                return cast(dict[str, Any], content)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {yaml_file}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax: {e}")
        except IOError as e:
            raise IOError(f"Failed to read file: {e}")

    def _validate_structure(self, content: dict[str, Any]) -> None:
        """
        Validate that the YAML content is a valid ArgoCD Application.

        Checks for required fields: apiVersion, kind, metadata.name,
        spec.project, spec.source, and spec.destination.

        Args:
            content: Parsed YAML content as a dictionary.

        Raises:
            ValueError: If any required field is missing or invalid.
        """
        # Check apiVersion
        if "apiVersion" not in content:
            raise ValueError("Missing required field: apiVersion")
        if content["apiVersion"] != "argoproj.io/v1alpha1":
            raise ValueError(
                f"Invalid apiVersion: {content['apiVersion']} "
                "(expected argoproj.io/v1alpha1)"
            )

        # Check kind
        if "kind" not in content:
            raise ValueError("Missing required field: kind")
        if content["kind"] != "Application":
            raise ValueError(f"Invalid kind: {content['kind']} (expected Application)")

        # Check metadata
        if "metadata" not in content:
            raise ValueError("Missing required field: metadata")
        if "name" not in content["metadata"]:
            raise ValueError("Missing required field: metadata.name")

        # Check spec
        if "spec" not in content:
            raise ValueError("Missing required field: spec")

        spec = content["spec"]

        # Check spec.project
        if "project" not in spec:
            raise ValueError("Missing required field: spec.project")

        # Check spec.source
        if "source" not in spec:
            raise ValueError("Missing required field: spec.source")

        source = spec["source"]
        if "repoURL" not in source:
            raise ValueError("Missing required field: spec.source.repoURL")
        if "targetRevision" not in source:
            raise ValueError("Missing required field: spec.source.targetRevision")
        if "path" not in source:
            raise ValueError("Missing required field: spec.source.path")

        # Check spec.destination
        if "destination" not in spec:
            raise ValueError("Missing required field: spec.destination")

        destination = spec["destination"]
        if "server" not in destination and "name" not in destination:
            raise ValueError(
                "Missing required field: spec.destination.server or "
                "spec.destination.name (at least one required)"
            )
        if "namespace" not in destination:
            raise ValueError("Missing required field: spec.destination.namespace")

    def _extract_metadata(self, content: dict[str, Any]) -> ParsedMetadata:
        """
        Extract metadata section from ArgoCD Application.

        Args:
            content: Parsed YAML content as a dictionary.

        Returns:
            ParsedMetadata with name, annotations, and labels.
        """
        metadata = content["metadata"]
        name = metadata["name"]
        annotations = metadata.get("annotations", {})
        labels = metadata.get("labels", {})

        return ParsedMetadata(
            name=name,
            annotations=dict(annotations) if annotations else {},
            labels=dict(labels) if labels else {},
        )

    def _extract_source(self, content: dict[str, Any]) -> ParsedSource:
        """
        Extract and transform source section from ArgoCD Application.

        Transforms field names:
        - targetRevision → revision
        - path → manifest_path

        Args:
            content: Parsed YAML content as a dictionary.

        Returns:
            ParsedSource with transformed field names.
        """
        source = content["spec"]["source"]
        repo_url = source["repoURL"]
        revision = source["targetRevision"]
        manifest_path = source["path"]

        # Extract directory config if present
        directory = None
        if "directory" in source:
            # Even if directory is empty dict, create ParsedSourceDirectory
            # with default recurse=False
            recurse = False
            if source["directory"] and isinstance(source["directory"], dict):
                recurse = source["directory"].get("recurse", False)
            directory = ParsedSourceDirectory(recurse=recurse)

        return ParsedSource(
            repo_url=repo_url,
            revision=revision,
            manifest_path=manifest_path,
            directory=directory,
        )

    def _extract_destination(self, content: dict[str, Any]) -> ParsedDestination:
        """
        Extract destination section from ArgoCD Application.

        Args:
            content: Parsed YAML content as a dictionary.

        Returns:
            ParsedDestination with server/name and namespace.
        """
        destination = content["spec"]["destination"]
        server = destination.get("server")
        name = destination.get("name")
        namespace = destination["namespace"]

        return ParsedDestination(
            server=server,
            name=name,
            namespace=namespace,
        )

    def _extract_sync_policy(self, content: dict[str, Any]) -> bool:
        """
        Extract and transform syncPolicy to boolean.

        Converts the presence of a syncPolicy object to a boolean value.
        Returns True if syncPolicy is defined, False otherwise.

        Args:
            content: Parsed YAML content as a dictionary.

        Returns:
            True if syncPolicy is defined, False otherwise.
        """
        spec = content["spec"]
        return "syncPolicy" in spec and spec["syncPolicy"] is not None
