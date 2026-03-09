"""
Test Metrics Tracker

Tests metrics tracking, cache hit rate calculation, and LLM reduction calculation.
"""

import logging
from metrics_tracker import MetricsTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_initialization():
    """Test metrics tracker initialization"""
    logger.info("=== Testing Initialization ===")
    
    tracker = MetricsTracker(log_interval=10)
    
    assert tracker.total_queries == 0
    assert tracker.fast_path_queries == 0
    assert tracker.cache_hits == 0
    assert tracker.cache_misses == 0
    assert tracker.llm_calls == 0
    
    logger.info("✓ Initialization test passed")


def test_fast_path_query():
    """Test recording fast path query (no LLM)"""
    logger.info("\n=== Testing Fast Path Query ===")
    
    tracker = MetricsTracker(log_interval=100)  # High interval to avoid logging
    
    # Record a fast path query (greeting)
    tracker.record_query(used_fast_path=True, cache_hit=False, used_llm=False)
    
    assert tracker.total_queries == 1
    assert tracker.fast_path_queries == 1
    assert tracker.cache_hits == 0
    assert tracker.cache_misses == 1
    assert tracker.llm_calls == 0
    
    logger.info("✓ Fast path query test passed")


def test_cache_hit_query():
    """Test recording cache hit query"""
    logger.info("\n=== Testing Cache Hit Query ===")
    
    tracker = MetricsTracker(log_interval=100)
    
    # Record a cache hit query
    tracker.record_query(used_fast_path=False, cache_hit=True, used_llm=False)
    
    assert tracker.total_queries == 1
    assert tracker.fast_path_queries == 0
    assert tracker.cache_hits == 1
    assert tracker.cache_misses == 0
    assert tracker.llm_calls == 0
    
    logger.info("✓ Cache hit query test passed")


def test_llm_query():
    """Test recording LLM query (cache miss)"""
    logger.info("\n=== Testing LLM Query ===")
    
    tracker = MetricsTracker(log_interval=100)
    
    # Record an LLM query (cache miss)
    tracker.record_query(used_fast_path=False, cache_hit=False, used_llm=True)
    
    assert tracker.total_queries == 1
    assert tracker.fast_path_queries == 0
    assert tracker.cache_hits == 0
    assert tracker.cache_misses == 1
    assert tracker.llm_calls == 1
    
    logger.info("✓ LLM query test passed")


def test_cache_hit_rate_calculation():
    """Test cache hit rate calculation"""
    logger.info("\n=== Testing Cache Hit Rate Calculation ===")
    
    tracker = MetricsTracker(log_interval=100)
    
    # Record 10 queries: 6 cache hits, 4 cache misses
    for _ in range(6):
        tracker.record_query(used_fast_path=False, cache_hit=True, used_llm=False)
    
    for _ in range(4):
        tracker.record_query(used_fast_path=False, cache_hit=False, used_llm=True)
    
    cache_hit_rate = tracker.get_cache_hit_rate()
    expected_rate = (6 / 10) * 100  # 60%
    
    assert abs(cache_hit_rate - expected_rate) < 0.01
    logger.info(f"Cache hit rate: {cache_hit_rate:.1f}% (expected: {expected_rate:.1f}%)")
    
    logger.info("✓ Cache hit rate calculation test passed")


def test_llm_reduction_calculation():
    """Test LLM usage reduction calculation"""
    logger.info("\n=== Testing LLM Reduction Calculation ===")
    
    tracker = MetricsTracker(log_interval=100)
    
    # Record 20 queries:
    # - 10 fast path (no LLM)
    # - 7 cache hits (no LLM)
    # - 3 LLM calls
    # Expected reduction: (10 + 7) / 20 * 100 = 85%
    
    for _ in range(10):
        tracker.record_query(used_fast_path=True, cache_hit=False, used_llm=False)
    
    for _ in range(7):
        tracker.record_query(used_fast_path=False, cache_hit=True, used_llm=False)
    
    for _ in range(3):
        tracker.record_query(used_fast_path=False, cache_hit=False, used_llm=True)
    
    llm_reduction = tracker.get_llm_reduction()
    expected_reduction = ((10 + 7) / 20) * 100  # 85%
    
    assert abs(llm_reduction - expected_reduction) < 0.01
    logger.info(f"LLM reduction: {llm_reduction:.1f}% (expected: {expected_reduction:.1f}%)")
    
    logger.info("✓ LLM reduction calculation test passed")


def test_periodic_logging():
    """Test periodic logging every 10 queries"""
    logger.info("\n=== Testing Periodic Logging ===")
    
    tracker = MetricsTracker(log_interval=10)
    
    logger.info("Recording 25 queries (should log at 10, 20)...")
    
    for i in range(25):
        # Mix of query types
        if i % 3 == 0:
            tracker.record_query(used_fast_path=True, cache_hit=False, used_llm=False)
        elif i % 3 == 1:
            tracker.record_query(used_fast_path=False, cache_hit=True, used_llm=False)
        else:
            tracker.record_query(used_fast_path=False, cache_hit=False, used_llm=True)
    
    logger.info("✓ Periodic logging test passed")


def test_metrics_summary():
    """Test getting metrics summary"""
    logger.info("\n=== Testing Metrics Summary ===")
    
    tracker = MetricsTracker(log_interval=100)
    
    # Record some queries
    tracker.record_query(used_fast_path=True, cache_hit=False, used_llm=False)
    tracker.record_query(used_fast_path=False, cache_hit=True, used_llm=False)
    tracker.record_query(used_fast_path=False, cache_hit=False, used_llm=True)
    
    summary = tracker.get_metrics_summary()
    
    assert summary["total_queries"] == 3
    assert summary["fast_path_queries"] == 1
    assert summary["cache_hits"] == 1
    assert summary["cache_misses"] == 2
    assert summary["llm_calls"] == 1
    assert "cache_hit_rate" in summary
    assert "llm_reduction_rate" in summary
    
    logger.info(f"Metrics summary: {summary}")
    logger.info("✓ Metrics summary test passed")


def test_snapshot():
    """Test getting metrics snapshot"""
    logger.info("\n=== Testing Metrics Snapshot ===")
    
    tracker = MetricsTracker(log_interval=100)
    
    # Record some queries
    tracker.record_query(used_fast_path=True, cache_hit=False, used_llm=False)
    tracker.record_query(used_fast_path=False, cache_hit=True, used_llm=False)
    
    snapshot = tracker.get_snapshot()
    
    assert snapshot.total_queries == 2
    assert snapshot.fast_path_queries == 1
    assert snapshot.cache_hits == 1
    assert snapshot.timestamp is not None
    
    logger.info(f"Snapshot: {snapshot}")
    logger.info("✓ Snapshot test passed")


def test_reset():
    """Test resetting metrics"""
    logger.info("\n=== Testing Reset ===")
    
    tracker = MetricsTracker(log_interval=100)
    
    # Record some queries
    tracker.record_query(used_fast_path=True, cache_hit=False, used_llm=False)
    tracker.record_query(used_fast_path=False, cache_hit=True, used_llm=False)
    
    assert tracker.total_queries == 2
    
    # Reset
    tracker.reset()
    
    assert tracker.total_queries == 0
    assert tracker.fast_path_queries == 0
    assert tracker.cache_hits == 0
    assert tracker.cache_misses == 0
    assert tracker.llm_calls == 0
    
    logger.info("✓ Reset test passed")


def test_85_percent_target():
    """Test achieving 85% LLM reduction target"""
    logger.info("\n=== Testing 85% LLM Reduction Target ===")
    
    tracker = MetricsTracker(log_interval=100)
    
    # Record 100 queries with 85% reduction
    # 50 fast path + 35 cache hits + 15 LLM = 85% reduction
    
    for _ in range(50):
        tracker.record_query(used_fast_path=True, cache_hit=False, used_llm=False)
    
    for _ in range(35):
        tracker.record_query(used_fast_path=False, cache_hit=True, used_llm=False)
    
    for _ in range(15):
        tracker.record_query(used_fast_path=False, cache_hit=False, used_llm=True)
    
    llm_reduction = tracker.get_llm_reduction()
    
    assert llm_reduction >= 85.0
    logger.info(f"LLM reduction: {llm_reduction:.1f}% (target: 85%)")
    logger.info("✓ 85% target achieved!")
    
    # Trigger logging to see the success message
    tracker.log_metrics()
    
    logger.info("✓ 85% LLM reduction target test passed")


def main():
    """Run all tests"""
    try:
        test_initialization()
        test_fast_path_query()
        test_cache_hit_query()
        test_llm_query()
        test_cache_hit_rate_calculation()
        test_llm_reduction_calculation()
        test_periodic_logging()
        test_metrics_summary()
        test_snapshot()
        test_reset()
        test_85_percent_target()
        
        logger.info("\n=== All Tests Passed ===")
        logger.info("Metrics tracker verified successfully!")
        
    except AssertionError as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Test error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
