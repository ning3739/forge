"""Rate limiting decorator generator"""
from core.decorators import Generator
from ..base import BaseTemplateGenerator


@Generator(
    category="decorator",
    priority=85,
    description="Generate rate limiting decorator (app/decorators/rate_limit.py)"
)
class RateLimitDecoratorGenerator(BaseTemplateGenerator):
    """Rate limiting decorator generator"""
    
    def generate(self) -> None:
        """Generate rate limiting decorator file"""
        content = '''"""Rate limiting decorator for API endpoints"""
import time
from functools import wraps
from typing import Dict, Callable
from fastapi import HTTPException, Request
from collections import defaultdict


class RateLimiter:
    """Simple in-memory rate limiter
    
    Note: This is a basic implementation suitable for single-instance applications.
    For production with multiple instances, consider using Redis-based rate limiting.
    """
    
    def __init__(self):
        # Store: {identifier: [(timestamp, count), ...]}
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """Check if request is allowed based on rate limit
        
        Args:
            identifier: Unique identifier (e.g., IP address, user ID)
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            True if request is allowed, False otherwise
        """
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Clean old requests outside the time window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff_time
        ]
        
        # Check if limit exceeded
        if len(self.requests[identifier]) >= max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(current_time)
        return True
    
    def get_remaining(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> int:
        """Get remaining requests in current window
        
        Args:
            identifier: Unique identifier
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Number of remaining requests
        """
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Count requests in current window
        recent_requests = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff_time
        ]
        
        return max(0, max_requests - len(recent_requests))


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
    identifier_func: Callable[[Request], str] = None
):
    """Rate limiting decorator for FastAPI endpoints
    
    Args:
        max_requests: Maximum number of requests allowed in the time window
        window_seconds: Time window in seconds
        identifier_func: Function to extract identifier from request (default: IP address)
        
    Example:
        @router.get("/api/data")
        @rate_limit(max_requests=10, window_seconds=60)
        async def get_data(request: Request):
            return {"data": "value"}
        
        # Custom identifier (e.g., user ID)
        @router.get("/api/user-data")
        @rate_limit(
            max_requests=50,
            window_seconds=3600,
            identifier_func=lambda req: req.state.user.id
        )
        async def get_user_data(request: Request):
            return {"data": "value"}
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get('request')
            
            if not request:
                raise ValueError("Request object not found in function arguments")
            
            # Get identifier (default: client IP)
            if identifier_func:
                identifier = identifier_func(request)
            else:
                identifier = request.client.host if request.client else "unknown"
            
            # Check rate limit
            if not rate_limiter.is_allowed(identifier, max_requests, window_seconds):
                remaining = rate_limiter.get_remaining(identifier, max_requests, window_seconds)
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again in {window_seconds} seconds.",
                    headers={
                        "X-RateLimit-Limit": str(max_requests),
                        "X-RateLimit-Remaining": str(remaining),
                        "X-RateLimit-Reset": str(int(time.time() + window_seconds))
                    }
                )
            
            # Execute the endpoint
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Predefined rate limit decorators for common use cases
def rate_limit_strict(func):
    """Strict rate limit: 10 requests per minute"""
    return rate_limit(max_requests=10, window_seconds=60)(func)


def rate_limit_moderate(func):
    """Moderate rate limit: 100 requests per minute"""
    return rate_limit(max_requests=100, window_seconds=60)(func)


def rate_limit_relaxed(func):
    """Relaxed rate limit: 1000 requests per hour"""
    return rate_limit(max_requests=1000, window_seconds=3600)(func)
'''
        
        self.file_ops.create_file(
            file_path="app/decorators/rate_limit.py",
            content=content,
            overwrite=True
        )
