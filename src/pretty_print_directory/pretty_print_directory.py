import re
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

SPACE = "    "
BRANCH = "│   "
TEE = "├── "
LAST = "└── "


@dataclass
class PrintConfig:
    """Configuration for printing directory contents, both in terms of display and filtering.

    Attributes:
        space: The string used for spaces in the tree.
        branch: The string used for branches in the tree.
        tee: The string used for tee nodes in the tree.
        last: The string used for the last node in the tree.
        file_extension: The file extension to include in the tree. If not specified, all files and directories
            are included. If specified, only files matching that extension are included, and only directories
            containing (at any level of nesting) files matching that extension are included.

    Raises:
        ValueError:
          - If file_extension (if provided) is not a list of strings or a string
          - If ignore_regex (if provided) is not a string
          - If ignore_regex (if provided) is not a valid regex pattern.

    Examples:
        >>> PrintConfig()
        PrintConfig(space='    ',
                    branch='│   ',
                    tee='├── ',
                    last='└── ',
                    file_extension=None,
                    ignore_regex=None)
        >>> PrintConfig(file_extension=".txt")
        PrintConfig(space='    ',
                    branch='│   ',
                    tee='├── ',
                    last='└── ',
                    file_extension=['.txt'],
                    ignore_regex=None)
        >>> PrintConfig(file_extension=[".txt", ".csv"], ignore_regex=r"tmp")
        PrintConfig(space='    ',
                    branch='│   ',
                    tee='├── ',
                    last='└── ',
                    file_extension=['.txt', '.csv'],
                    ignore_regex='tmp')

    The `PrintConfig` can be used to filter files and directories based on their extensions and regex
    patterns.

        >>> config = PrintConfig(file_extension=[".txt", ".csv"], ignore_regex=r"baz")
        >>> config.matches(Path("file.csv"))
        True
        >>> config.matches(Path("file.txt"))
        True
        >>> config.matches(Path("baz.txt"))
        False
        >>> config.matches(Path("file.py"))
        False
        >>> config.matches(Path("foo/baz/file.csv"))
        False
        >>> config.matches(Path("foo/bar/file.txt"))
        True

    File extensions will check sub-files instead of subdirectories when you pass an extant directory
    (non-existent directories will be checked as though they were files):

        >>> config.matches(Path("foo/bar"))
        False
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     path = Path(tmpdir)
        ...     (path / "file.txt").touch()
        ...     (path / "baz").mkdir()
        ...     (path / "baz" / "file.csv").touch()
        ...     print(f"On root: {config.matches(path)}")
        ...     print(f"On baz file: {config.matches(path / 'baz' / 'file.csv')}")
        On root: True
        On baz file: False

    Note that the ignore_regex is applied separately from the file extension checker, which can lead to
    inconsistencies if a directory is valid under both, but all valid files are within an ignored
    subdirectory:

        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     path = Path(tmpdir)
        ...     (path / "file.py").touch() # No longer matches
        ...     (path / "baz").mkdir()
        ...     (path / "baz" / "file.csv").touch()
        ...     print(f"On root: {config.matches(path)}")
        ...     for f in path.rglob("*.*"):
        ...          print(f"  - File: {f.relative_to(path)} matches: {config.matches(f)}")
        On root: True
          - File: file.py matches: False
          - File: baz/file.csv matches: False


    Validitiy of the parameters is checked:

        >>> PrintConfig(file_extension=[".txt", ".csv", 3])
        Traceback (most recent call last):
            ...
        ValueError: file_extension must be a list of strings, got ['.txt', '.csv', 3]
        >>> PrintConfig(ignore_regex=123)
        Traceback (most recent call last):
            ...
        ValueError: ignore_regex must be a string, got <class 'int'>: 123
        >>> PrintConfig(ignore_regex=r"[a-z+")
        Traceback (most recent call last):
            ...
        ValueError: Invalid regex for ignore_regex: [a-z+. Error: unterminated character set at position 0
    """

    space: str = SPACE
    branch: str = BRANCH
    tee: str = TEE
    last: str = LAST
    file_extension: list[str] | None = None
    ignore_regex: str | None = None

    def __post_init__(self):
        if isinstance(self.file_extension, str):
            self.file_extension = [self.file_extension]

        if self.file_extension is not None and not (
            isinstance(self.file_extension, list) and all(isinstance(ext, str) for ext in self.file_extension)
        ):
            raise ValueError(f"file_extension must be a list of strings, got {self.file_extension}")

        if self.ignore_regex is not None and not isinstance(self.ignore_regex, str):
            raise ValueError(
                f"ignore_regex must be a string, got {type(self.ignore_regex)}: {self.ignore_regex}"
            )

        if self.ignore_regex:
            try:
                self._ignore_re  # noqa: B018
            except re.error as e:
                raise ValueError(f"Invalid regex for ignore_regex: {self.ignore_regex}. Error: {e}") from e

    @cached_property
    def _ignore_re(self) -> re.Pattern:
        return re.compile(self.ignore_regex)

    def _matches_extension(self, path: Path) -> bool:
        """Checks if the path matches the file extension specified in the config.

        If the path exists and is a directory, it checks if any files within the directory match the file
        extension. If it is a file, it will be checked based on its extensions. If it does not exist, it will
        be checked as though it were a file.

        Args:
            path: The path to check.

        Returns:
            True if the path matches the file extension, False otherwise.

        Examples:
            >>> config = PrintConfig(file_extension=".txt")
            >>> config._matches_extension(Path("file.txt"))
            True
            >>> config._matches_extension(Path("file.csv"))
            False
            >>> with tempfile.TemporaryDirectory() as tmpdir:
            ...     path = Path(tmpdir)
            ...     (path / "file.txt").touch()
            ...     (path / "file.csv").touch()
            ...     config._matches_extension(path)
            True
            >>> with tempfile.TemporaryDirectory() as tmpdir:
            ...     path = Path(tmpdir)
            ...     (path / "file.csv").touch()
            ...     config._matches_extension(path)
            False
        """

        if not self.file_extension:
            return True

        if path.is_dir():
            return any(any(path.rglob(f"*{ext}")) for ext in self.file_extension)
        else:
            return any(path.name.endswith(ext) for ext in self.file_extension)

    def _matches_ignore_regex(self, path: Path) -> bool:
        """Checks if the path matches the ignore regex specified in the config.

        Unlike the file extension checker, this always checks against the path name, even for directories, so
        that whole directories can be ignored if they match the regex.

        Args:
            path: The path to check.

        Returns:
            True if the path _should not be ignored_ according to the ignore regex (i.e., does not match the
                regex), False otherwise.

        Examples:
            >>> config = PrintConfig(ignore_regex=r"\.txt")
            >>> config._matches_ignore_regex(Path("file.txt"))
            False
            >>> config._matches_ignore_regex(Path("filetxt"))
            True
            >>> config._matches_ignore_regex(Path("file.csv"))
            True
            >>> config = PrintConfig(ignore_regex=r"foo/.*")
            >>> config._matches_ignore_regex(Path("foo/bar/baz.txt"))
            False
            >>> config._matches_ignore_regex(Path("bar/foo/baz.txt"))
            False
            >>> config._matches_ignore_regex(Path("bar/baz.txt"))
            True
        """

        if not self.ignore_regex:
            return True

        # Check if the path matches the ignore regex
        return not self._ignore_re.search(str(path))

    def matches(self, path: Path) -> bool:
        """Checks if the path matches the config specification."""

        return self._matches_extension(path) and self._matches_ignore_regex(path)


def print_directory(path: Path | str, config: PrintConfig | None = None, **kwargs):
    """Prints the contents of a directory in string form. Returns `None`.

    Args:
        path: The path to the directory to print.

    Examples:
        >>> def set_up_dir(path: Path):
        ...     (path / "file1.txt").touch()
        ...     (path / "file2.csv").touch()
        ...     (path / "foo").mkdir()
        ...     (path / "bar").mkdir()
        ...     (path / "bar" / "baz.csv").touch()

    With no controls, all files and directories are printed:

        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     set_up_dir(Path(tmpdir))
        ...     print_directory(tmpdir)
        ├── bar
        │   └── baz.csv
        ├── file1.txt
        ├── file2.csv
        └── foo

    If we limit to an extension, only files with that extension are printed, and only directories containing
    such files are included.

        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     set_up_dir(Path(tmpdir))
        ...     print_directory(tmpdir, config=PrintConfig(file_extension=".csv"))
        ├── bar
        │   └── baz.csv
        └── file2.csv
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

    valid_children = []
    for child in children:
        if config.matches(child):
            valid_children.append(child)

    for i, child in enumerate(valid_children):
        is_last = i == len(valid_children) - 1

        node_prefix = config.last if is_last else config.tee
        subdir_prefix = config.space if is_last else config.branch

        if child.is_file():
            lines.append(f"{prefix}{node_prefix}{child.name}")
        elif child.is_dir():
            lines.append(f"{prefix}{node_prefix}{child.name}")
            lines.extend(list_directory(child, prefix=prefix + subdir_prefix, config=config))

    return lines
