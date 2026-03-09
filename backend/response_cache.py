"""
Response Cache
LRU cache for LLM responses with TTL
"""
import re
import logging
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib

logger = logging.getLogger(__name__)


class ResponseCache:
    """
    LRU cache for LLM responses
    - Max 1000 entries
    - 24-hour TTL
    - Normalized cache keys
    """
    
    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        """
        Initialize response cache
        
        Args:
            max_size: Maximum number of cache entries
            ttl_hours: Time-to-live in hours
        """
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
        self.hits = 0
        self.misses = 0
        
        logger.info(f"Response cache initialized: max_size={max_size}, ttl={ttl_hours}h")
    
    def get(self, query: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Get cached response if exists and not expired
        
        Args:
            query: User query
            context: Optional context dictionary
            
        Returns:
            Cached response or None
        """
        cache_key = self.normalize_key(query, context)
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            
            # Check if expired
            if datetime.now() > entry['expires_at']:
                # Remove expired entry
                del self.cache[cache_key]
                self.misses += 1
                logger.debug(f"Cache miss (expired): {cache_key[:50]}...")
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(cache_key)
            entry['hit_count'] += 1
            self.hits += 1
            
            logger.info(f"Cache hit: {cache_key[:50]}... (hits: {entry['hit_count']})")
            return entry['response']
        
        self.misses += 1
        logger.debug(f"Cache miss: {cache_key[:50]}...")
        return None
    
    def put(self, query: str, response: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Store response in cache with LRU eviction
        
        Args:
            query: User query
            response: LLM response
            context: Optional context dictionary
        """
        cache_key = self.normalize_key(query, context)
        
        # Check if we need to evict
        if len(self.cache) >= self.max_size and cache_key not in self.cache:
            # Remove least recently used (first item)
            evicted_key, evicted_entry = self.cache.popitem(last=False)
            logger.debug(f"Cache eviction (LRU): {evicted_key[:50]}...")
        
        # Add or update entry
        self.cache[cache_key] = {
            'response': response,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + self.ttl,
            'hit_count': 0
        }
        
        # Move to end (most recently used)
        self.cache.move_to_end(cache_key)
        
        logger.debug(f"Cache put: {cache_key[:50]}... (size: {len(self.cache)})")
    
    def normalize_key(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate normalized cache key
        
        Args:
            query: User query
            context: Optional context dictionary
            
        Returns:
            Normalized cache key
        """
        # Lowercase
        normalized = query.lower().strip()
        
        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Simple stemming (remove common suffixes)
        normalized = re.sub(r'ing\b', '', normalized)
        normalized = re.sub(r'ed\b', '', normalized)
        normalized = re.sub(r's\b', '', normalized)
        
        # Add context to key if provided
        if context:
            context_str = str(sorted(context.items()))
            normalized = f"{normalized}|{context_str}"
        
        # Hash for consistent length
        key_hash = hashlib.md5(normalized.encode()).hexdigest()
        
        return f"{normalized[:50]}_{key_hash[:8]}"
    
    def get_hit_rate(self) -> float:
        """
        Calculate cache hit rate percentage
        
        Returns:
            Hit rate (0.0 to 100.0)
        """
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100.0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary of cache stats
        """
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.get_hit_rate(),
            'ttl_hours': self.ttl.total_seconds() / 3600
        }
    
    def log_stats(self) -> None:
        """Log cache statistics to terminal"""
        stats = self.get_stats()
        logger.info(
            f"Cache stats: size={stats['size']}/{stats['max_size']}, "
            f"hits={stats['hits']}, misses={stats['misses']}, "
            f"hit_rate={stats['hit_rate']:.1f}%"
        )
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")
    
    def remove_expired(self) -> int:
        """
        Remove all expired entries
        
        Returns:
            Number of entries removed
        """
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Removed {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
