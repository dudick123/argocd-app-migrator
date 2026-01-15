"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from argocd_app_migrator.parser import Parser
from argocd_app_migrator.scanner import Scanner


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_input_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with sample YAML files."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    # Create a sample valid ArgoCD Application YAML
    app_yaml = input_dir / "app-1.yaml"
    app_yaml.write_text(
        """apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: example-app
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

    return input_dir


@pytest.fixture
def sample_output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def nested_input_dir(tmp_path: Path) -> Path:
    """Create a nested directory structure for recursive testing."""
    base = tmp_path / "nested"
    base.mkdir()

    # Create nested directories
    (base / "level1" / "level2").mkdir(parents=True)

    # Add YAML files at different levels
    (base / "app-root.yaml").write_text(
        "apiVersion: argoproj.io/v1alpha1\nkind: Application"
    )
    (base / "level1" / "app-l1.yaml").write_text(
        "apiVersion: argoproj.io/v1alpha1\nkind: Application"
    )
    (base / "level1" / "level2" / "app-l2.yaml").write_text(
        "apiVersion: argoproj.io/v1alpha1\nkind: Application"
    )

    return base


@pytest.fixture
def scanner() -> Scanner:
    """Provide a Scanner instance for testing."""
    return Scanner()


@pytest.fixture
def empty_dir(tmp_path: Path) -> Path:
    """Create an empty directory for testing."""
    empty = tmp_path / "empty"
    empty.mkdir()
    return empty


@pytest.fixture
def yaml_files_dir(tmp_path: Path) -> Path:
    """Create a directory with .yaml and .yml files."""
    yaml_dir = tmp_path / "yaml_files"
    yaml_dir.mkdir()

    # Create files with .yaml extension
    (yaml_dir / "app1.yaml").write_text("apiVersion: argoproj.io/v1alpha1\n")
    (yaml_dir / "app2.yaml").write_text("kind: Application\n")

    # Create files with .yml extension
    (yaml_dir / "app3.yml").write_text("metadata:\n  name: test\n")

    return yaml_dir


@pytest.fixture
def mixed_files_dir(tmp_path: Path) -> Path:
    """Create a directory with YAML and non-YAML files."""
    mixed = tmp_path / "mixed"
    mixed.mkdir()

    # YAML files
    (mixed / "config.yaml").write_text("key: value\n")
    (mixed / "app.yml").write_text("app: test\n")

    # Non-YAML files
    (mixed / "readme.txt").write_text("This is a readme\n")
    (mixed / "script.py").write_text("print('hello')\n")
    (mixed / "data.json").write_text('{"key": "value"}\n')

    return mixed


# Parser fixtures


@pytest.fixture
def parser() -> Parser:
    """Provide a Parser instance for testing."""
    return Parser()


@pytest.fixture
def valid_app_yaml(tmp_path: Path) -> Path:
    """Create a valid ArgoCD Application YAML file with all fields."""
    yaml_file = tmp_path / "valid_app.yaml"
    yaml_file.write_text("""apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: test-app
  namespace: argocd
  annotations:
    argocd.argoproj.io/sync-wave: "40"
  labels:
    environment: dev
    team: platform
spec:
  project: default
  source:
    repoURL: https://github.com/example/repo.git
    targetRevision: main
    path: ./manifests
    directory:
      recurse: true
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
""")
    return yaml_file


@pytest.fixture
def minimal_app_yaml(tmp_path: Path) -> Path:
    """Create a minimal valid ArgoCD Application (no optional fields)."""
    yaml_file = tmp_path / "minimal_app.yaml"
    yaml_file.write_text("""apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: minimal-app
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
""")
    return yaml_file


@pytest.fixture
def invalid_kind_yaml(tmp_path: Path) -> Path:
    """Create a YAML file with wrong kind (not Application)."""
    yaml_file = tmp_path / "invalid_kind.yaml"
    yaml_file.write_text("""apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: not-an-app
spec:
  project: default
""")
    return yaml_file
