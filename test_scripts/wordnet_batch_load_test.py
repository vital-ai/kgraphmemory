#!/usr/bin/env python3
"""
WordNet Batch Load Test Script

This script loads the large WordNet N-Triples file into KGraphRDFDB using
optimized bulk loading, then performs various SPARQL queries to test the data.

Based on inspection of the data structure, the WordNet file contains:
- KGFrame entities with WordNet hyponym relationships
- KGEntitySlot entities for source/destination slots
- Edge_hasKGSlot entities connecting frames to slots
- KGEntity entities representing WordNet concepts

The script demonstrates both batch loading and direct bulk loading approaches.
"""

import sys
import os
import time
from typing import Dict, Any, List

# Add the parent directory to the path so we can import kgraphmemory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kgraphmemory.kgraph_rdf_db import KGraphRDFDB


def progress_callback(processed: int, total: int, line_num: int):
    """Progress callback for batch loading"""
    if total > 0:
        percentage = (processed / total) * 100
        print(f"Progress: {processed:,}/{total:,} lines ({percentage:.1f}%) - Line {line_num:,}")
    else:
        print(f"Processed: {processed:,} lines - Line {line_num:,}")


def test_bulk_load_performance(db: KGraphRDFDB, file_path: str):
    """Test the direct bulk_load method for maximum performance"""
    print("\n" + "="*60)
    print("TESTING DIRECT BULK LOAD (Maximum Performance)")
    print("="*60)
    
    start_time = time.time()
    
    # Use the direct bulk_load method for maximum performance
    success = db.bulk_load_file(file_path, format="ntriples")
    
    end_time = time.time()
    load_time = end_time - start_time
    
    if success:
        triple_count = db.count_triples()
        print(f"✅ Bulk load completed successfully!")
        print(f"⏱️  Load time: {load_time:.2f} seconds")
        print(f"📊 Total triples loaded: {triple_count:,}")
        if triple_count > 0:
            print(f"🚀 Loading rate: {triple_count/load_time:,.0f} triples/second")
    else:
        print("❌ Bulk load failed!")
    
    return success


def test_batch_load_with_progress(db: KGraphRDFDB, file_path: str):
    """Test the batch loading method with progress reporting"""
    print("\n" + "="*60)
    print("TESTING BATCH LOAD WITH PROGRESS")
    print("="*60)
    
    start_time = time.time()
    
    # Use batch loading with progress reporting
    success = db.load_from_file_batch(
        file_path, 
        format="ntriples", 
        batch_size=50000,  # 50k lines per batch
        progress_callback=progress_callback
    )
    
    end_time = time.time()
    load_time = end_time - start_time
    
    if success:
        triple_count = db.count_triples()
        print(f"✅ Batch load completed successfully!")
        print(f"⏱️  Load time: {load_time:.2f} seconds")
        print(f"📊 Total triples loaded: {triple_count:,}")
        if triple_count > 0:
            print(f"🚀 Loading rate: {triple_count/load_time:,.0f} triples/second")
    else:
        print("❌ Batch load failed!")
    
    return success


def run_sparql_queries(db: KGraphRDFDB):
    """Run various SPARQL queries to test the loaded WordNet data"""
    print("\n" + "="*60)
    print("RUNNING SPARQL QUERIES ON WORDNET DATA")
    print("="*60)
    
    queries = [
        {
            "name": "Count all triples",
            "query": """
                SELECT (COUNT(*) AS ?count)
                WHERE {
                    ?s ?p ?o .
                }
            """,
            "description": "Get total number of triples in the store"
        },
        
        {
            "name": "Count KGFrame entities",
            "query": """
                PREFIX haley-ai-kg: <http://vital.ai/ontology/haley-ai-kg#>
                SELECT (COUNT(?frame) AS ?count)
                WHERE {
                    ?frame a haley-ai-kg:KGFrame .
                }
            """,
            "description": "Count all KGFrame entities (WordNet relationship frames)"
        },
        
        {
            "name": "Count WordNet Hyponym frames",
            "query": """
                PREFIX haley-ai-kg: <http://vital.ai/ontology/haley-ai-kg#>
                SELECT (COUNT(?frame) AS ?count)
                WHERE {
                    ?frame a haley-ai-kg:KGFrame .
                    ?frame haley-ai-kg:hasKGFrameType <urn:Edge_WordnetHyponym> .
                }
            """,
            "description": "Count frames specifically for WordNet hyponym relationships"
        },
        
        {
            "name": "Sample KGFrame details",
            "query": """
                PREFIX haley-ai-kg: <http://vital.ai/ontology/haley-ai-kg#>
                PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
                SELECT ?frame ?frameType ?frameDescription
                WHERE {
                    ?frame a haley-ai-kg:KGFrame .
                    ?frame haley-ai-kg:hasKGFrameType ?frameType .
                    OPTIONAL { ?frame haley-ai-kg:hasKGFrameTypeDescription ?frameDescription }
                }
                LIMIT 5
            """,
            "description": "Get sample KGFrame details"
        },
        
        {
            "name": "Count KGEntitySlot entities",
            "query": """
                PREFIX haley-ai-kg: <http://vital.ai/ontology/haley-ai-kg#>
                SELECT (COUNT(?slot) AS ?count)
                WHERE {
                    ?slot a haley-ai-kg:KGEntitySlot .
                }
            """,
            "description": "Count all KGEntitySlot entities"
        },
        
        {
            "name": "Count source vs destination slots",
            "query": """
                PREFIX haley-ai-kg: <http://vital.ai/ontology/haley-ai-kg#>
                SELECT ?slotType (COUNT(?slot) AS ?count)
                WHERE {
                    ?slot a haley-ai-kg:KGEntitySlot .
                    ?slot haley-ai-kg:hasKGSlotType ?slotType .
                }
                GROUP BY ?slotType
            """,
            "description": "Count source vs destination entity slots"
        },
        
        {
            "name": "Sample entity slot connections",
            "query": """
                PREFIX haley-ai-kg: <http://vital.ai/ontology/haley-ai-kg#>
                PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
                SELECT ?frame ?slot ?slotType ?entity
                WHERE {
                    ?frame a haley-ai-kg:KGFrame .
                    ?edge a haley-ai-kg:Edge_hasKGSlot .
                    ?edge vital-core:hasEdgeSource ?frame .
                    ?edge vital-core:hasEdgeDestination ?slot .
                    ?slot a haley-ai-kg:KGEntitySlot .
                    ?slot haley-ai-kg:hasKGSlotType ?slotType .
                    ?slot haley-ai-kg:hasEntitySlotValue ?entity .
                }
                LIMIT 10
            """,
            "description": "Sample connections between frames, slots, and entities"
        },
        
        {
            "name": "Find complete hyponym relationships",
            "query": """
                PREFIX haley-ai-kg: <http://vital.ai/ontology/haley-ai-kg#>
                PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
                
                CONSTRUCT {
                    ?sourceEntity <urn:hyponymOf> ?destEntity .
                    ?frame <urn:connectsEntities> ?sourceEntity .
                    ?frame <urn:connectsEntities> ?destEntity .
                }
                WHERE {
                    # Find frames for WordNet hyponym relationships
                    ?frame a haley-ai-kg:KGFrame .
                    ?frame haley-ai-kg:hasKGFrameType <urn:Edge_WordnetHyponym> .
                    
                    # Find source entity slot
                    ?sourceEdge a haley-ai-kg:Edge_hasKGSlot .
                    ?sourceEdge vital-core:hasEdgeSource ?frame .
                    ?sourceEdge vital-core:hasEdgeDestination ?sourceSlot .
                    ?sourceSlot a haley-ai-kg:KGEntitySlot .
                    ?sourceSlot haley-ai-kg:hasKGSlotType <urn:hasSourceEntity> .
                    ?sourceSlot haley-ai-kg:hasEntitySlotValue ?sourceEntity .
                    
                    # Find destination entity slot
                    ?destEdge a haley-ai-kg:Edge_hasKGSlot .
                    ?destEdge vital-core:hasEdgeSource ?frame .
                    ?destEdge vital-core:hasEdgeDestination ?destSlot .
                    ?destSlot a haley-ai-kg:KGEntitySlot .
                    ?destSlot haley-ai-kg:hasKGSlotType <urn:hasDestinationEntity> .
                    ?destSlot haley-ai-kg:hasEntitySlotValue ?destEntity .
                }
                LIMIT 10
            """,
            "description": "Construct complete hyponym relationships from the frame structure"
        },
        
        {
            "name": "Count unique entities",
            "query": """
                PREFIX haley-ai-kg: <http://vital.ai/ontology/haley-ai-kg#>
                SELECT (COUNT(DISTINCT ?entity) AS ?count)
                WHERE {
                    ?slot a haley-ai-kg:KGEntitySlot .
                    ?slot haley-ai-kg:hasEntitySlotValue ?entity .
                }
            """,
            "description": "Count unique entities referenced in slots"
        },
        
        {
            "name": "Sample entity URIs",
            "query": """
                PREFIX haley-ai-kg: <http://vital.ai/ontology/haley-ai-kg#>
                SELECT DISTINCT ?entity
                WHERE {
                    ?slot a haley-ai-kg:KGEntitySlot .
                    ?slot haley-ai-kg:hasEntitySlotValue ?entity .
                    FILTER(CONTAINS(STR(?entity), "KGEntity"))
                }
                LIMIT 10
            """,
            "description": "Sample entity URIs to understand naming pattern"
        }
    ]
    
    for i, query_info in enumerate(queries, 1):
        print(f"\n{i}. {query_info['name']}")
        print(f"   Description: {query_info['description']}")
        print("   " + "-" * 50)
        
        start_time = time.time()
        
        try:
            if "CONSTRUCT" in query_info['query'].upper():
                # Handle CONSTRUCT queries
                results = db.sparql_construct(query_info['query'])
                end_time = time.time()
                query_time = end_time - start_time
                
                print(f"   ✅ Query executed in {query_time:.3f}s")
                print(f"   📊 Constructed {len(results)} triples:")
                
                for j, triple in enumerate(results[:5]):  # Show first 5 results
                    s, p, o = triple
                    print(f"      {j+1}. {s} {p} {o}")
                
                if len(results) > 5:
                    print(f"      ... and {len(results) - 5} more triples")
                    
            else:
                # Handle SELECT queries
                results = db.sparql_query(query_info['query'])
                end_time = time.time()
                query_time = end_time - start_time
                
                print(f"   ✅ Query executed in {query_time:.3f}s")
                print(f"   📊 Results ({len(results)} rows):")
                
                for j, result in enumerate(results[:10]):  # Show first 10 results
                    if isinstance(result, dict):
                        formatted_result = ", ".join([f"{k}: {v}" for k, v in result.items()])
                        print(f"      {j+1}. {formatted_result}")
                    else:
                        print(f"      {j+1}. {result}")
                
                if len(results) > 10:
                    print(f"      ... and {len(results) - 10} more results")
                    
        except Exception as e:
            end_time = time.time()
            query_time = end_time - start_time
            print(f"   ❌ Query failed after {query_time:.3f}s: {e}")


def main():
    """Main test function"""
    print("🔬 WordNet Batch Load Test Script")
    print("=" * 60)
    
    # File path to the WordNet data
    file_path = "/Users/hadfield/Local/vital-git/kgraphmemory/test_data/kgframe-wordnet-0.0.2.nt"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: WordNet file not found at {file_path}")
        return
    
    # Get file size for reference
    file_size = os.path.getsize(file_path)
    print(f"📁 File: {file_path}")
    print(f"📏 File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    
    # Create KGraphRDFDB instance
    print(f"\n🏗️  Creating KGraphRDFDB instance...")
    db = KGraphRDFDB("wordnet_test_db")
    
    # Test approach 1: Direct bulk load (fastest)
    print(f"\n🚀 Testing direct bulk load approach...")
    success = test_bulk_load_performance(db, file_path)
    
    if success:
        # Run SPARQL queries on the loaded data
        run_sparql_queries(db)
        
        # Clear the database for the next test
        print(f"\n🧹 Clearing database for batch load test...")
        db.clear()
        
        # Test approach 2: Batch load with progress (more controlled)
        print(f"\n📊 Testing batch load with progress reporting...")
        success2 = test_batch_load_with_progress(db, file_path)
        
        if success2:
            print(f"\n✅ Both loading methods completed successfully!")
            
            # Quick verification query
            count_result = db.sparql_query("SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o . }")
            if count_result:
                final_count = count_result[0].get('count', 0)
                print(f"📊 Final triple count: {final_count:,}")
        else:
            print(f"\n⚠️  Batch load method failed, but bulk load succeeded")
    else:
        print(f"\n❌ Both loading methods failed!")
    
    print(f"\n🏁 Test completed!")


if __name__ == "__main__":
    main()
