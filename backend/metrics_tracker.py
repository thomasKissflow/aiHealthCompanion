"""
Metrics Tracker for AI Health Companion

Tracks LLM usage optimization metrics including fast path usage,
cache hits/misses, and LLM call reduction.

Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7
"""

import logging
from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MetricsSnapshot:
    """Snapshot of metrics at a point in time"""
    timestamp: datetime
    total_queries: int
    fast_path_queries: int
    cache_hits: int
    cache_misses: int
    llm_calls: int
    cache_hit_rate: float
    llm_reduction_rate: float


class MetricsTracker:
    """
    Tracks and logs LLM usage optimization metrics.
    
    Monitors:
    - Total queries received
    - Fast path queries (no LLM)
    - Cache hits and misses
    - LLM calls made
    - Cache hit rate percentage
    - LLM usage reduction percentage
    
    Logs metrics every 10 queries to terminal.
    """
    
    def __init__(self, log_interval: int = 10):
        """
        Initialize metrics tracker.
        
        Args:
            log_interval: Number of queries between metric logs (default: 10)
        """
        self.total_queries = 0
        self.fast_path_queries = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.llm_calls = 0
        self.log_interval = log_interval
        
        logger.info("[Metrics] Tracker initialized")
    
    def record_query(
        self,
        used_fast_path: bool = False,
        cache_hit: bool = False,
        used_llm: bool = False
    ) -> None:
        """
        Record metrics for a single query.
        
        Requirements: 19.1, 19.2, 19.3, 19.4
        
        Args:
            used_fast_path: True if query was served via fast path (no LLM)
            cache_hit: True if response was served from cache
            used_llm: True if LLM was invoked for this query
        """
        self.total_queries += 1
        
        if used_fast_path:
            self.fast_path_queries += 1
        
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        
        if used_llm:
            self.llm_calls += 1
        
        # Log metrics at intervals
        if self.total_queries % self.log_interval == 0:
            self.log_metrics()
    
    def get_cache_hit_rate(self) -> float:
        """
        Calculate cache hit rate as a percentage.
        
        Requirements: 19.5
        
        Returns:
            Cache hit rate percentage (0-100)
        """
        total_cache_queries = self.cache_hits + self.cache_misses
        
        if total_cache_queries == 0:
            return 0.0
        
        return (self.cache_hits / total_cache_queries) * 100
    
    def get_llm_reduction(self) -> float:
        """
        Calculate LLM usage reduction percentage.
        
        LLM reduction = (queries without LLM / total queries) * 100
        Queries without LLM = fast path queries + cache hits
        
        Requirements: 19.6
        
        Returns:
            LLM usage reduction percentage (0-100)
        """
        if self.total_queries == 0:
            return 0.0
        
        queries_without_llm = self.fast_path_queries + self.cache_hits
        return (queries_without_llm / self.total_queries) * 100
    
    def log_metrics(self) -> None:
        """
        Log optimization metrics to terminal.
        
        Requirements: 19.7
        """
        cache_hit_rate = self.get_cache_hit_rate()
        llm_reduction = self.get_llm_reduction()
        
        logger.info(
            f"[Metrics] Query #{self.total_queries} - "
            f"Fast Path: {self.fast_path_queries}, "
            f"Cache Hits: {self.cache_hits}, "
            f"Cache Misses: {self.cache_misses}, "
            f"LLM Calls: {self.llm_calls}"
        )
        
        logger.info(
            f"[Metrics] Cache Hit Rate: {cache_hit_rate:.1f}%, "
            f"LLM Reduction: {llm_reduction:.1f}%"
        )
        
        # Check if we're meeting the 85% LLM reduction target
        if llm_reduction >= 85.0:
            logger.info("[Metrics] ✓ Target 85% LLM reduction achieved!")
        elif self.total_queries >= 20:  # Only warn after sufficient queries
            logger.info(
                f"[Metrics] Target 85% LLM reduction not yet achieved "
                f"(current: {llm_reduction:.1f}%)"
            )
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get current metrics as a dictionary.
        
        Returns:
            Dictionary with all current metrics
        """
        return {
            "total_queries": self.total_queries,
            "fast_path_queries": self.fast_path_queries,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "llm_calls": self.llm_calls,
            "cache_hit_rate": self.get_cache_hit_rate(),
            "llm_reduction_rate": self.get_llm_reduction(),
        }
    
    def get_snapshot(self) -> MetricsSnapshot:
        """
        Get a snapshot of current metrics.
        
        Returns:
            MetricsSnapshot with current values
        """
        return MetricsSnapshot(
            timestamp=datetime.now(),
            total_queries=self.total_queries,
            fast_path_queries=self.fast_path_queries,
            cache_hits=self.cache_hits,
            cache_misses=self.cache_misses,
            llm_calls=self.llm_calls,
            cache_hit_rate=self.get_cache_hit_rate(),
            llm_reduction_rate=self.get_llm_reduction(),
        )
    
    def reset(self) -> None:
        """
        Reset all metrics to zero.
        
        Useful for testing or starting a new measurement period.
        """
        self.total_queries = 0
        self.fast_path_queries = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.llm_calls = 0
        
        logger.info("[Metrics] Metrics reset")
    
    def __repr__(self) -> str:
        """String representation of metrics tracker."""
        return (
            f"MetricsTracker("
            f"queries={self.total_queries}, "
            f"fast_path={self.fast_path_queries}, "
            f"cache_hits={self.cache_hits}, "
            f"llm_calls={self.llm_calls}, "
            f"llm_reduction={self.get_llm_reduction():.1f}%"
            f")"
        )
