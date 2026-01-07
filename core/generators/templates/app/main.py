"""Main.py generategenerator"""
from core.decorators import Generator
from pathlib import Path
from .base import BaseTemplateGenerator


@Generator(
    category="app",
    priority=90,
    requires=["ConfigSettingsGenerator", "LoggerManagerGenerator", "DatabaseConnectionGenerator"],
    description="Generate main application entry point (app/main.py)"
)
class MainGenerator(BaseTemplateGenerator):
    """Main.py File generator"""
    
    def generate(self) -> None:
        """generate main.py file"""
        auth_type = self.config_reader.get_auth_type() if self.config_reader.has_auth() else None
        
        if auth_type:
            self._generate_main_with_auth()
        else:
            self._generate_basic_main()
    
    def _generate_basic_main(self) -> None:
        """generatebase main.py(noneauthentication)"""
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
            "from app.core.database import db_manager",  # Database is nowrequired
        ]
        
        content = '''# Create LoggerManager instance
logger_manager.setup()

# Create Logger instance
logger = logger_manager.get_logger(__name__)


# Create lifespan
async def lifespan(_app: FastAPI):
    """Application lifespan management"""
    logger.info("🚩 Starting the application...")
    logger.info(f"🚧 You are working in {os.getenv('ENV', 'development')} environment")
    
    try:
        # Initializedatabase connection
        await db_manager.initialize()
        logger.info("🎉 Database connections initialized successfully")
        await db_manager.test_connections()
        logger.info("🎉 Database connections test successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.warning("⚠️ Application will start without database connections")
    
    yield
    
    # closedatabase connection
    try:
        await db_manager.close()
        logger.info("🎉 Database connections closed successfully")
    except Exception as e:
        logger.error(f"❌ Database connection closed failed: {e}")
        logger.warning("⚠️ Database connection closed failed")
'''
        
        content += '''

# Create FastAPI instance
app = FastAPI(
    lifespan=lifespan,
    title=settings.app.APP_NAME,
    version=settings.app.APP_VERSION,
    description=settings.app.APP_DESCRIPTION,
)


# globalexceptionprocessgenerator
@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    """HTTP exceptionprocessgenerator"""
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
    """General exception handler"""
    logger.error(f"Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": 500, "error": "Internal server error"},
    )


# CORS middleware
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

# staticfile
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# OpenAPI documentation
def custom_openapi():
    """Custom OpenAPI documentation"""
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


# startapplication
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
            docstring="FastAPI application main entry point",
            imports=imports,
            content=content,
            overwrite=True
        )
    
    def _generate_main_with_auth(self) -> None:
        """Generate main.py with authentication"""
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
            "from app.core.database import db_manager",  # Database is nowrequired
        ]
        
        # addrouterimport
        imports.extend([
            "",
            "from app.routers.v1 import (",
            "    auth_router,",
            "    user_router,",
            ")",
        ])
        
        content = '''# Create LoggerManager instance
logger_manager.setup()

# Create Logger instance
logger = logger_manager.get_logger(__name__)


# Create lifespan
async def lifespan(_app: FastAPI):
    """Application lifespan management"""
    logger.info("🚩 Starting the application...")
    logger.info(f"🚧 You are working in {os.getenv('ENV', 'development')} environment")
    
    try:
        # Initializedatabase connection
        await db_manager.initialize()
        logger.info("🎉 Database connections initialized successfully")
        await db_manager.test_connections()
        logger.info("🎉 Database connections test successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.warning("⚠️ Application will start without database connections")
    
    yield
    
    # closedatabase connection
    try:
        await db_manager.close()
        logger.info("🎉 Database connections closed successfully")
    except Exception as e:
        logger.error(f"❌ Database connection closed failed: {e}")
        logger.warning("⚠️ Database connection closed failed")
'''
        
        content += '''

# Create FastAPI instance
app = FastAPI(
    lifespan=lifespan,
    title=settings.app.APP_NAME,
    version=settings.app.APP_VERSION,
    description=settings.app.APP_DESCRIPTION,
)


# globalexceptionprocessgenerator
@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    """HTTP exceptionprocessgenerator"""
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
    """General exception handler"""
    logger.error(f"Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": 500, "error": "Internal server error"},
    )


# CORS middleware
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

# registerrouter
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")


# staticfile
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# OpenAPI documentation
def custom_openapi():
    """Custom OpenAPI documentation"""
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


# startapplication
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
            docstring="FastAPI application main entry point",
            imports=imports,
            content=content,
            overwrite=True
        )
