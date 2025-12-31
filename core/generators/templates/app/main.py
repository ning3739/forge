"""Main.py 生成器"""
from pathlib import Path
from .base import BaseTemplateGenerator


class MainGenerator(BaseTemplateGenerator):
    """Main.py 文件生成器"""
    
    def generate(self) -> None:
        """生成 main.py 文件"""
        auth_type = self.config_reader.get_auth_type() if self.config_reader.has_auth() else None
        
        if auth_type:
            self._generate_main_with_auth()
        else:
            self._generate_basic_main()
    
    def _generate_basic_main(self) -> None:
        """生成基础的 main.py（无认证）"""
        imports = [
            "import os",
            "import uvicorn",
            "from fastapi import FastAPI, HTTPException, Request",
            "from fastapi.responses import JSONResponse",
            "from fastapi.openapi.utils import get_openapi",
            "from fastapi.middleware.cors import CORSMiddleware",
            "from fastapi.staticfiles import StaticFiles",
            "",
            "from app.core.config.settings import settings",
            "from app.core.logger import logger_manager",
        ]
        
        if self.config_reader.has_database():
            imports.append("from app.core.database import db_manager")
        
        content = '''# 创建 LoggerManager 实例
logger_manager.setup()

# 创建 Logger 实例
logger = logger_manager.get_logger(__name__)


# 创建生命周期
async def lifespan(_app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚩 Starting the application...")
    logger.info(f"🚧 You are working in {os.getenv('ENV', 'development')} environment")
    '''
        
        if self.config_reader.has_database():
            content += '''
    try:
        # 初始化数据库连接
        await db_manager.initialize()
        logger.info("🎉 Database connections initialized successfully")
        await db_manager.test_connections()
        logger.info("🎉 Database connections test successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.warning("⚠️ Application will start without database connections")
    '''
        
        content += '''
    yield
    '''
        
        if self.config_reader.has_database():
            content += '''
    # 关闭数据库连接
    try:
        await db_manager.close()
        logger.info("🎉 Database connections closed successfully")
    except Exception as e:
        logger.error(f"❌ Database connection closed failed: {e}")
        logger.warning("⚠️ Database connection closed failed")
    '''
        
        content += '''

# 创建 FastAPI 实例
app = FastAPI(
    lifespan=lifespan,
    title=settings.app.APP_NAME,
    version=settings.app.APP_VERSION,
    description=settings.app.APP_DESCRIPTION,
)


# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    """HTTP 异常处理器"""
    logger.error(f"HTTPException: {exc}")
    error_detail = exc.detail
    
    if isinstance(error_detail, dict):
        error_message = error_detail.get("error", str(error_detail))
    else:
        error_message = str(error_detail)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": exc.status_code, "error": error_message},
    )


@app.exception_handler(Exception)
async def general_exception_handler(_request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": 500, "error": "Internal server error"},
    )


# CORS 中间件
'''
        
        if self.config_reader.has_cors():
            content += '''allow_origins = [x.strip() for x in settings.cors.CORS_ALLOWED_ORIGINS.split(',') if x.strip()]
allow_methods = [x.strip() for x in settings.cors.CORS_ALLOW_METHODS.split(',') if x.strip()]
allow_headers = [x.strip() for x in settings.cors.CORS_ALLOW_HEADERS.split(',') if x.strip()]
allow_credentials = settings.cors.CORS_ALLOW_CREDENTIALS
expose_headers = [x.strip() for x in settings.cors.CORS_EXPOSE_HEADERS.split(',') if x.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
    allow_credentials=allow_credentials,
    expose_headers=expose_headers,
)
'''
        
        content += '''

# 静态文件
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# 健康检查端点
@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


# OpenAPI 文档
def custom_openapi():
    """自定义 OpenAPI 文档"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app.APP_NAME,
        version=settings.app.APP_VERSION,
        description=settings.app.APP_DESCRIPTION,
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# 启动应用
if __name__ == "__main__":
    if os.getenv("ENV") == "development":
        logger.info("🚩 Starting the application in development mode...")
        uvicorn.run(
            app="app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
        )
'''
        
        self.file_ops.create_python_file(
            file_path="app/main.py",
            docstring="FastAPI 应用主入口",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_main_with_auth(self) -> None:
        """生成带认证的 main.py"""
        imports = [
            "import os",
            "import uvicorn",
            "from fastapi import FastAPI, HTTPException, Request",
            "from fastapi.responses import JSONResponse",
            "from fastapi.openapi.utils import get_openapi",
            "from fastapi.middleware.cors import CORSMiddleware",
            "from fastapi.staticfiles import StaticFiles",
            "",
            "from app.core.config.settings import settings",
            "from app.core.logger import logger_manager",
        ]
        
        if self.config_reader.has_database():
            imports.append("from app.core.database import db_manager")
        
        # 添加路由导入
        imports.extend([
            "",
            "from app.routers.v1 import (",
            "    auth_router,",
            "    user_router,",
            ")",
        ])
        
        content = '''# 创建 LoggerManager 实例
logger_manager.setup()

# 创建 Logger 实例
logger = logger_manager.get_logger(__name__)


# 创建生命周期
async def lifespan(_app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚩 Starting the application...")
    logger.info(f"🚧 You are working in {os.getenv('ENV', 'development')} environment")
    '''
        
        if self.config_reader.has_database():
            content += '''
    try:
        # 初始化数据库连接
        await db_manager.initialize()
        logger.info("🎉 Database connections initialized successfully")
        await db_manager.test_connections()
        logger.info("🎉 Database connections test successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.warning("⚠️ Application will start without database connections")
    '''
        
        content += '''
    yield
    '''
        
        if self.config_reader.has_database():
            content += '''
    # 关闭数据库连接
    try:
        await db_manager.close()
        logger.info("🎉 Database connections closed successfully")
    except Exception as e:
        logger.error(f"❌ Database connection closed failed: {e}")
        logger.warning("⚠️ Database connection closed failed")
    '''
        
        content += '''

# 创建 FastAPI 实例
app = FastAPI(
    lifespan=lifespan,
    title=settings.app.APP_NAME,
    version=settings.app.APP_VERSION,
    description=settings.app.APP_DESCRIPTION,
)


# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    """HTTP 异常处理器"""
    logger.error(f"HTTPException: {exc}")
    error_detail = exc.detail
    
    if isinstance(error_detail, dict):
        error_message = error_detail.get("error", str(error_detail))
    else:
        error_message = str(error_detail)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": exc.status_code, "error": error_message},
    )


@app.exception_handler(Exception)
async def general_exception_handler(_request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": 500, "error": "Internal server error"},
    )


# CORS 中间件
'''
        
        if self.config_reader.has_cors():
            content += '''allow_origins = [x.strip() for x in settings.cors.CORS_ALLOWED_ORIGINS.split(',') if x.strip()]
allow_methods = [x.strip() for x in settings.cors.CORS_ALLOW_METHODS.split(',') if x.strip()]
allow_headers = [x.strip() for x in settings.cors.CORS_ALLOW_HEADERS.split(',') if x.strip()]
allow_credentials = settings.cors.CORS_ALLOW_CREDENTIALS
expose_headers = [x.strip() for x in settings.cors.CORS_EXPOSE_HEADERS.split(',') if x.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
    allow_credentials=allow_credentials,
    expose_headers=expose_headers,
)
'''
        
        content += '''

# 注册路由
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")


# 静态文件
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# 健康检查端点
@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


# OpenAPI 文档
def custom_openapi():
    """自定义 OpenAPI 文档"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app.APP_NAME,
        version=settings.app.APP_VERSION,
        description=settings.app.APP_DESCRIPTION,
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# 启动应用
if __name__ == "__main__":
    if os.getenv("ENV") == "development":
        logger.info("🚩 Starting the application in development mode...")
        uvicorn.run(
            app="app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
        )
'''
        
        self.file_ops.create_python_file(
            file_path="app/main.py",
            docstring="FastAPI 应用主入口",
            imports=imports,
            content=content,
            overwrite=True
        )
