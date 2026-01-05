"""File generation utility class"""
from pathlib import Path
from typing import Optional, List, Union


class FileOperations:
    """File generation and operation utility class"""

    def __init__(self, base_path: Optional[Path] = None):
        """
        InitializeFile generator

        Args:
            base_path: Base path, all relative paths are based on this path
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()

    def create_file(
        self,
        file_path: Union[str, Path],
        content: str = "",
        encoding: str = "utf-8",
        overwrite: bool = False
    ) -> Path:
        """
        Create file

        Args:
            file_path: File path(relative tobase_pathor absolute path)
            content: File content
            encoding: File encoding
            overwrite: Whether to overwrite existing files

        Returns:
            CreateFile path

        Raises:
            FileExistsError: File already existsandoverwrite=False
        """
        full_path = self._resolve_path(file_path)

        if full_path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {full_path}")

        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        full_path.write_text(content, encoding=encoding)
        return full_path

    def append_content(
        self,
        file_path: Union[str, Path],
        content: str,
        encoding: str = "utf-8",
        newline: bool = True
    ) -> Path:
        """
        Append content to end of file

        Args:
            file_path: File path
            content: AppendContent
            encoding: File encoding
            newline: whetherinAppendbeforeaddnewline

        Returns:
            File path

        Raises:
            FileNotFoundError: File does not exist
        """
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            raise FileNotFoundError(f"File does not exist: {full_path}")

        with open(full_path, 'a', encoding=encoding) as f:
            if newline:
                f.write('\n')
            f.write(content)

        return full_path

    def insert_content(
        self,
        file_path: Union[str, Path],
        content: str,
        position: int = 0,
        encoding: str = "utf-8"
    ) -> Path:
        """
        infilespecified positionInsertContent

        Args:
            file_path: File path
            content: InsertContent
            position: Insert position(Line number，0indicates beginning of file)
            encoding: File encoding

        Returns:
            File path

        Raises:
            FileNotFoundError: File does not exist
        """
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            raise FileNotFoundError(f"File does not exist: {full_path}")

        # Read existing content
        lines = full_path.read_text(encoding=encoding).splitlines(keepends=True)

        # InsertNew content
        if position < 0:
            position = len(lines) + position + 1

        position = max(0, min(position, len(lines)))
        lines.insert(position, content if content.endswith('\n') else content + '\n')

        # Write back to file
        full_path.write_text(''.join(lines), encoding=encoding)
        return full_path

    def insert_after_pattern(
        self,
        file_path: Union[str, Path],
        pattern: str,
        content: str,
        encoding: str = "utf-8",
        first_match: bool = True
    ) -> Path:
        """
        inmatchschemarowafterInsertContent

        Args:
            file_path: File path
            pattern: String to match
            content: InsertContent
            encoding: File encoding
            first_match: Whether to match only the first occurrence(Falsematch all)

        Returns:
            File path

        Raises:
            FileNotFoundError: File does not exist
            ValueError: Pattern not found
        """
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            raise FileNotFoundError(f"File does not exist: {full_path}")

        lines = full_path.read_text(encoding=encoding).splitlines(keepends=True)
        new_lines = []
        found = False

        for line in lines:
            new_lines.append(line)
            if pattern in line:
                found = True
                new_lines.append(content if content.endswith('\n') else content + '\n')
                if first_match:
                    new_lines.extend(lines[len(new_lines):])
                    break

        if not found:
            raise ValueError(f"Pattern not found: {pattern}")

        full_path.write_text(''.join(new_lines), encoding=encoding)
        return full_path

    def insert_before_pattern(
        self,
        file_path: Union[str, Path],
        pattern: str,
        content: str,
        encoding: str = "utf-8",
        first_match: bool = True
    ) -> Path:
        """
        inmatchschemarowbeforeInsertContent

        Args:
            file_path: File path
            pattern: String to match
            content: InsertContent
            encoding: File encoding
            first_match: Whether to match only the first occurrence(Falsematch all)

        Returns:
            File path

        Raises:
            FileNotFoundError: File does not exist
            ValueError: Pattern not found
        """
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            raise FileNotFoundError(f"File does not exist: {full_path}")

        lines = full_path.read_text(encoding=encoding).splitlines(keepends=True)
        new_lines = []
        found = False

        for line in lines:
            if pattern in line:
                found = True
                new_lines.append(content if content.endswith('\n') else content + '\n')
                new_lines.append(line)
                if first_match:
                    new_lines.extend(lines[len(new_lines) - 1:])
                    break
            else:
                new_lines.append(line)

        if not found:
            raise ValueError(f"Pattern not found: {pattern}")

        full_path.write_text(''.join(new_lines), encoding=encoding)
        return full_path

    def replace_content(
        self,
        file_path: Union[str, Path],
        old_content: str,
        new_content: str,
        encoding: str = "utf-8",
        count: int = -1
    ) -> Path:
        """
        ReplacefilemediumContent

        Args:
            file_path: File path
            old_content: ReplaceContent
            new_content: New content
            encoding: File encoding
            count: Replacement count(-1 means replace all)

        Returns:
            File path

        Raises:
            FileNotFoundError: File does not exist
        """
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            raise FileNotFoundError(f"File does not exist: {full_path}")

        content = full_path.read_text(encoding=encoding)
        new_text = content.replace(old_content, new_content, count)
        full_path.write_text(new_text, encoding=encoding)
        return full_path

    def create_python_file(
        self,
        file_path: Union[str, Path],
        docstring: Optional[str] = None,
        imports: Optional[List[str]] = None,
        content: str = "",
        overwrite: bool = False
    ) -> Path:
        """
        CreatePythonfile

        Args:
            file_path: File path
            docstring: File docstring
            imports: List of import statements
            content: File content
            overwrite: Whether to overwrite existing files

        Returns:
            CreateFile path
        """
        parts = []

        if docstring:
            parts.append(f'"""{docstring}"""')

        if imports:
            parts.append('\n'.join(imports))

        if content:
            parts.append(content)

        full_content = '\n\n'.join(parts) + '\n'
        return self.create_file(file_path, full_content, overwrite=overwrite)

    def create_json_file(
        self,
        file_path: Union[str, Path],
        data: dict,
        indent: int = 2,
        overwrite: bool = False
    ) -> Path:
        """
        CreateJSONfile

        Args:
            file_path: File path
            data: JSON data
            indent: Number of spaces for indentation
            overwrite: Whether to overwrite existing files

        Returns:
            CreateFile path
        """
        import json
        content = json.dumps(data, indent=indent, ensure_ascii=False)
        return self.create_file(file_path, content, overwrite=overwrite)

    def create_yaml_file(
        self,
        file_path: Union[str, Path],
        data: dict,
        overwrite: bool = False
    ) -> Path:
        """
        CreateYAMLfile

        Args:
            file_path: File path
            data: YAML data
            overwrite: Whether to overwrite existing files

        Returns:
            CreateFile path
        """
        try:
            import yaml
            content = yaml.dump(data, allow_unicode=True, default_flow_style=False)
            return self.create_file(file_path, content, overwrite=overwrite)
        except ImportError:
            raise ImportError("PyYAML required: pip install pyyaml")

    def create_markdown_file(
        self,
        file_path: Union[str, Path],
        title: Optional[str] = None,
        content: str = "",
        overwrite: bool = False
    ) -> Path:
        """
        CreateMarkdownfile

        Args:
            file_path: File path
            title: Title
            content: Content
            overwrite: Whether to overwrite existing files

        Returns:
            CreateFile path
        """
        parts = []

        if title:
            parts.append(f"# {title}")

        if content:
            parts.append(content)

        full_content = '\n\n'.join(parts) + '\n'
        return self.create_file(file_path, full_content, overwrite=overwrite)

    def _resolve_path(self, file_path: Union[str, Path]) -> Path:
        """
        parseFile path

        Args:
            file_path: File path

        Returns:
            completeFile path
        """
        path = Path(file_path)
        if path.is_absolute():
            return path
        return self.base_path / path
