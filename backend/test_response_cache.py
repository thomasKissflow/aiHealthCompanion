"""
Test Response Cache
"""
from response_cache import ResponseCache
import time
import logging

logging.basicConfig(level=logging.INFO)

def test_response_cache():
    """Test response cache functionality"""
    cache = ResponseCache(max_size=5, ttl_hours=24)
    
    print("=" * 60)
    print("RESPONSE CACHE TEST")
    print("=" * 60)
    print()
    
    # Test 1: Basic put and get
    print("Test 1: Basic put and get")
    cache.put("What causes headaches?", "Headaches can be caused by...")
    result = cache.get("What causes headaches?")
    assert result == "Headaches can be caused by...", "Basic get failed"
    print("✓ Basic put/get works")
    print()
    
    # Test 2: Cache hit
    print("Test 2: Cache hit")
    result = cache.get("What causes headaches?")
    assert result == "Headaches can be caused by...", "Cache hit failed"
    assert cache.hits == 2, f"Expected 2 hits, got {cache.hits}"
    print(f"✓ Cache hit works (hits: {cache.hits})")
    print()
    
    # Test 3: Cache miss
    print("Test 3: Cache miss")
    result = cache.get("What causes migraines?")
    assert result is None, "Cache miss should return None"
    assert cache.misses == 1, f"Expected 1 miss, got {cache.misses}"
    print(f"✓ Cache miss works (misses: {cache.misses})")
    print()
    
    # Test 4: Key normalization
    print("Test 4: Key normalization")
    cache.put("What causes HEADACHES?", "Response 1")
    result = cache.get("what causes headaches")  # Different case
    assert result == "Response 1", "Key normalization failed"
    print("✓ Key normalization works (case-insensitive)")
    print()
    
    # Test 5: LRU eviction
    print("Test 5: LRU eviction (max_size=5)")
    cache.clear()
    for i in range(6):
        cache.put(f"Query {i}", f"Response {i}")
    
    # First entry should be evicted
    result = cache.get("Query 0")
    assert result is None, "LRU eviction failed - Query 0 should be evicted"
    
    # Last entry should still be there
    result = cache.get("Query 5")
    assert result == "Response 5", "LRU eviction failed - Query 5 should exist"
    
    print(f"✓ LRU eviction works (cache size: {len(cache.cache)})")
    print()
    
    # Test 6: Hit rate calculation
    print("Test 6: Hit rate calculation")
    cache.clear()
    cache.put("Q1", "R1")
    cache.get("Q1")  # Hit
    cache.get("Q1")  # Hit
    cache.get("Q2")  # Miss
    
    hit_rate = cache.get_hit_rate()
    expected_rate = (2 / 3) * 100  # 2 hits, 1 miss
    assert abs(hit_rate - expected_rate) < 0.1, f"Hit rate calculation failed: {hit_rate}"
    print(f"✓ Hit rate: {hit_rate:.1f}% (2 hits, 1 miss)")
    print()
    
    # Test 7: Cache stats
    print("Test 7: Cache stats")
    stats = cache.get_stats()
    print(f"  Size: {stats['size']}/{stats['max_size']}")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit rate: {stats['hit_rate']:.1f}%")
    print(f"  TTL: {stats['ttl_hours']}h")
    print("✓ Cache stats work")
    print()
    
    # Test 8: Context in cache key
    print("Test 8: Context in cache key")
    cache.clear()
    cache.put("Hello", "Response 1", context={"user": "thomas"})
    cache.put("Hello", "Response 2", context={"user": "tana"})
    
    result1 = cache.get("Hello", context={"user": "thomas"})
    result2 = cache.get("Hello", context={"user": "tana"})
    
    assert result1 == "Response 1", "Context-based caching failed"
    assert result2 == "Response 2", "Context-based caching failed"
    print("✓ Context-based caching works")
    print()
    
    print("=" * 60)
    cache.log_stats()
    print("=" * 60)
    print("✓ All cache tests passed")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_response_cache()
    exit(0 if success else 1)
