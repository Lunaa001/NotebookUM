"""Redis caching service for documents and summaries."""

import logging
import json
from typing import Any, Optional, Callable, TypeVar, get_type_hints
from functools import wraps
from datetime import timedelta
import redis
import os

logger = logging.getLogger(__name__)

# Cache TTLs
CACHE_TTL_DOCUMENT_TEXT = timedelta(days=7)  # 7 days
CACHE_TTL_DOCUMENT_METADATA = timedelta(days=7)  # 7 days
CACHE_TTL_SUMMARY = timedelta(days=30)  # 30 days
CACHE_TTL_HOT_SUMMARIES = timedelta(hours=1)  # 1 hour

# Type variable for decorators
T = TypeVar("T")


class CacheService:
    """
    Redis-based caching service with TTL management and graceful fallback.
    
    If Redis is unavailable, operations gracefully fall through without caching.
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        db: int = 0,
        password: str = None,
        auto_connect: bool = True,
    ):
        """
        Initialize cache service.
        
        Args:
            host: Redis host (default from REDIS_HOST env var or localhost)
            port: Redis port (default from REDIS_PORT env var or 6379)
            db: Redis database number (default 0)
            password: Redis password (default from REDIS_PASSWORD env var)
            auto_connect: Whether to connect on init (default True)
        """
        self.host = host or os.getenv("REDIS_HOST", "localhost")
        self.port = port or int(os.getenv("REDIS_PORT", 6379))
        self.db = db
        self.password = password or os.getenv("REDIS_PASSWORD")
        self._redis: Optional[redis.Redis] = None
        self._connected = False
        
        # Metrics
        self._metrics = {
            "total_gets": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_sets": 0,
            "total_deletes": 0,
            "errors": 0,
        }
        
        if auto_connect:
            self.connect()
    
    def connect(self) -> bool:
        """
        Connect to Redis.
        
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            self._redis = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
                socket_connect_timeout=5,
            )
            # Test connection
            self._redis.ping()
            self._connected = True
            logger.info(f"✓ Connected to Redis at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.warning(f"⚠️  Failed to connect to Redis: {e}")
            self._connected = False
            self._redis = None
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to Redis."""
        return self._connected
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/error
        """
        if not self._connected:
            return None
        
        try:
            self._metrics["total_gets"] += 1
            value = self._redis.get(key)
            
            if value is not None:
                self._metrics["cache_hits"] += 1
                logger.debug(f"💾 Cache HIT: {key}")
                try:
                    # Try to deserialize JSON
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # Return as string if not JSON
                    return value
            else:
                self._metrics["cache_misses"] += 1
                logger.debug(f"💾 Cache MISS: {key}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting cache key {key}: {e}")
            self._metrics["errors"] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live (default: no expiration)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._connected:
            return False
        
        try:
            self._metrics["total_sets"] += 1
            
            # Serialize value to JSON
            serialized = json.dumps(value) if not isinstance(value, str) else value
            
            # Set with TTL
            if ttl:
                self._redis.setex(
                    key,
                    int(ttl.total_seconds()),
                    serialized,
                )
            else:
                self._redis.set(key, serialized)
            
            logger.debug(f"💾 Cache SET: {key} (TTL: {ttl})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting cache key {key}: {e}")
            self._metrics["errors"] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key (supports wildcards with*)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._connected:
            return False
        
        try:
            self._metrics["total_deletes"] += 1
            
            # Handle wildcard patterns
            if "*" in key:
                keys = self._redis.keys(key)
                if keys:
                    self._redis.delete(*keys)
                logger.debug(f"💾 Cache DELETE (pattern): {key} ({len(keys)} keys)")
            else:
                self._redis.delete(key)
                logger.debug(f"💾 Cache DELETE: {key}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting cache key {key}: {e}")
            self._metrics["errors"] += 1
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._connected:
            return False
        
        try:
            return self._redis.exists(key) > 0
        except Exception as e:
            logger.error(f"❌ Error checking key existence {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get TTL for key in seconds.
        
        Returns:
            TTL in seconds, -1 if no expiration, -2 if key doesn't exist, None on error
        """
        if not self._connected:
            return None
        
        try:
            return self._redis.ttl(key)
        except Exception as e:
            logger.error(f"❌ Error getting TTL for {key}: {e}")
            return None
    
    def flush_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.
        
        Args:
            pattern: Pattern like "document:123:*"
            
        Returns:
            Number of keys deleted
        """
        if not self._connected:
            return 0
        
        try:
            keys = self._redis.keys(pattern)
            if keys:
                self._redis.delete(*keys)
            logger.debug(f"💾 Cache FLUSH pattern: {pattern} ({len(keys)} keys)")
            return len(keys)
        except Exception as e:
            logger.error(f"❌ Error flushing pattern {pattern}: {e}")
            self._metrics["errors"] += 1
            return 0
    
    def clear_all(self) -> bool:
        """Clear entire cache (use with caution!)."""
        if not self._connected:
            return False
        
        try:
            self._redis.flushdb()
            logger.warning("🗑️  Cache completely cleared")
            return True
        except Exception as e:
            logger.error(f"❌ Error clearing cache: {e}")
            self._metrics["errors"] += 1
            return False
    
    def get_metrics(self) -> dict:
        """Get cache metrics."""
        total_requests = self._metrics["total_gets"]
        hit_rate = (
            (self._metrics["cache_hits"] / total_requests * 100)
            if total_requests > 0
            else 0
        )
        
        return {
            **self._metrics,
            "hit_rate_percent": hit_rate,
            "connected": self._connected,
        }
    
    def reset_metrics(self):
        """Reset metrics."""
        self._metrics = {
            "total_gets": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_sets": 0,
            "total_deletes": 0,
            "errors": 0,
        }


# Global cache instance
_cache_instance: Optional[CacheService] = None


def get_cache() -> CacheService:
    """Get or create global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheService()
    return _cache_instance


def cache_result(ttl: timedelta = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live for cached result
        
    Example:
        @cache_result(ttl=timedelta(hours=1))
        def get_document(doc_id: int) -> Document:
            return db.query(Document).get(doc_id)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            cache = get_cache()
            
            # Build cache key from function name and arguments
            cache_key = f"{func.__module__}:{func.__name__}:{args}:{sorted(kwargs.items())}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    
    return decorator


def invalidate_cache(*patterns: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to invalidate cache patterns after function execution.
    
    Args:
        patterns: Cache key patterns to invalidate
        
    Example:
        @invalidate_cache("document:*", "summary:*")
        def delete_document(doc_id: int):
            db.session.delete(...)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Call function
            result = func(*args, **kwargs)
            
            # Invalidate patterns
            cache = get_cache()
            for pattern in patterns:
                cache.flush_pattern(pattern)
            
            return result
        
        return wrapper
    
    return decorator
