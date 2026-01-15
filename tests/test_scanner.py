"""Tests for Scanner module."""

from pathlib import Path

from argocd_app_migrator.scanner import Scanner, ScannerError


class TestScannerBasics:
    """Test basic Scanner functionality."""

    def test_scanner_initialization(self, scanner: Scanner) -> None:
        """Test that Scanner can be initialized."""
        assert scanner is not None
        assert isinstance(scanner, Scanner)

    def test_scan_empty_directory(self, scanner: Scanner, empty_dir: Path) -> None:
        """Test scanning an empty directory returns empty list."""
        result = scanner.scan(empty_dir, recursive=False)

        assert result == []
        assert isinstance(result, list)

    def test_scan_directory_with_no_yaml_files(
        self, scanner: Scanner, tmp_path: Path
    ) -> None:
        """Test scanning directory with only non-YAML files."""
        test_dir = tmp_path / "no_yaml"
        test_dir.mkdir()
        (test_dir / "readme.txt").write_text("text file")
        (test_dir / "config.json").write_text('{"key": "value"}')

        result = scanner.scan(test_dir, recursive=False)

        assert result == []

    def test_scan_returns_list_of_paths(
        self, scanner: Scanner, yaml_files_dir: Path
    ) -> None:
        """Test that scan returns a list of Path objects."""
        result = scanner.scan(yaml_files_dir, recursive=False)

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(path, Path) for path in result)


class TestYamlFileDetection:
    """Test YAML file detection functionality."""

    def test_scan_finds_yaml_extension(self, scanner: Scanner, tmp_path: Path) -> None:
        """Test that .yaml files are found."""
        test_dir = tmp_path / "yaml_only"
        test_dir.mkdir()
        (test_dir / "app.yaml").write_text("content")

        result = scanner.scan(test_dir, recursive=False)

        assert len(result) == 1
        assert result[0].name == "app.yaml"

    def test_scan_finds_yml_extension(self, scanner: Scanner, tmp_path: Path) -> None:
        """Test that .yml files are found."""
        test_dir = tmp_path / "yml_only"
        test_dir.mkdir()
        (test_dir / "config.yml").write_text("content")

        result = scanner.scan(test_dir, recursive=False)

        assert len(result) == 1
        assert result[0].name == "config.yml"

    def test_scan_finds_both_extensions(
        self, scanner: Scanner, yaml_files_dir: Path
    ) -> None:
        """Test that both .yaml and .yml files are found."""
        result = scanner.scan(yaml_files_dir, recursive=False)

        # yaml_files_dir has 2 .yaml and 1 .yml file
        assert len(result) == 3
        extensions = [path.suffix for path in result]
        assert ".yaml" in extensions
        assert ".yml" in extensions

    def test_scan_ignores_non_yaml_files(
        self, scanner: Scanner, mixed_files_dir: Path
    ) -> None:
        """Test that non-YAML files are ignored."""
        result = scanner.scan(mixed_files_dir, recursive=False)

        # mixed_files_dir has 2 YAML files and 3 non-YAML files
        assert len(result) == 2
        assert all(path.suffix in [".yaml", ".yml"] for path in result)

    def test_scan_only_returns_files_not_directories(
        self, scanner: Scanner, tmp_path: Path
    ) -> None:
        """Test that directories matching *.yaml are not included."""
        test_dir = tmp_path / "dir_test"
        test_dir.mkdir()

        # Create a directory with .yaml in name
        yaml_dir = test_dir / "config.yaml"
        yaml_dir.mkdir()

        # Create an actual YAML file
        (test_dir / "app.yaml").write_text("content")

        result = scanner.scan(test_dir, recursive=False)

        # Should only find the file, not the directory
        assert len(result) == 1
        assert result[0].is_file()
        assert result[0].name == "app.yaml"


class TestRecursiveScanning:
    """Test recursive scanning functionality."""

    def test_non_recursive_finds_root_only(
        self, scanner: Scanner, nested_input_dir: Path
    ) -> None:
        """Test that non-recursive scan only finds root-level files."""
        result = scanner.scan(nested_input_dir, recursive=False)

        # nested_input_dir has 1 file at root
        assert len(result) == 1
        assert result[0].parent == nested_input_dir

    def test_non_recursive_ignores_subdirectories(
        self, scanner: Scanner, tmp_path: Path
    ) -> None:
        """Test that non-recursive scan ignores subdirectories."""
        test_dir = tmp_path / "ignore_sub"
        test_dir.mkdir()
        subdir = test_dir / "subdir"
        subdir.mkdir()

        # Create files at both levels
        (test_dir / "root.yaml").write_text("root")
        (subdir / "sub.yaml").write_text("sub")

        result = scanner.scan(test_dir, recursive=False)

        assert len(result) == 1
        assert result[0].name == "root.yaml"

    def test_recursive_finds_all_levels(
        self, scanner: Scanner, nested_input_dir: Path
    ) -> None:
        """Test that recursive scan finds files at all levels."""
        result = scanner.scan(nested_input_dir, recursive=True)

        # nested_input_dir has 3 files total (root, level1, level2)
        assert len(result) == 3

    def test_recursive_with_nested_structure(
        self, scanner: Scanner, tmp_path: Path
    ) -> None:
        """Test recursive scan with complex nested structure."""
        test_dir = tmp_path / "deep"
        test_dir.mkdir()

        # Create deeply nested structure
        (test_dir / "a.yaml").write_text("a")
        level1 = test_dir / "level1"
        level1.mkdir()
        (level1 / "b.yaml").write_text("b")
        level2 = level1 / "level2"
        level2.mkdir()
        (level2 / "c.yml").write_text("c")
        level3 = level2 / "level3"
        level3.mkdir()
        (level3 / "d.yaml").write_text("d")

        result = scanner.scan(test_dir, recursive=True)

        assert len(result) == 4
        names = [path.name for path in result]
        assert "a.yaml" in names
        assert "b.yaml" in names
        assert "c.yml" in names
        assert "d.yaml" in names


class TestPathHandling:
    """Test path handling and normalization."""

    def test_returns_absolute_paths(
        self, scanner: Scanner, yaml_files_dir: Path
    ) -> None:
        """Test that returned paths are absolute."""
        result = scanner.scan(yaml_files_dir, recursive=False)

        assert all(path.is_absolute() for path in result)

    def test_paths_are_resolved(self, scanner: Scanner, tmp_path: Path) -> None:
        """Test that paths are fully resolved."""
        test_dir = tmp_path / "resolve_test"
        test_dir.mkdir()
        (test_dir / "app.yaml").write_text("content")

        result = scanner.scan(test_dir, recursive=False)

        # Resolved paths should not contain .. or symlink components
        assert len(result) == 1
        assert ".." not in str(result[0])
        assert result[0] == result[0].resolve()

    def test_paths_are_sorted_alphabetically(
        self, scanner: Scanner, tmp_path: Path
    ) -> None:
        """Test that results are sorted alphabetically."""
        test_dir = tmp_path / "sort_test"
        test_dir.mkdir()

        # Create files in non-alphabetical order
        (test_dir / "zebra.yaml").write_text("z")
        (test_dir / "alpha.yaml").write_text("a")
        (test_dir / "beta.yml").write_text("b")
        (test_dir / "gamma.yaml").write_text("g")

        result = scanner.scan(test_dir, recursive=False)

        names = [path.name for path in result]
        assert names == sorted(names)
        assert names == ["alpha.yaml", "beta.yml", "gamma.yaml", "zebra.yaml"]


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_scanner_error_contains_context(self, scanner: Scanner) -> None:
        """Test that ScannerError messages contain helpful context."""
        # ScannerError should be raisable with context
        try:
            raise ScannerError("Test error message")
        except ScannerError as e:
            assert "Test error message" in str(e)
