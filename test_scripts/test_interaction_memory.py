#!/usr/bin/env python3
"""
Test script for KGraphInteractionBridge CRUD operations and search functionality.

This script demonstrates:
1. Creating KGraphMemory and KGraphBridge instances
2. CRUD operations on KGInteraction objects via the bridge interface
3. CRUD operations on KGActor and KGAgent objects
4. SPARQL-based search by date range
5. Vector-based similarity search
6. Edge operations for linking actors/agents to interactions

All operations are performed through the bridge interface only.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the parent directory to the path so we can import kgraphmemory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vital_ai_vitalsigns.embedding.embedding_model import EmbeddingModel
from vital_ai_vitalsigns.vitalsigns import VitalSigns

# Import ontology classes
from ai_haley_kg_domain.model.KGInteraction import KGInteraction
from ai_haley_kg_domain.model.KGActor import KGActor
from ai_haley_kg_domain.model.KGAgent import KGAgent

from kgraphmemory.kgraph_memory import KGraphMemory

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_results(title: str, results: List[Dict[str, Any]]):
    """Print formatted results."""
    print(f"\n{title}:")
    if not results:
        print("  No results found.")
        return
    
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result}")

def test_interaction_memory():
    """Test KGraphInteractionBridge functionality."""
    
    print_section("KGraphInteractionBridge Test Script")
    
    vs = VitalSigns()
    
    # Initialize KGraphMemory and create a bridge
    print("\n1. Initializing KGraphMemory and creating bridge...")
    
    # Initialize embedding model
    try:
        embedding_model = EmbeddingModel()
    except Exception as e:
        print(f"Warning: EmbeddingModel initialization issue: {e}")
        print("Continuing with default EmbeddingModel...")
        embedding_model = EmbeddingModel()
    
    memory = KGraphMemory(embedding_model)
    
    bridge = memory.create_kgraph_bridge(
        graph_id="test_interaction_graph",
        graph_uri="http://vital.ai/test/interactions"
    )
    
    print(f"Bridge created with ID: {bridge.get_bridge_id()}")
    print(f"Graph URI: {bridge.get_graph_uri()}")
    
    # ========================================================================
    # TEST CRUD OPERATIONS FOR INTERACTIONS
    # ========================================================================
    
    print_section("Testing KGInteraction CRUD Operations")
    
    # Create interactions using actual KGInteraction instances
    print("\n2. Creating interactions using KGInteraction instances...")
    
    # Create first interaction instance
    interaction1 = KGInteraction()
    interaction1.URI = "http://vital.ai/test/interactions/meeting_001"
    interaction1.name = "Project Planning Meeting"
    interaction1.kGraphDescription = "Planning session for Q1 project goals"
    interaction1.timestamp = int(datetime.now().timestamp() * 1000)  # Unix timestamp in milliseconds
    interaction1.objectUpdateTime = datetime.now().isoformat() + "Z"  # ISO datetime for SPARQL
    
    interaction1_uri = bridge.interactions.create_interaction(
        interaction_instance=interaction1
    )
    print(f"Created interaction 1 (from instance): {interaction1_uri}")
    
    # Create second interaction instance
    interaction2 = KGInteraction()
    interaction2.URI = "http://vital.ai/test/interactions/support_001"
    interaction2.name = "Customer Support Chat"
    interaction2.kGraphDescription = "Helping customer with product issues"
    interaction2.timestamp = int(datetime.now().timestamp() * 1000)  # Unix timestamp in milliseconds
    interaction2.objectUpdateTime = datetime.now().isoformat() + "Z"  # ISO datetime for SPARQL
    
    interaction2_uri = bridge.interactions.create_interaction(
        interaction_instance=interaction2
    )
    print(f"Created interaction 2 (from instance): {interaction2_uri}")
    
    # Create interactions using named parameters
    print("\n3. Creating interactions using named parameters...")
    
    interaction3_uri = bridge.interactions.create_interaction(
        name="Code Review Session",
        interaction_type="http://vital.ai/ontology/haley-ai-kg#KGInteractionType_Review",
        description="Reviewing pull request for new features"
    )
    print(f"Created interaction 3 (from parameters): {interaction3_uri}")
    
    # Create interaction with defaults
    interaction4_uri = bridge.interactions.create_interaction()
    print(f"Created interaction 4 (with defaults): {interaction4_uri}")
    
    # Read interactions
    print("\n3. Reading interaction details...")
    interaction1_data = bridge.interactions.get_interaction(interaction1_uri)
    print(f"Interaction 1 data: {interaction1_data}")
    
    # Update interaction
    print("\n4. Updating interaction...")
    update_success = bridge.interactions.update_interaction(
        interaction1_uri,
        hasKGInteractionDescription="Updated: Planning session for Q1 and Q2 project goals"
    )
    print(f"Update successful: {update_success}")
    
    # Verify update
    updated_data = bridge.interactions.get_interaction(interaction1_uri)
    print(f"Updated interaction data: {updated_data}")
    
    # Query interactions by type
    print("\n5. Querying interactions by type...")
    meeting_interactions = bridge.interactions.query_interactions(
        interaction_type="http://vital.ai/ontology/haley-ai-kg#KGInteractionType_Meeting",
        limit=5
    )
    print_results("Meeting interactions", meeting_interactions)
    
    # ========================================================================
    # TEST CRUD OPERATIONS FOR ACTORS AND AGENTS
    # ========================================================================
    
    print_section("Testing KGActor and KGAgent CRUD Operations")
    
    # Create actors using instances
    print("\n6. Creating actors using KGActor instances...")
    
    # Create first actor instance
    actor1 = KGActor()
    actor1.URI = "http://vital.ai/test/actors/john_smith"
    actor1.name = "John Smith"
    actor1.kGraphDescription = "Project manager"
    
    actor1_uri = bridge.interactions.create_actor(
        actor_instance=actor1
    )
    print(f"Created actor 1 (from instance): {actor1_uri}")
    
    # Create actor using parameters
    actor2_uri = bridge.interactions.create_actor(
        name="Sarah Johnson",
        actor_type="http://vital.ai/ontology/haley-ai-kg#KGActorType_Customer"
    )
    print(f"Created actor 2 (from parameters): {actor2_uri}")
    
    # Create agents using instances and parameters
    print("\n7. Creating agents using KGAgent instances...")
    
    # Create first agent instance
    agent1 = KGAgent()
    agent1.URI = "http://vital.ai/test/agents/ai_assistant"
    agent1.name = "AI Assistant"
    agent1.kGraphDescription = "General purpose AI helper"
    
    agent1_uri = bridge.interactions.create_agent(
        agent_instance=agent1
    )
    print(f"Created agent 1 (from instance): {agent1_uri}")
    
    # Create agent using parameters
    agent2_uri = bridge.interactions.create_agent(
        name="Support Bot",
        agent_type="http://vital.ai/ontology/haley-ai-kg#KGAgentType_Support"
    )
    print(f"Created agent 2 (from parameters): {agent2_uri}")
    
    # ========================================================================
    # TEST EDGE OPERATIONS (LINKING)
    # ========================================================================
    
    print_section("Testing Edge Operations (Linking)")
    
    # Link actors and agents to interactions
    print("\n8. Linking actors and agents to interactions...")
    
    # Link actor to interaction 1
    edge1_uri = bridge.interactions.link_actor_to_interaction(interaction1_uri, actor1_uri)
    print(f"Linked actor to interaction 1: {edge1_uri}")
    
    # Link agent to interaction 2
    edge2_uri = bridge.interactions.link_agent_to_interaction(interaction2_uri, agent2_uri)
    print(f"Linked agent to interaction 2: {edge2_uri}")
    
    # Link actor to interaction 2
    edge3_uri = bridge.interactions.link_actor_to_interaction(interaction2_uri, actor2_uri)
    print(f"Linked actor to interaction 2: {edge3_uri}")
    
    # Get linked objects
    print("\n9. Getting linked objects...")
    interaction1_actors = bridge.interactions.get_interaction_actors(interaction1_uri)
    print_results("Actors linked to interaction 1", interaction1_actors)
    
    interaction2_agents = bridge.interactions.get_interaction_agents(interaction2_uri)
    print_results("Agents linked to interaction 2", interaction2_agents)
    
    # ========================================================================
    # TEST SPARQL-BASED SEARCH
    # ========================================================================
    
    print_section("Testing SPARQL-Based Date Search")
    
    print("\n10. Searching interactions by date range...")
    
    # Search for recent interactions (last 7 days)
    end_date = datetime.now().isoformat() + "Z"
    start_date = (datetime.now() - timedelta(days=7)).isoformat() + "Z"
    
    recent_interactions = bridge.interactions.search_interactions_by_date(
        start_date=start_date,
        end_date=end_date,
        limit=10
    )
    print_results(f"Interactions from {start_date} to {end_date}", recent_interactions)
    
    # Search by interaction type and date
    meeting_interactions_by_date = bridge.interactions.search_interactions_by_date(
        start_date=start_date,
        end_date=end_date,
        interaction_type="http://vital.ai/ontology/haley-ai-kg#KGInteractionType_Meeting",
        limit=5
    )
    print_results("Meeting interactions in date range", meeting_interactions_by_date)
    
    # ========================================================================
    # TEST VECTOR-BASED SEARCH
    # ========================================================================
    
    print_section("Testing Vector-Based Similarity Search")
    
    print("\n11. Searching interactions by similarity...")

    # Search interactions using description vector (should match kGraphDescription)
    interaction_results = bridge.interactions.search_interactions('planning project goals', vector_id="description")
    print(f"\nInteractions similar to 'planning project goals' (description vector):")
    if interaction_results:
        for result in interaction_results:
            object_uri = result.get('metadata', {}).get('uri', 'Unknown URI')
            print(f"  - {object_uri} (score: {result.get('score', 'N/A')})")
    else:
        print("  No results found.")

    # Also try general vector for comparison
    interaction_results_general = bridge.interactions.search_interactions('planning project goals', vector_id="general")
    print(f"\nInteractions similar to 'planning project goals' (general vector):")
    if interaction_results_general:
        for result in interaction_results_general:
            object_uri = result.get('metadata', {}).get('uri', 'Unknown URI')
            print(f"  - {object_uri} (score: {result.get('score', 'N/A')})")
    else:
        print("  No results found.")

    actor_results = bridge.interactions.search_actors('manager project lead', vector_id="general")
    print(f"\nActors similar to 'manager project lead':")
    if actor_results:
        for result in actor_results:
            object_uri = result.get('metadata', {}).get('uri', 'Unknown URI')
            print(f"  - {object_uri} (score: {result.get('score', 'N/A')})")
    else:
        print("  No results found.")

    agent_results = bridge.interactions.search_agents('support help customer', vector_id="general")
    print(f"\nAgents similar to 'support help customer':")
    if agent_results:
        for result in agent_results:
            object_uri = result.get('metadata', {}).get('uri', 'Unknown URI')
            print(f"  - {object_uri} (score: {result.get('score', 'N/A')})")
    else:
        print("  No results found.")
    
    # ========================================================================
    # TEST DELETE OPERATIONS
    # ========================================================================
    
    print_section("Testing Delete Operations")
    
    print("\n12. Testing delete operations...")
    
    # Delete an interaction
    delete_success = bridge.interactions.delete_interaction(interaction4_uri)
    print(f"Deleted interaction 4: {delete_success}")
    
    # Try to get deleted interaction (should return empty/None)
    try:
        deleted_data = bridge.interactions.get_interaction(interaction4_uri)
        print(f"Deleted interaction data (should be empty): {deleted_data}")
    except Exception as e:
        print(f"Expected error when getting deleted interaction: {e}")
    
    # Unlink actor from interaction
    unlink_success = bridge.interactions.unlink_actor_from_interaction(interaction1_uri, actor1_uri)
    print(f"Unlinked actor from interaction 1: {unlink_success}")
    
    # Verify unlinking
    remaining_actors = bridge.interactions.get_interaction_actors(interaction1_uri)
    print_results("Remaining actors for interaction 1 (should be empty)", remaining_actors)
    
    # ========================================================================
    # FINAL STATISTICS
    # ========================================================================
    
    print_section("Final Statistics")
    
    print("\n13. Getting final statistics...")
    stats = bridge.get_stats()
    print(f"Final graph statistics: {stats}")
    
    # Query all remaining interactions
    all_interactions = bridge.interactions.query_interactions(limit=20)
    print_results("All remaining interactions", all_interactions)
    
    print_section("Test Completed Successfully!")

if __name__ == "__main__":
    try:
        test_interaction_memory()
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
