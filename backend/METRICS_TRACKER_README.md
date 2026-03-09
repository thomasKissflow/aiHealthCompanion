# Metrics Tracker Implementation

## Overview

The Metrics Tracker monitors LLM usage optimization effectiveness by tracking fast path usage, cache hits/misses, and calculating LLM reduction rates. It provides real-time visibility into system performance and optimization success.

## Implementation Details

### File: `backend/metrics_tracker.py`

**Key Features:**
- Tracks total queries, fast path queries, cache hits/misses, and LLM calls
- Calculates cache hit rate percentage
- Calculates LLM usage reduction percentage
- Logs metrics every 10 queries (configurable)
- Provides metrics snapshots for monitoring
- Validates 85% LLM reduction target achievement

## Metrics Tracked

### Core Metrics
1. **Total Queries**: All user queries received by the system
2. **Fast Path Queries**: Queries served without LLM (greetings, acknowledgments, risk symptoms)
3. **Cache Hits**: Queries served from response cache
4. **Cache Misses**: Queries requiring new processing
5. **LLM Calls**: Number of times LLM was invoked

### Calculated Metrics
1. **Cache Hit Rate**: `(cache_hits / (cache_hits + cache_misses)) * 100`
2. **LLM Reduction Rate**: `((fast_path_queries + cache_hits) / total_queries) * 100`

## Usage

### Basic Usage

```python
from metrics_tracker import MetricsTracker

# Initialize tracker (logs every 10 queries by default)
tracker = MetricsTracker(log_interval=10)

# Record a fast path query (greeting)
tracker.record_query(
    used_fast_path=True,
    cache_hit=False,
    used_llm=False
)

# Record a cache hit query
tracker.record_query(
    used_fast_path=False,
    cache_hit=True,
    used_llm=False
)

# Record an LLM query (cache miss)
tracker.record_query(
    used_fast_path=False,
    cache_hit=False,
    used_llm=True
)

# Get current metrics
summary = tracker.get_metrics_summary()
print(f"LLM Reduction: {summary['llm_reduction_rate']:.1f}%")
```

### Integration with Supervisor Agent

```python
# In supervisor_agent.py
class SupervisorAgent:
    def __init__(self, ..., metrics_tracker: MetricsTracker):
        self.metrics = metrics_tracker
    
    async def process_query(self, text: str, session: Session) -> str:
        intent, confidence = self.intent_classifier.classify(text)
        
        # Track metrics based on query type
        if intent in [Intent.GREETING, Intent.ACKNOWLEDGMENT, Intent.RISK_SYMPTOM]:
            # Fast path - no LLM
            response = self._handle_fast_path(intent, text)
            self.metrics.record_query(
                used_fast_path=True,
                cache_hit=False,
                used_llm=False
            )
        else:
            # Check cache first
            cached = self.cache.get(text)
            if cached:
                self.metrics.record_query(
                    used_fast_path=False,
                    cache_hit=True,
                    used_llm=False
                )
                return cached
            
            # Use LLM
            response = await self._generate_llm_response(...)
            self.metrics.record_query(
                used_fast_path=False,
                cache_hit=False,
                used_llm=True
            )
        
        return response
```

## Metrics Logging

### Automatic Logging
Metrics are automatically logged every 10 queries (configurable):

```
[Metrics] Query #10 - Fast Path: 7, Cache Hits: 2, Cache Misses: 8, LLM Calls: 1
[Metrics] Cache Hit Rate: 20.0%, LLM Reduction: 90.0%
[Metrics] ✓ Target 85% LLM reduction achieved!
```

### Manual Logging
Force metrics logging at any time:

```python
tracker.log_metrics()
```

## Performance Targets

### 85% LLM Reduction Target
The system targets 85% LLM usage reduction through:
- **Fast Path**: ~50% of queries (greetings, acknowledgments, risk symptoms)
- **Cache Hits**: ~35% of queries (repeat or similar queries)
- **LLM Calls**: ~15% of queries (novel complex queries)

When the target is achieved, the tracker logs:
```
[Metrics] ✓ Target 85% LLM reduction achieved!
```

When below target (after 20+ queries):
```
[Metrics] Target 85% LLM reduction not yet achieved (current: 70.0%)
```

## API Reference

### `MetricsTracker(log_interval=10)`
Initialize metrics tracker.

**Parameters:**
- `log_interval` (int): Number of queries between automatic logs (default: 10)

### `record_query(used_fast_path, cache_hit, used_llm)`
Record metrics for a single query.

**Parameters:**
- `used_fast_path` (bool): True if query used fast path (no LLM)
- `cache_hit` (bool): True if response was from cache
- `used_llm` (bool): True if LLM was invoked

### `get_cache_hit_rate() -> float`
Calculate cache hit rate percentage (0-100).

### `get_llm_reduction() -> float`
Calculate LLM usage reduction percentage (0-100).

### `log_metrics()`
Manually log current metrics to terminal.

### `get_metrics_summary() -> dict`
Get all metrics as a dictionary.

**Returns:**
```python
{
    "total_queries": 100,
    "fast_path_queries": 50,
    "cache_hits": 35,
    "cache_misses": 65,
    "llm_calls": 15,
    "cache_hit_rate": 35.0,
    "llm_reduction_rate": 85.0
}
```

### `get_snapshot() -> MetricsSnapshot`
Get a timestamped snapshot of current metrics.

### `reset()`
Reset all metrics to zero.

## Requirements Satisfied

- **19.1**: Tracks total number of user queries
- **19.2**: Tracks queries served via fast path
- **19.3**: Tracks queries served via response cache
- **19.4**: Tracks queries requiring LLM calls
- **19.5**: Calculates and logs cache hit rate percentage
- **19.6**: Calculates and logs LLM usage reduction percentage
- **19.7**: Logs optimization metrics every 10 queries

## Testing

### Test File: `backend/test_metrics_tracker.py`

**Test Coverage:**
- Initialization
- Fast path query recording
- Cache hit query recording
- LLM query recording
- Cache hit rate calculation
- LLM reduction calculation
- Periodic logging (every 10 queries)
- Metrics summary generation
- Snapshot creation
- Metrics reset
- 85% LLM reduction target validation

**Run Tests:**
```bash
cd backend
python test_metrics_tracker.py
```

**Expected Output:**
```
=== All Tests Passed ===
Metrics tracker verified successfully!
```

## Example Metrics Flow

### Demo Script Execution
```
Query 1: "Hello"
  → Fast path (greeting)
  → Metrics: Fast Path: 1, LLM Calls: 0

Query 2: "I have a headache"
  → LLM (first time)
  → Metrics: Fast Path: 1, LLM Calls: 1

Query 3: "I have a headache"
  → Cache hit (same query)
  → Metrics: Fast Path: 1, Cache Hits: 1, LLM Calls: 1

Query 10: "chest pain"
  → Fast path (risk symptom)
  → [Metrics] Query #10 - Fast Path: 5, Cache Hits: 3, Cache Misses: 7, LLM Calls: 2
  → [Metrics] Cache Hit Rate: 30.0%, LLM Reduction: 80.0%
```

## Integration Points

The Metrics Tracker integrates with:
- **Supervisor Agent**: Records metrics for each query
- **Response Cache**: Tracks cache hits/misses
- **Intent Classifier**: Identifies fast path queries
- **LLM Client**: Tracks LLM invocations
- **Main Application**: Provides performance monitoring

## Performance Impact

- **Memory**: Minimal (~100 bytes for counters)
- **CPU**: Negligible (<1ms per query)
- **Logging**: Only every 10 queries to avoid spam

## Next Steps

The Metrics Tracker is ready for:
1. Integration with Supervisor Agent
2. Integration with main FastAPI application
3. Dashboard visualization (future enhancement)
4. Prometheus/Grafana export (future enhancement)
