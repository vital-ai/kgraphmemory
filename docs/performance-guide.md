# Performance Guide

## Overview

This guide provides recommendations for optimizing KGraphMemory performance in AI agent applications. The system is designed for <1M records with efficient in-memory operations, but proper configuration and usage patterns are essential for optimal performance.

## System Architecture Performance

### Memory Architecture

KGraphMemory uses a dual-store architecture that affects performance characteristics:

- **RDF Store (pyoxigraph)**: Optimized for SPARQL queries and relationship traversal
- **Vector Store (Qdrant)**: Optimized for similarity search and embedding operations
- **Synchronization**: Automatic sync between stores adds overhead but ensures consistency

### Performance Targets

- **Scale**: <1M records per knowledge graph
- **RDF Loading**: 500K+ triples/second (bulk operations)
- **SPARQL Queries**: 0.1-0.8 seconds for complex queries
- **Vector Search**: Sub-millisecond similarity search
- **Memory Usage**: ~1-2GB for 100K entities with multi-vector support

## Optimization Strategies

### Data Loading Optimization

#### Bulk Loading for Large Datasets

```python
# Use bulk loading for initial data import
def bulk_load_entities(graph, entities):
    """Efficiently load large numbers of entities"""
    
    # Batch entities for bulk operations
    batch_size = 1000
    for i in range(0, len(entities), batch_size):
        batch = entities[i:i + batch_size]
        
        # Use batch operations where available
        for entity in batch:
            graph.add_object(entity)
```

#### RDF File Import

```python
# For large RDF files, use direct file loading
def load_rdf_data(graph, file_path):
    """Load RDF data efficiently"""
    
    # Use bulk_load_file for large datasets
    rdf_db = graph.get_rdf_db()
    rdf_db.bulk_load_file(file_path, format="turtle")
    
    # Note: This bypasses vector generation
    # You may need to regenerate vectors separately
```

### Query Optimization

#### SPARQL Query Performance

```python
# Optimize SPARQL queries for better performance

# BAD: Unfiltered queries
bad_query = """
SELECT ?entity ?name ?description WHERE {
    ?entity a kg:KGEntity ;
            vital-core:hasName ?name ;
            kg:hasKGEntityDescription ?description .
}
"""

# GOOD: Filtered and limited queries
good_query = """
SELECT ?entity ?name ?description WHERE {
    ?entity a kg:KGEntity ;
            vital-core:hasName ?name ;
            kg:hasKGEntityDescription ?description .
    FILTER(STRLEN(?name) > 3)
}
ORDER BY ?name
LIMIT 100
"""
```

#### Vector Search Optimization

```python
# Optimize vector searches

# Use specific vector types for targeted search
def optimized_search(graph, query, search_type="general"):
    """Perform optimized vector search"""
    
    # Use type-specific search when possible
    if search_type == "type":
        return graph.vector_search_by_type(query, "type", limit=10)
    elif search_type == "content":
        return graph.vector_search_by_type(query, "content", limit=10)
    else:
        return graph.vector_search(query, limit=10)

# Use metadata filters to reduce search space
def filtered_search(graph, query, entity_type=None):
    """Search with metadata filtering"""
    
    filters = {}
    if entity_type:
        filters['entity_type'] = entity_type
    
    return graph.vector_search(query, filters=filters, limit=10)
```

### Memory Management

#### Vector Configuration

```python
# Optimize vector mappings for performance

# BAD: Too many vector types
excessive_mappings = {
    "KGEntity": {
        "type": ["hasKGEntityType"],
        "description": ["hasKGEntityDescription"],
        "content": ["hasKGEntityContent"],
        "summary": ["hasKGEntitySummary"],
        "details": ["hasKGEntityDetails"],
        "metadata": ["hasKGEntityMetadata"],
        "general": ["hasName", "hasKGEntityDescription"]
    }
}

# GOOD: Essential vector types only
optimized_mappings = {
    "KGEntity": {
        "type": ["hasKGEntityType"],
        "description": ["hasKGEntityDescription"],
        "general": ["hasName", "hasKGEntityDescription"]
    }
}
```

#### Memory Monitoring

```python
class PerformanceMonitor:
    def __init__(self, graph):
        self.graph = graph
        
    def get_memory_stats(self):
        """Get current memory usage statistics"""
        stats = self.graph.get_statistics()
        
        return {
            'total_objects': stats.get('total_objects', 0),
            'rdf_triples': stats.get('rdf_triple_count', 0),
            'vector_count': stats.get('vector_count', 0),
            'vectors_by_type': stats.get('vectors_by_type', {}),
            'estimated_memory_mb': self.estimate_memory_usage(stats)
        }
    
    def estimate_memory_usage(self, stats):
        """Estimate memory usage in MB"""
        # Rough estimates
        rdf_memory = stats.get('rdf_triple_count', 0) * 100  # bytes per triple
        vector_memory = stats.get('vector_count', 0) * 1536  # bytes per vector (384 dim * 4 bytes)
        
        total_bytes = rdf_memory + vector_memory
        return total_bytes / (1024 * 1024)  # Convert to MB
    
    def check_memory_limits(self, max_objects=100000, max_memory_mb=1000):
        """Check if memory limits are exceeded"""
        stats = self.get_memory_stats()
        
        warnings = []
        if stats['total_objects'] > max_objects:
            warnings.append(f"Object count ({stats['total_objects']}) exceeds limit ({max_objects})")
        
        if stats['estimated_memory_mb'] > max_memory_mb:
            warnings.append(f"Memory usage ({stats['estimated_memory_mb']:.1f}MB) exceeds limit ({max_memory_mb}MB)")
        
        return warnings
```

### Caching Strategies

#### Query Result Caching

```python
import time
from functools import lru_cache

class CachedKGraph:
    def __init__(self, graph):
        self.graph = graph
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def cached_vector_search(self, query, vector_id="general", limit=10):
        """Vector search with caching"""
        cache_key = f"vector_{hash(query)}_{vector_id}_{limit}"
        
        # Check cache
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return result
        
        # Perform search
        result = self.graph.vector_search(query, vector_id=vector_id, limit=limit)
        
        # Cache result
        self.cache[cache_key] = (result, time.time())
        
        return result
    
    @lru_cache(maxsize=100)
    def cached_sparql_query(self, query):
        """SPARQL query with LRU caching"""
        return self.graph.sparql_query(query)
    
    def clear_cache(self):
        """Clear all cached results"""
        self.cache.clear()
        self.cached_sparql_query.cache_clear()
```

#### Embedding Caching

```python
class EmbeddingCache:
    def __init__(self, embedding_model, max_cache_size=10000):
        self.embedding_model = embedding_model
        self.cache = {}
        self.max_cache_size = max_cache_size
    
    def get_embedding(self, text):
        """Get embedding with caching"""
        text_hash = hash(text)
        
        if text_hash in self.cache:
            return self.cache[text_hash]
        
        # Generate embedding
        embedding = self.embedding_model.encode(text)
        
        # Cache with size limit
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[text_hash] = embedding
        return embedding
```

## Performance Monitoring

### Benchmarking Tools

```python
import time
import statistics

class PerformanceBenchmark:
    def __init__(self, graph):
        self.graph = graph
        self.results = {}
    
    def benchmark_vector_search(self, queries, iterations=10):
        """Benchmark vector search performance"""
        times = []
        
        for _ in range(iterations):
            for query in queries:
                start_time = time.time()
                results = self.graph.vector_search(query, limit=10)
                end_time = time.time()
                times.append(end_time - start_time)
        
        self.results['vector_search'] = {
            'mean_time': statistics.mean(times),
            'median_time': statistics.median(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0
        }
        
        return self.results['vector_search']
    
    def benchmark_sparql_queries(self, queries, iterations=5):
        """Benchmark SPARQL query performance"""
        times = []
        
        for _ in range(iterations):
            for query in queries:
                start_time = time.time()
                results = self.graph.sparql_query(query)
                end_time = time.time()
                times.append(end_time - start_time)
        
        self.results['sparql_queries'] = {
            'mean_time': statistics.mean(times),
            'median_time': statistics.median(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0
        }
        
        return self.results['sparql_queries']
    
    def benchmark_add_operations(self, objects, batch_size=100):
        """Benchmark object addition performance"""
        times = []
        
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            
            start_time = time.time()
            for obj in batch:
                self.graph.add_object(obj)
            end_time = time.time()
            
            batch_time = end_time - start_time
            times.append(batch_time / len(batch))  # Time per object
        
        self.results['add_operations'] = {
            'mean_time_per_object': statistics.mean(times),
            'objects_per_second': 1.0 / statistics.mean(times),
            'total_objects': len(objects)
        }
        
        return self.results['add_operations']
```

### Real-time Monitoring

```python
class RealTimeMonitor:
    def __init__(self, graph, monitoring_interval=60):
        self.graph = graph
        self.monitoring_interval = monitoring_interval
        self.metrics_history = []
        self.running = False
    
    def start_monitoring(self):
        """Start real-time performance monitoring"""
        self.running = True
        
        while self.running:
            metrics = self.collect_metrics()
            self.metrics_history.append(metrics)
            
            # Keep only last 100 measurements
            if len(self.metrics_history) > 100:
                self.metrics_history.pop(0)
            
            # Check for performance issues
            self.check_performance_alerts(metrics)
            
            time.sleep(self.monitoring_interval)
    
    def collect_metrics(self):
        """Collect current performance metrics"""
        stats = self.graph.get_statistics()
        
        return {
            'timestamp': time.time(),
            'total_objects': stats.get('total_objects', 0),
            'rdf_triples': stats.get('rdf_triple_count', 0),
            'vector_count': stats.get('vector_count', 0),
            'memory_usage_mb': self.estimate_memory_usage(stats)
        }
    
    def check_performance_alerts(self, metrics):
        """Check for performance issues and alert"""
        alerts = []
        
        if metrics['memory_usage_mb'] > 1000:  # 1GB threshold
            alerts.append(f"High memory usage: {metrics['memory_usage_mb']:.1f}MB")
        
        if metrics['total_objects'] > 500000:  # 500K objects threshold
            alerts.append(f"High object count: {metrics['total_objects']}")
        
        for alert in alerts:
            print(f"PERFORMANCE ALERT: {alert}")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
    
    def get_performance_trends(self):
        """Analyze performance trends"""
        if len(self.metrics_history) < 2:
            return {}
        
        recent = self.metrics_history[-10:]  # Last 10 measurements
        
        memory_trend = [m['memory_usage_mb'] for m in recent]
        object_trend = [m['total_objects'] for m in recent]
        
        return {
            'memory_growth_rate': (memory_trend[-1] - memory_trend[0]) / len(memory_trend),
            'object_growth_rate': (object_trend[-1] - object_trend[0]) / len(object_trend),
            'current_memory': memory_trend[-1],
            'current_objects': object_trend[-1]
        }
```

## Scaling Strategies

### Horizontal Scaling

```python
class DistributedKGraphMemory:
    def __init__(self, embedding_model, num_shards=4):
        self.embedding_model = embedding_model
        self.num_shards = num_shards
        self.shards = []
        
        # Create multiple KGraphMemory instances
        for i in range(num_shards):
            memory = KGraphMemory(embedding_model)
            self.shards.append(memory)
    
    def get_shard_for_object(self, obj):
        """Determine which shard to use for an object"""
        # Simple hash-based sharding
        obj_hash = hash(str(obj.uri))
        return obj_hash % self.num_shards
    
    def add_object(self, obj):
        """Add object to appropriate shard"""
        shard_index = self.get_shard_for_object(obj)
        shard = self.shards[shard_index]
        
        # Add to a graph in the shard
        graph_id = f"shard_{shard_index}_graph"
        if not shard.has_kgraph(graph_id):
            shard.create_kgraph(graph_id, f"http://example.org/shard/{shard_index}")
        
        graph = shard.get_kgraph(graph_id)
        graph.add_object(obj)
    
    def search_across_shards(self, query, limit=10):
        """Search across all shards"""
        all_results = []
        
        for i, shard in enumerate(self.shards):
            shard_results = shard.search_across_kgraphs(query, limit=limit)
            
            # Add shard information to results
            for result in shard_results:
                result['shard_id'] = i
            
            all_results.extend(shard_results)
        
        # Sort by score and limit
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return all_results[:limit]
```

### Vertical Scaling

```python
class OptimizedKGraphMemory:
    def __init__(self, embedding_model, config=None):
        self.embedding_model = embedding_model
        self.config = config or self.get_default_config()
        self.memory = KGraphMemory(embedding_model)
        
        # Apply optimizations based on config
        self.apply_optimizations()
    
    def get_default_config(self):
        """Get default optimization configuration"""
        return {
            'max_objects_per_graph': 100000,
            'vector_cache_size': 10000,
            'query_cache_ttl': 300,
            'batch_size': 1000,
            'enable_compression': True,
            'optimize_for': 'balanced'  # 'speed', 'memory', 'balanced'
        }
    
    def apply_optimizations(self):
        """Apply optimizations based on configuration"""
        if self.config['optimize_for'] == 'speed':
            # Optimize for speed
            self.config['vector_cache_size'] = 20000
            self.config['query_cache_ttl'] = 600
        elif self.config['optimize_for'] == 'memory':
            # Optimize for memory usage
            self.config['vector_cache_size'] = 5000
            self.config['query_cache_ttl'] = 60
```

## Best Practices Summary

### Do's
1. **Use bulk operations** for large data imports
2. **Limit SPARQL query results** with LIMIT clauses
3. **Use specific vector types** for targeted searches
4. **Monitor memory usage** regularly
5. **Cache frequently used queries**
6. **Use metadata filters** to reduce search space
7. **Batch operations** when possible

### Don'ts
1. **Don't create too many vector types** per object
2. **Don't run unlimited SPARQL queries**
3. **Don't ignore memory limits**
4. **Don't perform individual operations** for large datasets
5. **Don't cache everything** - be selective
6. **Don't ignore performance monitoring**

### Configuration Recommendations

#### Small Scale (< 10K objects)
- Single knowledge graph
- 3-4 vector types maximum
- Basic caching
- Real-time operations

#### Medium Scale (10K - 100K objects)
- Multiple specialized graphs
- Optimized vector mappings
- Query result caching
- Batch operations for bulk updates

#### Large Scale (100K - 1M objects)
- Sharded architecture
- Aggressive caching
- Background processing
- Performance monitoring
- Memory management strategies
