"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest
from typer.testing import CliRunner


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
