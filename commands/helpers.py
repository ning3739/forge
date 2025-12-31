"""PyPI统计信息获取器"""
import requests


class PyPIStats:
    """PyPI统计信息获取器"""

    BASE_URL = "https://pypistats.org/api/packages"
    USER_AGENT = "Forge-CLI/0.1.0"
    DEFAULT_TIMEOUT = 5

    def __init__(self, package_name: str = "forge", timeout: int = DEFAULT_TIMEOUT):
        """
        初始化PyPI统计信息获取器

        Args:
            package_name: 包名
            timeout: 请求超时时间（秒）
        """
        self.package_name = package_name
        self.timeout = timeout

    def get_downloads(self) -> str:
        """
        获取PyPI下载量

        Returns:
            格式化的下载量字符串 (e.g. "22.3k", "1.5M", "N/A")
        """
        try:
            url = f"{self.BASE_URL}/{self.package_name}/overall"
            response = requests.get(
                url,
                headers={'User-Agent': self.USER_AGENT},
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                total = self._calculate_total_downloads(data)
                return self._format_downloads(total)
        except (requests.RequestException, KeyError, ValueError):
            pass
        return "N/A"

    @staticmethod
    def _calculate_total_downloads(data: dict) -> int:
        """计算总下载量"""
        total = 0
        for item in data.get('data', []):
            if item.get('category') == 'with_mirrors':
                total += item.get('downloads', 0)
        return total

    @staticmethod
    def _format_downloads(downloads: int) -> str:
        """格式化下载量数字"""
        if downloads >= 1_000_000:
            return f"{downloads / 1_000_000:.1f}M"
        elif downloads >= 1_000:
            return f"{downloads / 1_000:.1f}k"
        return str(downloads)
