"""
Redis client and cache management
"""

from typing import Any, Optional
import json
import redis.asyncio as aioredis
from redis.asyncio import Redis
from functools import wraps
import hashlib

from app.core.config import settings
from app.core.logging import logger


# ============================================
# REDIS CLIENT
# ============================================

class RedisManager:
    """
    Redis connection manager with multiple DB support
    """

    def __init__(self):
        self._clients: dict[int, Redis] = {}

    async def get_client(self, db: int = 0) -> Redis:
        """
        Get Redis client for specific DB
        """
        if db not in self._clients:
            self._clients[db] = await aioredis.from_url(
                settings.REDIS_URL.rsplit("/", 1)[0] + f"/{db}",
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=settings.REDIS_TIMEOUT,
                socket_connect_timeout=settings.REDIS_TIMEOUT,
            )
            logger.info(f"Redis client created for DB {db}")
        return self._clients[db]

    async def close_all(self):
        """
        Close all Redis connections
        """
        for db, client in self._clients.items():
            await client.close()
            logger.info(f"Redis client closed for DB {db}")
        self._clients.clear()

    async def ping(self, db: int = 0) -> bool:
        """
        Check Redis connection
        """
        try:
            client = await self.get_client(db)
            await client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed for DB {db}: {e}")
            return False


# Global Redis manager
redis_manager = RedisManager()


async def get_redis(db: int = 0) -> Redis:
    """
    Get Redis client dependency
    """
    return await redis_manager.get_client(db)


# ============================================
# CACHE UTILITIES
# ============================================

class Cache:
    """
    High-level cache interface
    """

    def __init__(self, db: int = None):
        self.db = db or settings.REDIS_CACHE_DB

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        """
        try:
            redis = await redis_manager.get_client(self.db)
            value = await redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        """
        Set value in cache with TTL (default 1 hour)
        """
        try:
            redis = await redis_manager.get_client(self.db)
            serialized = json.dumps(value, default=str)
            await redis.setex(key, ttl, serialized)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")

    async def delete(self, key: str):
        """
        Delete key from cache
        """
        try:
            redis = await redis_manager.get_client(self.db)
            await redis.delete(key)
            logger.debug(f"Cache deleted: {key}")
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        """
        try:
            redis = await redis_manager.get_client(self.db)
            return await redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str):
        """
        Clear all keys matching pattern
        """
        try:
            redis = await redis_manager.get_client(self.db)
            keys = []
            async for key in redis.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                await redis.delete(*keys)
                logger.info(f"Cache cleared: {len(keys)} keys matching {pattern}")
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment counter
        """
        try:
            redis = await redis_manager.get_client(self.db)
            return await redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return 0

    async def expire(self, key: str, ttl: int):
        """
        Set expiration on existing key
        """
        try:
            redis = await redis_manager.get_client(self.db)
            await redis.expire(key, ttl)
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")


# Global cache instance
cache = Cache()


# ============================================
# CACHE DECORATORS
# ============================================

def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Cache decorator for async functions

    Usage:
        @cached(ttl=3600, key_prefix="user")
        async def get_user(user_id: int):
            return await db.query(User).filter(User.id == user_id).first()
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value

            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl=ttl)
            logger.debug(f"Cache miss: {cache_key}")
            return result

        return wrapper
    return decorator


def cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments
    """
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


# ============================================
# RATE LIMITING
# ============================================

class RateLimiter:
    """
    Rate limiter using Redis
    """

    def __init__(self, db: int = None):
        self.db = db or settings.REDIS_CACHE_DB

    async def is_allowed(
        self,
        key: str,
        max_requests: int,
        window: int = 60
    ) -> tuple[bool, int]:
        """
        Check if request is allowed

        Returns:
            (allowed, remaining_requests)
        """
        try:
            redis = await redis_manager.get_client(self.db)

            current = await redis.get(key)
            if current is None:
                await redis.setex(key, window, 1)
                return True, max_requests - 1

            current = int(current)
            if current >= max_requests:
                ttl = await redis.ttl(key)
                return False, 0

            await redis.incr(key)
            return True, max_requests - current - 1

        except Exception as e:
            logger.error(f"Rate limit error for key {key}: {e}")
            return True, max_requests  # Fail open

    async def reset(self, key: str):
        """
        Reset rate limit counter
        """
        try:
            redis = await redis_manager.get_client(self.db)
            await redis.delete(key)
        except Exception as e:
            logger.error(f"Rate limit reset error for key {key}: {e}")


# Global rate limiter
rate_limiter = RateLimiter()


# ============================================
# DISTRIBUTED LOCK
# ============================================

class DistributedLock:
    """
    Distributed lock using Redis
    """

    def __init__(self, key: str, timeout: int = 10, db: int = None):
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.db = db or settings.REDIS_CACHE_DB
        self.acquired = False

    async def __aenter__(self):
        redis = await redis_manager.get_client(self.db)
        self.acquired = await redis.set(
            self.key,
            "locked",
            ex=self.timeout,
            nx=True
        )
        if not self.acquired:
            raise RuntimeError(f"Failed to acquire lock: {self.key}")
        logger.debug(f"Lock acquired: {self.key}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.acquired:
            redis = await redis_manager.get_client(self.db)
            await redis.delete(self.key)
            logger.debug(f"Lock released: {self.key}")
