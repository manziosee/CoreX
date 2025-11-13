from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Dict, Tuple
import redis
from app.core.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent API abuse"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute window
        
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                decode_responses=True
            )
        except:
            # Fallback to in-memory storage
            self.redis_client = None
            self._requests: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/"]:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if not self._is_allowed(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Record the request
        self._record_request(client_ip)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed based on rate limit"""
        current_time = time.time()
        
        if self.redis_client:
            # Use Redis for distributed rate limiting
            key = f"rate_limit:{client_ip}"
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, current_time - self.window_size)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, self.window_size)
            
            results = pipe.execute()
            request_count = results[1]
            
            return request_count < self.requests_per_minute
        else:
            # Fallback to in-memory storage
            if client_ip not in self._requests:
                self._requests[client_ip] = []
            
            # Clean old requests
            self._requests[client_ip] = [
                req_time for req_time in self._requests[client_ip]
                if current_time - req_time < self.window_size
            ]
            
            return len(self._requests[client_ip]) < self.requests_per_minute
    
    def _record_request(self, client_ip: str):
        """Record the current request"""
        current_time = time.time()
        
        if not self.redis_client:
            # Only record for in-memory storage (Redis records in _is_allowed)
            if client_ip not in self._requests:
                self._requests[client_ip] = []
            self._requests[client_ip].append(current_time)