from typing import Set
from datetime import datetime, timedelta
import redis
from app.core.config import settings

class JWTBlacklist:
    """JWT Token Blacklist Service using Redis"""
    
    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                decode_responses=True
            )
        except:
            # Fallback to in-memory storage if Redis is not available
            self.redis_client = None
            self._blacklisted_tokens: Set[str] = set()
    
    def blacklist_token(self, token: str, expires_at: datetime):
        """Add token to blacklist"""
        if self.redis_client:
            # Calculate TTL for Redis
            ttl = int((expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                self.redis_client.setex(f"blacklist:{token}", ttl, "1")
        else:
            # Fallback to in-memory storage
            self._blacklisted_tokens.add(token)
    
    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        if self.redis_client:
            return self.redis_client.exists(f"blacklist:{token}")
        else:
            return token in self._blacklisted_tokens
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens (Redis handles this automatically)"""
        if not self.redis_client:
            # For in-memory storage, we'd need to track expiration times
            # This is a simplified implementation
            pass

# Global instance
jwt_blacklist = JWTBlacklist()