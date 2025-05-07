"""Core utilities for MEDS pipelines built with these tools."""

from dataclasses import dataclass
from pathlib import Path

SPACE = "    "
BRANCH = "│   "
TEE = "├── "
LAST = "└── "


@dataclass
class PrintConfig:
    """Configuration for printing directory contents.

    Attributes:
        space: The string used for spaces in the tree.
        branch: The string used for branches in the tree.
        tee: The string used for tee nodes in the tree.
        last: The string used for the last node in the tree.
    """

    space: str = SPACE
    branch: str = BRANCH
    tee: str = TEE
    last: str = LAST


def print_directory(path: Path | str, config: PrintConfig | None = None, **kwargs):
    """Prints the contents of a directory in string form. Returns `None`.

    Args:
        path: The path to the directory to print.

    Examples:
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     path = Path(tmpdir)
        ...     (path / "file1.txt").touch()
        ...     (path / "foo").mkdir()
        ...     (path / "bar").mkdir()
        ...     (path / "bar" / "baz.csv").touch()
        ...     print_directory(path)
        ├── bar
        │   └── baz.csv
        ├── file1.txt
        └── foo
    """

    print("\n".join(list_directory(Path(path), config=config)), **kwargs)


def list_directory(
    path: Path,
    prefix: str | None = None,
    config: PrintConfig | None = None,
) -> list[str]:
    """Returns a set of lines representing the contents of a directory, formatted for pretty printing.

    Args:
        path: The path to the directory to list.
        prefix: Used for the recursive prefixing of subdirectories. Defaults to None.

    Returns:
        A list of strings representing the contents of the directory. To be printed with newlines separating
        them.

    Raises:
        ValueError: If the path is not a directory.

    Examples:
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     path = Path(tmpdir)
        ...     (path / "file1.txt").touch()
        ...     (path / "foo").mkdir()
        ...     (path / "bar").mkdir()
        ...     (path / "bar" / "baz.csv").touch()
        ...     for l in list_directory(path):
        ...         print(l)  # This is just used as newlines break doctests
        ├── bar
        │   └── baz.csv
        ├── file1.txt
        └── foo

    Errors are raised when the path is not a path:

        >>> list_directory("foo")
        Traceback (most recent call last):
            ...
        ValueError: Expected a Path object, got <class 'str'>: foo

    Or when the path does not exist:

        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     path = Path(tmpdir)
        ...     list_directory(path / "foo")
        Traceback (most recent call last):
            ...
        ValueError: Path /tmp/tmp.../foo does not exist.

    Or when the path is not a directory:

        >>> with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
        ...     path = Path(tmp.name)
        ...     list_directory(path)
        Traceback (most recent call last):
            ...
        ValueError: Path /tmp/tmp....txt is not a directory.
    """

    if not isinstance(path, Path):
        raise ValueError(f"Expected a Path object, got {type(path)}: {path}")

    if not path.exists():
        raise ValueError(f"Path {path} does not exist.")

    if not path.is_dir():
        raise ValueError(f"Path {path} is not a directory.")

    if config is None:
        config = PrintConfig()

    if prefix is None:
        prefix = ""

    lines = []

    children = sorted(path.iterdir())

    for i, child in enumerate(children):
        is_last = i == len(children) - 1

        node_prefix = config.last if is_last else config.tee
        subdir_prefix = config.space if is_last else config.branch

        if child.is_file():
            lines.append(f"{prefix}{node_prefix}{child.name}")
        elif child.is_dir():
            lines.append(f"{prefix}{node_prefix}{child.name}")
            lines.extend(list_directory(child, prefix=prefix + subdir_prefix, config=config))
    return lines
