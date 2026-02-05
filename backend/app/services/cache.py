"""Simple in-memory cache for frequently accessed data."""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Simple in-memory cache
_cache: Dict[str, Dict[str, Any]] = {}


def get_cache_key(prefix: str, key: str) -> str:
    """Generate cache key."""
    return f"{prefix}:{key}"


def get_cached(key: str, ttl_seconds: int = 300) -> Optional[Any]:
    """
    Get value from cache if not expired.
    
    Args:
        key: Cache key
        ttl_seconds: Time to live in seconds (default: 5 minutes)
        
    Returns:
        Cached value or None if not found/expired
    """
    if key not in _cache:
        return None
    
    entry = _cache[key]
    if datetime.now() > entry['expires_at']:
        del _cache[key]
        return None
    
    return entry['value']


def set_cached(key: str, value: Any, ttl_seconds: int = 300):
    """
    Set value in cache.
    
    Args:
        key: Cache key
        value: Value to cache
        ttl_seconds: Time to live in seconds (default: 5 minutes)
    """
    _cache[key] = {
        'value': value,
        'expires_at': datetime.now() + timedelta(seconds=ttl_seconds)
    }


def clear_cache(prefix: Optional[str] = None):
    """Clear cache entries, optionally filtered by prefix."""
    if prefix:
        keys_to_delete = [k for k in _cache.keys() if k.startswith(prefix)]
        for key in keys_to_delete:
            del _cache[key]
    else:
        _cache.clear()


def get_cache_stats() -> Dict[str, int]:
    """Get cache statistics."""
    return {
        'total_entries': len(_cache),
        'expired_entries': sum(
            1 for entry in _cache.values()
            if datetime.now() > entry['expires_at']
        )
    }
