"""Tests for Parser module."""

from pathlib import Path

from argocd_app_migrator.parser import (
    ParsedApplication,
    ParsedDestination,
    ParsedMetadata,
    ParsedSource,
    ParsedSourceDirectory,
    ParseResult,
    Parser,
)


class TestParserBasics:
    """Test basic Parser functionality."""

    def test_parser_initialization(self, parser: Parser) -> None:
        """Test that Parser can be initialized."""
        assert parser is not None
        assert isinstance(parser, Parser)

    def test_parse_returns_parse_result(
        self, parser: Parser, valid_app_yaml: Path
    ) -> None:
        """Test that parse returns a ParseResult object."""
        result = parser.parse(valid_app_yaml)

        assert isinstance(result, ParseResult)
        assert isinstance(result.success, bool)
        assert isinstance(result.file_path, Path)

    def test_parse_batch_returns_list_of_results(
        self, parser: Parser, valid_app_yaml: Path, minimal_app_yaml: Path
    ) -> None:
        """Test that parse_batch returns a list of ParseResult objects."""
        results = parser.parse_batch([valid_app_yaml, minimal_app_yaml])

        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(r, ParseResult) for r in results)


class TestValidApplicationParsing:
    """Test parsing of valid ArgoCD Applications."""

    def test_parse_minimal_valid_application(
        self, parser: Parser, minimal_app_yaml: Path
    ) -> None:
        """Test parsing a minimal valid Application."""
        result = parser.parse(minimal_app_yaml)

        assert result.success is True
        assert result.data is not None
        assert result.error_message is None
        assert isinstance(result.data, ParsedApplication)

    def test_parse_application_with_all_fields(
        self, parser: Parser, valid_app_yaml: Path
    ) -> None:
        """Test parsing an Application with all fields."""
        result = parser.parse(valid_app_yaml)

        assert result.success is True
        assert result.data is not None
        assert result.data.metadata.name == "test-app"
        assert result.data.project == "default"
        assert result.data.source.repo_url == "https://github.com/example/repo.git"
        assert result.data.destination.namespace == "default"

    def test_parse_extracts_correct_metadata(
        self, parser: Parser, valid_app_yaml: Path
    ) -> None:
        """Test that metadata is extracted correctly."""
        result = parser.parse(valid_app_yaml)

        assert result.success is True
        assert result.data is not None
        metadata = result.data.metadata
        assert isinstance(metadata, ParsedMetadata)
        assert metadata.name == "test-app"
        assert "argocd.argoproj.io/sync-wave" in metadata.annotations
        assert metadata.annotations["argocd.argoproj.io/sync-wave"] == "40"
        assert "environment" in metadata.labels
        assert metadata.labels["environment"] == "dev"

    def test_parse_extracts_correct_source(
        self, parser: Parser, valid_app_yaml: Path
    ) -> None:
        """Test that source is extracted and transformed correctly."""
        result = parser.parse(valid_app_yaml)

        assert result.success is True
        assert result.data is not None
        source = result.data.source
        assert isinstance(source, ParsedSource)
        assert source.repo_url == "https://github.com/example/repo.git"
        assert source.revision == "main"
        assert source.manifest_path == "./manifests"
        assert source.directory is not None
        assert isinstance(source.directory, ParsedSourceDirectory)
        assert source.directory.recurse is True

    def test_parse_extracts_correct_destination(
        self, parser: Parser, valid_app_yaml: Path
    ) -> None:
        """Test that destination is extracted correctly."""
        result = parser.parse(valid_app_yaml)

        assert result.success is True
        assert result.data is not None
        destination = result.data.destination
        assert isinstance(destination, ParsedDestination)
        assert destination.server == "https://kubernetes.default.svc"
        assert destination.namespace == "default"


class TestFieldTransformations:
    """Test field name transformations."""

    def test_targetRevision_renamed_to_revision(
        self, parser: Parser, valid_app_yaml: Path
    ) -> None:
        """Test that targetRevision is renamed to revision."""
        result = parser.parse(valid_app_yaml)

        assert result.success is True
        assert result.data is not None
        assert hasattr(result.data.source, "revision")
        assert result.data.source.revision == "main"

    def test_source_path_renamed_to_manifest_path(
        self, parser: Parser, valid_app_yaml: Path
    ) -> None:
        """Test that path is renamed to manifest_path."""
        result = parser.parse(valid_app_yaml)

        assert result.success is True
        assert result.data is not None
        assert hasattr(result.data.source, "manifest_path")
        assert result.data.source.manifest_path == "./manifests"

    def test_syncPolicy_converted_to_boolean_true(
        self, parser: Parser, valid_app_yaml: Path
    ) -> None:
        """Test that syncPolicy presence is converted to True."""
        result = parser.parse(valid_app_yaml)

        assert result.success is True
        assert result.data is not None
        assert result.data.enable_sync_policy is True

    def test_syncPolicy_missing_converts_to_false(
        self, parser: Parser, minimal_app_yaml: Path
    ) -> None:
        """Test that missing syncPolicy is converted to False."""
        result = parser.parse(minimal_app_yaml)

        assert result.success is True
        assert result.data is not None
        assert result.data.enable_sync_policy is False

    def test_sync_wave_annotation_extracted(
        self, parser: Parser, valid_app_yaml: Path
    ) -> None:
        """Test that sync-wave annotation is extracted."""
        result = parser.parse(valid_app_yaml)

        assert result.success is True
        assert result.data is not None
        assert "argocd.argoproj.io/sync-wave" in result.data.metadata.annotations
        assert result.data.metadata.annotations["argocd.argoproj.io/sync-wave"] == "40"


class TestOptionalFields:
    """Test handling of optional fields."""

    def test_parse_without_annotations(self, parser: Parser, tmp_path: Path) -> None:
        """Test parsing Application without annotations."""
        yaml_file = tmp_path / "no_annotations.yaml"
        yaml_file.write_text(
            """apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: no-annotations-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/repo.git
    targetRevision: main
    path: ./manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: default
"""
        )

        result = parser.parse(yaml_file)

        assert result.success is True
        assert result.data is not None
        assert result.data.metadata.annotations == {}

    def test_parse_without_labels(self, parser: Parser, tmp_path: Path) -> None:
        """Test parsing Application without labels."""
        yaml_file = tmp_path / "no_labels.yaml"
        yaml_file.write_text(
            """apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: no-labels-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/repo.git
    targetRevision: main
    path: ./manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: default
"""
        )

        result = parser.parse(yaml_file)

        assert result.success is True
        assert result.data is not None
        assert result.data.metadata.labels == {}

    def test_parse_without_directory_config(
        self, parser: Parser, minimal_app_yaml: Path
    ) -> None:
        """Test parsing Application without directory config."""
        result = parser.parse(minimal_app_yaml)

        assert result.success is True
        assert result.data is not None
        assert result.data.source.directory is None

    def test_parse_without_syncPolicy(
        self, parser: Parser, minimal_app_yaml: Path
    ) -> None:
        """Test parsing Application without syncPolicy."""
        result = parser.parse(minimal_app_yaml)

        assert result.success is True
        assert result.data is not None
        assert result.data.enable_sync_policy is False

    def test_directory_recurse_defaults_to_false(
        self, parser: Parser, tmp_path: Path
    ) -> None:
        """Test that directory.recurse defaults to False if not specified."""
        yaml_file = tmp_path / "dir_no_recurse.yaml"
        yaml_file.write_text(
            """apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: dir-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/repo.git
    targetRevision: main
    path: ./manifests
    directory: {}
  destination:
    server: https://kubernetes.default.svc
    namespace: default
"""
        )

        result = parser.parse(yaml_file)

        assert result.success is True
        assert result.data is not None
        assert result.data.source.directory is not None
        assert result.data.source.directory.recurse is False


class TestInvalidApplications:
    """Test handling of invalid Applications."""

    def test_parse_missing_apiVersion(self, parser: Parser, tmp_path: Path) -> None:
        """Test parsing YAML without apiVersion."""
        yaml_file = tmp_path / "no_apiVersion.yaml"
        yaml_file.write_text(
            """kind: Application
metadata:
  name: test-app
spec:
  project: default
"""
        )

        result = parser.parse(yaml_file)

        assert result.success is False
        assert result.data is None
        assert result.error_message is not None
        assert "apiVersion" in result.error_message

    def test_parse_wrong_kind(self, parser: Parser, invalid_kind_yaml: Path) -> None:
        """Test parsing YAML with wrong kind."""
        result = parser.parse(invalid_kind_yaml)

        assert result.success is False
        assert result.data is None
        assert result.error_message is not None
        assert "kind" in result.error_message or "Application" in result.error_message

    def test_parse_missing_metadata_name(self, parser: Parser, tmp_path: Path) -> None:
        """Test parsing YAML without metadata.name."""
        yaml_file = tmp_path / "no_name.yaml"
        yaml_file.write_text(
            """apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  namespace: argocd
spec:
  project: default
"""
        )

        result = parser.parse(yaml_file)

        assert result.success is False
        assert result.data is None
        assert result.error_message is not None
        assert "metadata.name" in result.error_message

    def test_parse_missing_spec_project(self, parser: Parser, tmp_path: Path) -> None:
        """Test parsing YAML without spec.project."""
        yaml_file = tmp_path / "no_project.yaml"
        yaml_file.write_text(
            """apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: test-app
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/example/repo.git
    targetRevision: main
    path: ./manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: default
"""
        )

        result = parser.parse(yaml_file)

        assert result.success is False
        assert result.data is None
        assert result.error_message is not None
        assert "spec.project" in result.error_message

    def test_parse_missing_source_repoURL(self, parser: Parser, tmp_path: Path) -> None:
        """Test parsing YAML without spec.source.repoURL."""
        yaml_file = tmp_path / "no_repoURL.yaml"
        yaml_file.write_text(
            """apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: test-app
  namespace: argocd
spec:
  project: default
  source:
    targetRevision: main
    path: ./manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: default
"""
        )

        result = parser.parse(yaml_file)

        assert result.success is False
        assert result.data is None
        assert result.error_message is not None
        assert "repoURL" in result.error_message

    def test_parse_missing_destination(self, parser: Parser, tmp_path: Path) -> None:
        """Test parsing YAML without spec.destination."""
        yaml_file = tmp_path / "no_destination.yaml"
        yaml_file.write_text(
            """apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: test-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/repo.git
    targetRevision: main
    path: ./manifests
"""
        )

        result = parser.parse(yaml_file)

        assert result.success is False
        assert result.data is None
        assert result.error_message is not None
        assert "destination" in result.error_message

    def test_parse_invalid_yaml_syntax(self, parser: Parser, tmp_path: Path) -> None:
        """Test parsing file with invalid YAML syntax."""
        yaml_file = tmp_path / "invalid_syntax.yaml"
        yaml_file.write_text(
            """apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: test-app
  namespace: argocd
  [invalid syntax here]
"""
        )

        result = parser.parse(yaml_file)

        assert result.success is False
        assert result.data is None
        assert result.error_message is not None

    def test_parse_non_existent_file(self, parser: Parser, tmp_path: Path) -> None:
        """Test parsing a non-existent file."""
        yaml_file = tmp_path / "does_not_exist.yaml"

        result = parser.parse(yaml_file)

        assert result.success is False
        assert result.data is None
        assert result.error_message is not None
        assert "not found" in result.error_message.lower()


class TestBatchParsing:
    """Test batch parsing functionality."""

    def test_parse_batch_mixed_valid_invalid(
        self,
        parser: Parser,
        valid_app_yaml: Path,
        minimal_app_yaml: Path,
        invalid_kind_yaml: Path,
    ) -> None:
        """Test parsing a batch with mixed valid and invalid files."""
        results = parser.parse_batch(
            [valid_app_yaml, minimal_app_yaml, invalid_kind_yaml]
        )

        assert len(results) == 3
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        assert len(successful) == 2
        assert len(failed) == 1

    def test_parse_batch_all_valid(
        self, parser: Parser, valid_app_yaml: Path, minimal_app_yaml: Path
    ) -> None:
        """Test parsing a batch with all valid files."""
        results = parser.parse_batch([valid_app_yaml, minimal_app_yaml])

        assert len(results) == 2
        assert all(r.success for r in results)
        assert all(r.data is not None for r in results)

    def test_parse_batch_empty_list(self, parser: Parser) -> None:
        """Test parsing an empty list of files."""
        results = parser.parse_batch([])

        assert isinstance(results, list)
        assert len(results) == 0
