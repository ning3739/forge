"""文件生成工具类"""
from pathlib import Path
from typing import Optional, List, Union


class FileOperations:
    """文件生成和操作工具类"""

    def __init__(self, base_path: Optional[Path] = None):
        """
        初始化文件生成器

        Args:
            base_path: 基础路径，所有相对路径都基于此路径
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
        创建文件

        Args:
            file_path: 文件路径（相对于base_path或绝对路径）
            content: 文件内容
            encoding: 文件编码
            overwrite: 是否覆盖已存在的文件

        Returns:
            创建的文件路径

        Raises:
            FileExistsError: 文件已存在且overwrite=False
        """
        full_path = self._resolve_path(file_path)

        if full_path.exists() and not overwrite:
            raise FileExistsError(f"文件已存在: {full_path}")

        # 确保父目录存在
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
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
        追加内容到文件末尾

        Args:
            file_path: 文件路径
            content: 要追加的内容
            encoding: 文件编码
            newline: 是否在追加前添加换行符

        Returns:
            文件路径

        Raises:
            FileNotFoundError: 文件不存在
        """
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {full_path}")

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
        在文件指定位置插入内容

        Args:
            file_path: 文件路径
            content: 要插入的内容
            position: 插入位置（行号，0表示文件开头）
            encoding: 文件编码

        Returns:
            文件路径

        Raises:
            FileNotFoundError: 文件不存在
        """
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {full_path}")

        # 读取现有内容
        lines = full_path.read_text(encoding=encoding).splitlines(keepends=True)

        # 插入新内容
        if position < 0:
            position = len(lines) + position + 1

        position = max(0, min(position, len(lines)))
        lines.insert(position, content if content.endswith('\n') else content + '\n')

        # 写回文件
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
        在匹配模式的行后插入内容

        Args:
            file_path: 文件路径
            pattern: 要匹配的字符串
            content: 要插入的内容
            encoding: 文件编码
            first_match: 是否只匹配第一个（False则匹配所有）

        Returns:
            文件路径

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 未找到匹配的模式
        """
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {full_path}")

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
            raise ValueError(f"未找到匹配的模式: {pattern}")

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
        在匹配模式的行前插入内容

        Args:
            file_path: 文件路径
            pattern: 要匹配的字符串
            content: 要插入的内容
            encoding: 文件编码
            first_match: 是否只匹配第一个（False则匹配所有）

        Returns:
            文件路径

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 未找到匹配的模式
        """
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {full_path}")

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
            raise ValueError(f"未找到匹配的模式: {pattern}")

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
        替换文件中的内容

        Args:
            file_path: 文件路径
            old_content: 要替换的内容
            new_content: 新内容
            encoding: 文件编码
            count: 替换次数（-1表示全部替换）

        Returns:
            文件路径

        Raises:
            FileNotFoundError: 文件不存在
        """
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {full_path}")

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
        创建Python文件

        Args:
            file_path: 文件路径
            docstring: 文件文档字符串
            imports: 导入语句列表
            content: 文件内容
            overwrite: 是否覆盖已存在的文件

        Returns:
            创建的文件路径
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
        创建JSON文件

        Args:
            file_path: 文件路径
            data: JSON数据
            indent: 缩进空格数
            overwrite: 是否覆盖已存在的文件

        Returns:
            创建的文件路径
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
        创建YAML文件

        Args:
            file_path: 文件路径
            data: YAML数据
            overwrite: 是否覆盖已存在的文件

        Returns:
            创建的文件路径
        """
        try:
            import yaml
            content = yaml.dump(data, allow_unicode=True, default_flow_style=False)
            return self.create_file(file_path, content, overwrite=overwrite)
        except ImportError:
            raise ImportError("需要安装 PyYAML: pip install pyyaml")

    def create_markdown_file(
        self,
        file_path: Union[str, Path],
        title: Optional[str] = None,
        content: str = "",
        overwrite: bool = False
    ) -> Path:
        """
        创建Markdown文件

        Args:
            file_path: 文件路径
            title: 标题
            content: 内容
            overwrite: 是否覆盖已存在的文件

        Returns:
            创建的文件路径
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
        解析文件路径

        Args:
            file_path: 文件路径

        Returns:
            完整的文件路径
        """
        path = Path(file_path)
        if path.is_absolute():
            return path
        return self.base_path / path
