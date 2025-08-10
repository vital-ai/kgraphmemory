# Integration Patterns

## Overview

This document provides common integration patterns for using KGraphMemory in AI agent applications. These patterns demonstrate how to effectively incorporate the in-memory knowledge graph system into various agent architectures and use cases.

## Basic Integration Patterns

### Single Agent with Persistent Memory

```python
from kgraphmemory import KGraphMemory
from sentence_transformers import SentenceTransformer
from ai_haley_kg_domain.model.KGEntity import KGEntity
from ai_haley_kg_domain.model.KGChatMessage import KGChatMessage

class ConversationalAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        self.memory = KGraphMemory(self.embedding_model)
        self.knowledge_graph = self.memory.create_kgraph(
            f"agent_{agent_id}", 
            f"http://example.org/agent/{agent_id}"
        )
    
    def process_message(self, user_message):
        # Store the message
        message = KGChatMessage()
        message.hasKGChatMessageContent = user_message
        message.hasKGChatMessageType = "user_input"
        self.knowledge_graph.add_object(message)
        
        # Search for relevant context
        context = self.knowledge_graph.vector_search(user_message, limit=5)
        
        # Generate response using context
        response = self.generate_response(user_message, context)
        
        # Store the response
        response_msg = KGChatMessage()
        response_msg.hasKGChatMessageContent = response
        response_msg.hasKGChatMessageType = "agent_response"
        self.knowledge_graph.add_object(response_msg)
        
        return response
    
    def learn_fact(self, fact_text, entity_type=None):
        """Learn and store a new fact"""
        entity = KGEntity()
        entity.hasName = f"Fact_{len(self.get_all_facts())}"
        entity.hasKGEntityDescription = fact_text
        if entity_type:
            entity.hasKGEntityType = entity_type
        
        self.knowledge_graph.add_object(entity)
    
    def get_all_facts(self):
        """Retrieve all stored facts"""
        query = """
        PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
        PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
        
        SELECT ?entity ?description WHERE {
            ?entity a kg:KGEntity ;
                    kg:hasKGEntityDescription ?description .
        }
        """
        return self.knowledge_graph.sparql_query(query)
```

### Multi-Agent Knowledge Sharing

```python
class MultiAgentSystem:
    def __init__(self):
        self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        self.shared_memory = KGraphMemory(self.embedding_model)
        self.agents = {}
        
        # Create shared knowledge graph
        self.shared_kb = self.shared_memory.create_kgraph(
            "shared_knowledge", 
            "http://example.org/shared"
        )
    
    def create_agent(self, agent_id, agent_type):
        """Create a new agent with its own knowledge graph"""
        agent_graph = self.shared_memory.create_kgraph(
            f"agent_{agent_id}",
            f"http://example.org/agent/{agent_id}"
        )
        
        agent = {
            'id': agent_id,
            'type': agent_type,
            'graph': agent_graph
        }
        self.agents[agent_id] = agent
        return agent
    
    def share_knowledge(self, source_agent_id, knowledge_item):
        """Share knowledge from one agent to the shared knowledge base"""
        self.shared_kb.add_object(knowledge_item)
        
        # Optionally propagate to other relevant agents
        for agent_id, agent in self.agents.items():
            if agent_id != source_agent_id:
                # Check if knowledge is relevant to this agent
                if self.is_relevant_to_agent(knowledge_item, agent):
                    agent['graph'].add_object(knowledge_item)
    
    def search_across_all_agents(self, query):
        """Search across all agent knowledge graphs"""
        return self.shared_memory.search_across_kgraphs(query)
    
    def is_relevant_to_agent(self, knowledge_item, agent):
        """Determine if knowledge is relevant to a specific agent"""
        # Implement relevance logic based on agent type and knowledge content
        return True  # Simplified for example
```

## Task-Oriented Agent Patterns

### Task Planning and Execution

```python
from ai_haley_kg_domain.model.KGAction import KGAction
from ai_haley_kg_domain.model.KGFrame import KGFrame

class TaskOrientedAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        self.memory = KGraphMemory(self.embedding_model)
        self.task_graph = self.memory.create_kgraph(
            f"tasks_{agent_id}",
            f"http://example.org/tasks/{agent_id}"
        )
    
    def create_task_plan(self, goal, available_actions):
        """Create a task plan and store it in the knowledge graph"""
        
        # Create task frame
        task_frame = KGFrame()
        task_frame.hasName = f"Task_Plan_{goal}"
        task_frame.hasKGFrameDescription = f"Plan to achieve: {goal}"
        task_frame.hasKGFrameType = "task_plan"
        self.task_graph.add_object(task_frame)
        
        # Add actions to the plan
        for i, action_desc in enumerate(available_actions):
            action = KGAction()
            action.hasName = f"Action_{i}_{goal}"
            action.hasKGActionDescription = action_desc
            action.hasKGActionType = "planned_action"
            self.task_graph.add_object(action)
            
            # Create relationship between task and action
            # (This would use proper edge objects in full implementation)
        
        return task_frame
    
    def execute_task_step(self, task_id, step_id):
        """Execute a specific step and update knowledge"""
        
        # Find the action
        query = f"""
        PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
        PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
        
        SELECT ?action ?description WHERE {{
            ?action a kg:KGAction ;
                    vital-core:hasName "{step_id}" ;
                    kg:hasKGActionDescription ?description .
        }}
        """
        
        results = self.task_graph.sparql_query(query)
        if results:
            action_desc = results[0]['description']
            
            # Execute the action (implementation specific)
            result = self.perform_action(action_desc)
            
            # Store execution result
            self.store_execution_result(step_id, result)
            
            return result
        
        return None
    
    def store_execution_result(self, step_id, result):
        """Store the result of task execution"""
        result_entity = KGEntity()
        result_entity.hasName = f"Result_{step_id}"
        result_entity.hasKGEntityDescription = str(result)
        result_entity.hasKGEntityType = "execution_result"
        self.task_graph.add_object(result_entity)
    
    def perform_action(self, action_description):
        """Placeholder for actual action execution"""
        return f"Executed: {action_description}"
```

### Workflow Management

```python
class WorkflowAgent:
    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        self.memory = KGraphMemory(self.embedding_model)
        self.workflow_graph = self.memory.create_kgraph(
            f"workflow_{workflow_id}",
            f"http://example.org/workflow/{workflow_id}"
        )
        self.current_step = 0
    
    def define_workflow(self, steps):
        """Define a workflow with sequential steps"""
        workflow_frame = KGFrame()
        workflow_frame.hasName = f"Workflow_{self.workflow_id}"
        workflow_frame.hasKGFrameType = "workflow_definition"
        self.workflow_graph.add_object(workflow_frame)
        
        for i, step in enumerate(steps):
            step_action = KGAction()
            step_action.hasName = f"Step_{i}_{self.workflow_id}"
            step_action.hasKGActionDescription = step['description']
            step_action.hasKGActionType = step.get('type', 'workflow_step')
            self.workflow_graph.add_object(step_action)
    
    def execute_next_step(self):
        """Execute the next step in the workflow"""
        query = f"""
        PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
        PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
        
        SELECT ?action ?description WHERE {{
            ?action a kg:KGAction ;
                    vital-core:hasName "Step_{self.current_step}_{self.workflow_id}" ;
                    kg:hasKGActionDescription ?description .
        }}
        """
        
        results = self.workflow_graph.sparql_query(query)
        if results:
            step_desc = results[0]['description']
            result = self.execute_step(step_desc)
            self.current_step += 1
            return result
        
        return None
    
    def execute_step(self, step_description):
        """Execute a workflow step"""
        # Implementation specific
        return f"Completed: {step_description}"
```

## Context Management Patterns

### Conversation Context Tracking

```python
from ai_haley_kg_domain.model.KGChatInteraction import KGChatInteraction

class ContextAwareAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        self.memory = KGraphMemory(self.embedding_model)
        self.context_graph = self.memory.create_kgraph(
            f"context_{agent_id}",
            f"http://example.org/context/{agent_id}"
        )
        self.current_interaction = None
    
    def start_interaction(self, user_id, interaction_type="conversation"):
        """Start a new interaction context"""
        interaction = KGChatInteraction()
        interaction.hasName = f"Interaction_{user_id}_{len(self.get_all_interactions())}"
        interaction.hasKGInteractionType = interaction_type
        self.context_graph.add_object(interaction)
        self.current_interaction = interaction
        return interaction
    
    def add_to_context(self, item, context_type="general"):
        """Add an item to the current interaction context"""
        if self.current_interaction:
            # Store the item
            self.context_graph.add_object(item)
            
            # Create relationship to current interaction
            # (Would use proper edge objects in full implementation)
    
    def get_relevant_context(self, query, limit=5):
        """Get context relevant to the current query"""
        if not self.current_interaction:
            return []
        
        # Search within current interaction context
        context_results = self.context_graph.vector_search(query, limit=limit)
        
        # Also search historical interactions for relevant context
        historical_results = self.search_historical_context(query, limit=3)
        
        return context_results + historical_results
    
    def search_historical_context(self, query, limit=3):
        """Search previous interactions for relevant context"""
        # Implementation would search across past interactions
        return self.context_graph.vector_search(query, limit=limit)
    
    def get_all_interactions(self):
        """Get all past interactions"""
        query = """
        PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
        
        SELECT ?interaction WHERE {
            ?interaction a kg:KGChatInteraction .
        }
        """
        return self.context_graph.sparql_query(query)
```

### Session Management

```python
class SessionManagedAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        self.memory = KGraphMemory(self.embedding_model)
        self.sessions = {}
    
    def create_session(self, session_id, user_id):
        """Create a new session with its own knowledge graph"""
        session_graph = self.memory.create_kgraph(
            f"session_{session_id}",
            f"http://example.org/session/{session_id}"
        )
        
        session = {
            'id': session_id,
            'user_id': user_id,
            'graph': session_graph,
            'start_time': datetime.now(),
            'context': {}
        }
        
        self.sessions[session_id] = session
        return session
    
    def process_in_session(self, session_id, message):
        """Process a message within a specific session context"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        session_graph = session['graph']
        
        # Store message in session
        chat_msg = KGChatMessage()
        chat_msg.hasKGChatMessageContent = message
        session_graph.add_object(chat_msg)
        
        # Get session-specific context
        context = session_graph.vector_search(message, limit=5)
        
        # Process with context
        response = self.generate_response(message, context)
        
        # Store response
        response_msg = KGChatMessage()
        response_msg.hasKGChatMessageContent = response
        session_graph.add_object(response_msg)
        
        return response
    
    def end_session(self, session_id, save_to_long_term=True):
        """End a session and optionally save to long-term memory"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            if save_to_long_term:
                self.save_session_to_long_term(session)
            
            # Clean up session memory
            self.memory.remove_kgraph(f"session_{session_id}")
            del self.sessions[session_id]
    
    def save_session_to_long_term(self, session):
        """Save important session information to long-term memory"""
        # Implementation would extract and save key information
        pass
```

## Performance Optimization Patterns

### Lazy Loading and Caching

```python
class OptimizedAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        self.memory = KGraphMemory(self.embedding_model)
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get_cached_or_search(self, query, cache_key=None):
        """Use caching for frequent queries"""
        if cache_key is None:
            cache_key = hash(query)
        
        # Check cache
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_result
        
        # Perform search
        results = self.memory.search_across_kgraphs(query)
        
        # Cache results
        self.cache[cache_key] = (results, time.time())
        
        return results
    
    def batch_operations(self, operations):
        """Batch multiple operations for efficiency"""
        # Group operations by type
        adds = [op for op in operations if op['type'] == 'add']
        searches = [op for op in operations if op['type'] == 'search']
        
        # Execute batches
        for add_op in adds:
            # Batch add operations
            pass
        
        for search_op in searches:
            # Batch search operations
            pass
```

### Memory Management

```python
class MemoryManagedAgent:
    def __init__(self, agent_id, max_memory_items=10000):
        self.agent_id = agent_id
        self.max_memory_items = max_memory_items
        self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        self.memory = KGraphMemory(self.embedding_model)
        self.main_graph = self.memory.create_kgraph(
            f"agent_{agent_id}",
            f"http://example.org/agent/{agent_id}"
        )
    
    def add_with_memory_management(self, item):
        """Add item with automatic memory management"""
        # Check memory usage
        stats = self.main_graph.get_statistics()
        
        if stats['total_objects'] >= self.max_memory_items:
            self.cleanup_old_items()
        
        # Add new item
        self.main_graph.add_object(item)
    
    def cleanup_old_items(self, cleanup_ratio=0.1):
        """Remove oldest items to free memory"""
        # Implementation would identify and remove old items
        items_to_remove = int(self.max_memory_items * cleanup_ratio)
        
        # Query for oldest items
        query = """
        PREFIX kg: <http://vital.ai/ontology/haley-ai-kg#>
        PREFIX vital-core: <http://vital.ai/ontology/vital-core#>
        
        SELECT ?item ?timestamp WHERE {
            ?item vital-core:hasTimestamp ?timestamp .
        }
        ORDER BY ?timestamp
        LIMIT %d
        """ % items_to_remove
        
        old_items = self.main_graph.sparql_query(query)
        
        for item in old_items:
            self.main_graph.delete_object(item['item'])
```

## Integration Best Practices

### Error Handling and Resilience

```python
class ResilientAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        self.memory = KGraphMemory(self.embedding_model)
        self.backup_enabled = True
    
    def safe_operation(self, operation_func, *args, **kwargs):
        """Execute operations with error handling"""
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            self.handle_error(e, operation_func.__name__)
            return None
    
    def handle_error(self, error, operation_name):
        """Handle errors gracefully"""
        print(f"Error in {operation_name}: {error}")
        
        if self.backup_enabled:
            self.create_backup()
    
    def create_backup(self):
        """Create backup of current state"""
        # Implementation would save current state
        pass
    
    def restore_from_backup(self):
        """Restore from backup"""
        # Implementation would restore previous state
        pass
```

### Monitoring and Logging

```python
import logging
from datetime import datetime

class MonitoredAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        self.memory = KGraphMemory(self.embedding_model)
        self.logger = logging.getLogger(f"agent_{agent_id}")
        self.metrics = {
            'operations_count': 0,
            'search_count': 0,
            'add_count': 0,
            'error_count': 0
        }
    
    def monitored_search(self, query, **kwargs):
        """Search with monitoring"""
        start_time = time.time()
        
        try:
            results = self.memory.search_across_kgraphs(query, **kwargs)
            self.metrics['search_count'] += 1
            self.metrics['operations_count'] += 1
            
            duration = time.time() - start_time
            self.logger.info(f"Search completed in {duration:.3f}s, {len(results)} results")
            
            return results
            
        except Exception as e:
            self.metrics['error_count'] += 1
            self.logger.error(f"Search failed: {e}")
            raise
    
    def get_performance_metrics(self):
        """Get current performance metrics"""
        return {
            **self.metrics,
            'timestamp': datetime.now().isoformat()
        }
```

These integration patterns provide a foundation for building sophisticated AI agents that leverage KGraphMemory's capabilities for knowledge storage, retrieval, and management. Each pattern can be adapted and extended based on specific application requirements.
