"""响应工具生成器"""
from pathlib import Path
from core.utils import FileOperations


class ResponseGenerator:
    """响应工具生成器"""
    
    def __init__(self, project_path: Path):
        """初始化响应工具生成器
        
        Args:
            project_path: 项目根目录路径
        """
        self.project_path = Path(project_path)
        self.file_ops = FileOperations(base_path=project_path)
    
    def generate(self) -> None:
        """生成响应工具文件"""
        self._create_response_file()
    
    def _create_response_file(self) -> None:
        """创建响应工具文件"""
        imports = [
            "from typing import Any, Optional, Dict, List, Union",
            "from datetime import datetime",
            "from enum import Enum",
        ]
        
        content = '''class ResponseCode(Enum):
    """响应状态码枚举"""
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    VALIDATION_ERROR = 422
    INTERNAL_ERROR = 500


class ResponseModel:
    """统一响应模型"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "操作成功",
        code: int = ResponseCode.SUCCESS.value
    ) -> Dict[str, Any]:
        """
        成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            code: 状态码
            
        Returns:
            标准响应字典
        """
        return {
            "code": code,
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def error(
        message: str = "操作失败",
        code: int = ResponseCode.BAD_REQUEST.value,
        errors: Optional[Union[List, Dict]] = None
    ) -> Dict[str, Any]:
        """
        错误响应
        
        Args:
            message: 错误消息
            code: 状态码
            errors: 详细错误信息
            
        Returns:
            标准响应字典
        """
        response = {
            "code": code,
            "success": False,
            "message": message,
            "data": None,
            "timestamp": datetime.now().isoformat()
        }
        
        if errors:
            response["errors"] = errors
            
        return response
    
    @staticmethod
    def paginated(
        items: List[Any],
        total: int,
        page: int = 1,
        page_size: int = 10,
        message: str = "查询成功"
    ) -> Dict[str, Any]:
        """
        分页响应
        
        Args:
            items: 数据列表
            total: 总数
            page: 当前页码
            page_size: 每页大小
            message: 响应消息
            
        Returns:
            标准分页响应字典
        """
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "code": ResponseCode.SUCCESS.value,
            "success": True,
            "message": message,
            "data": {
                "items": items,
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "创建成功"
    ) -> Dict[str, Any]:
        """创建成功响应"""
        return ResponseModel.success(
            data=data,
            message=message,
            code=ResponseCode.CREATED.value
        )
    
    @staticmethod
    def not_found(
        message: str = "资源不存在"
    ) -> Dict[str, Any]:
        """资源不存在响应"""
        return ResponseModel.error(
            message=message,
            code=ResponseCode.NOT_FOUND.value
        )
    
    @staticmethod
    def unauthorized(
        message: str = "未授权访问"
    ) -> Dict[str, Any]:
        """未授权响应"""
        return ResponseModel.error(
            message=message,
            code=ResponseCode.UNAUTHORIZED.value
        )
    
    @staticmethod
    def forbidden(
        message: str = "禁止访问"
    ) -> Dict[str, Any]:
        """禁止访问响应"""
        return ResponseModel.error(
            message=message,
            code=ResponseCode.FORBIDDEN.value
        )
    
    @staticmethod
    def validation_error(
        message: str = "数据验证失败",
        errors: Optional[Union[List, Dict]] = None
    ) -> Dict[str, Any]:
        """验证错误响应"""
        return ResponseModel.error(
            message=message,
            code=ResponseCode.VALIDATION_ERROR.value,
            errors=errors
        )
    
    @staticmethod
    def internal_error(
        message: str = "服务器内部错误"
    ) -> Dict[str, Any]:
        """服务器错误响应"""
        return ResponseModel.error(
            message=message,
            code=ResponseCode.INTERNAL_ERROR.value
        )


# 便捷别名
Response = ResponseModel
'''
        
        self.file_ops.create_python_file(
            file_path="app/utils/response.py",
            docstring="统一响应格式工具",
            imports=imports,
            content=content,
            overwrite=True
        )
