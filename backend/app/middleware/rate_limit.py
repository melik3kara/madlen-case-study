"""Rate limiting middleware for API protection."""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    
    # Requests per window 
    requests_per_minute: int = 60  
    requests_per_hour: int = 500
    
    # Chat-specific limits
    chat_requests_per_minute: int = 20  
    chat_requests_per_hour: int = 200
    
    # Burst protection
    max_burst: int = 10 
    
    # Exempt paths
    exempt_paths: Tuple[str, ...] = ("/health", "/metrics", "/docs", "/redoc", "/openapi.json")


# Global config instance
rate_limit_config = RateLimitConfig()


class RateLimiter:
    """Token bucket rate limiter with sliding window."""
    
    def __init__(self):
        # Structure: {client_ip: {window_key: request_count}}
        self._minute_windows: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self._hour_windows: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self._second_windows: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self._last_cleanup = time.time()
    
    def _cleanup_old_windows(self, current_time: float):
        """Remove old window data to prevent memory growth."""
        if current_time - self._last_cleanup < 60:  # Cleanup every minute
            return
        
        current_minute = int(current_time // 60)
        current_hour = int(current_time // 3600)
        
        # Cleanup minute windows (keep last 2 minutes)
        for ip in list(self._minute_windows.keys()):
            windows = self._minute_windows[ip]
            for window_key in list(windows.keys()):
                if window_key < current_minute - 1:
                    del windows[window_key]
            if not windows:
                del self._minute_windows[ip]
        
        # Cleanup hour windows (keep last 2 hours)
        for ip in list(self._hour_windows.keys()):
            windows = self._hour_windows[ip]
            for window_key in list(windows.keys()):
                if window_key < current_hour - 1:
                    del windows[window_key]
            if not windows:
                del self._hour_windows[ip]
        
        # Cleanup second windows (keep last 2 seconds)
        current_second = int(current_time)
        for ip in list(self._second_windows.keys()):
            windows = self._second_windows[ip]
            for window_key in list(windows.keys()):
                if window_key < current_second - 1:
                    del windows[window_key]
            if not windows:
                del self._second_windows[ip]
        
        self._last_cleanup = current_time
    
    def check_rate_limit(
        self, 
        client_ip: str, 
        is_chat: bool = False,
        config: RateLimitConfig = rate_limit_config
    ) -> Tuple[bool, str, Dict[str, int]]:
        """
        Check if request is within rate limits.
        
        Returns:
            Tuple of (allowed, reason, headers)
        """
        current_time = time.time()
        self._cleanup_old_windows(current_time)
        
        current_second = int(current_time)
        current_minute = int(current_time // 60)
        current_hour = int(current_time // 3600)
        
        # Get current counts
        second_count = self._second_windows[client_ip].get(current_second, 0)
        minute_count = self._minute_windows[client_ip].get(current_minute, 0)
        hour_count = self._hour_windows[client_ip].get(current_hour, 0)
        
        # Determine limits based on endpoint
        minute_limit = config.chat_requests_per_minute if is_chat else config.requests_per_minute
        hour_limit = config.chat_requests_per_hour if is_chat else config.requests_per_hour
        
        # Headers for rate limit info
        headers = {
            "X-RateLimit-Limit-Minute": minute_limit,
            "X-RateLimit-Remaining-Minute": max(0, minute_limit - minute_count - 1),
            "X-RateLimit-Limit-Hour": hour_limit,
            "X-RateLimit-Remaining-Hour": max(0, hour_limit - hour_count - 1),
        }
        
        # Check burst protection
        if second_count >= config.max_burst:
            return False, "Burst limit exceeded. Please slow down.", headers
        
        # Check minute limit
        if minute_count >= minute_limit:
            headers["Retry-After"] = 60 - int(current_time % 60)
            return False, f"Rate limit exceeded. Max {minute_limit} requests per minute.", headers
        
        # Check hour limit
        if hour_count >= hour_limit:
            headers["Retry-After"] = 3600 - int(current_time % 3600)
            return False, f"Hourly rate limit exceeded. Max {hour_limit} requests per hour.", headers
        
        # Request allowed, increment counters
        self._second_windows[client_ip][current_second] += 1
        self._minute_windows[client_ip][current_minute] += 1
        self._hour_windows[client_ip][current_hour] += 1
        
        return True, "", headers


# Global rate limiter instance
_rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests."""
    
    def __init__(self, app, config: RateLimitConfig = rate_limit_config):
        super().__init__(app)
        self.config = config
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for proxy headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        return request.client.host if request.client else "unknown"
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request through rate limiter."""
        path = request.url.path
        
        # Skip exempt paths
        if path in self.config.exempt_paths:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        
        # Session management endpoints should NOT count towards chat limit
        # Only actual chat messages to /api/chat (POST without session operations)
        session_management_paths = (
            "/sessions",
            "/new-session", 
            "/switch",
            "/clear",
        )
        is_session_operation = any(p in path for p in session_management_paths)
        is_chat = path.endswith("/api/chat") and request.method == "POST" and not is_session_operation
        
        # DEBUG LOG
        print(f"🔒 [RateLimit] IP={client_ip}, Path={path}, Method={request.method}, IsChat={is_chat}")
        
        allowed, reason, headers = _rate_limiter.check_rate_limit(
            client_ip, is_chat, self.config
        )
        
        # DEBUG LOG
        remaining = headers.get('X-RateLimit-Remaining-Minute', '?')
        print(f"🔒 [RateLimit] Allowed={allowed}, Remaining={remaining}, Reason={reason}")
        
        if not allowed:
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "detail": reason,
                    "type": "TooManyRequests"
                }
            )
            for key, value in headers.items():
                response.headers[key] = str(value)
            return response
        
        # Process request and add rate limit headers
        response = await call_next(request)
        for key, value in headers.items():
            response.headers[key] = str(value)
        
        return response
