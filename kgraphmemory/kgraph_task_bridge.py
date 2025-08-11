"""
KGraphTaskBridge - Specialized bridge for managing tasks and workflows.

Handles KGTask and related objects for storing task information in memory.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from vital_ai_vitalsigns.utils.uri_generator import URIGenerator
from .kgraph_bridge_utilities import KGraphBridgeUtilities

# Import ontology classes
try:
    from ai_haley_kg_domain.model.KGTask import KGTask
except ImportError as e:
    print(f"Warning: Could not import ontology classes: {e}")
    KGTask = None


class KGraphTaskBridge:
    """
    Specialized bridge for managing tasks and workflows.
    
    Provides high-level methods for:
    - Creating and managing KGTask objects
    - Linking tasks to interactions
    - Task status and progress tracking
    - Task search and filtering
    """
    
    def __init__(self, kgraph, parent_bridge=None):
        """
        Initialize the task bridge.
        
        Args:
            kgraph: KGraph instance
            parent_bridge: Parent KGraphBridge instance for cross-helper access
        """
        self.kgraph = kgraph
        self.parent_bridge = parent_bridge
        self.utils = KGraphBridgeUtilities(kgraph)
    
    # ============================================================================
    # TASK MANAGEMENT
    # ============================================================================
    
    def create_task(self, name: str, description: str = None,
                   task_type: str = None, priority: str = None,
                   status: str = "pending") -> str:
        """
        Create a new task.
        
        Args:
            name: Task name
            description: Task description
            task_type: Type of task
            priority: Task priority (e.g., "low", "medium", "high")
            status: Initial task status (default: "pending")
            
        Returns:
            URI of created task
        """
        task_props = {
            'hasName': name,
            'hasKGTaskStatus': status
        }
        
        if description:
            task_props['hasKGTaskDescription'] = description
        if task_type:
            task_props['hasKGTaskType'] = task_type
        if priority:
            task_props['hasKGTaskPriority'] = priority
        
        task_uri = self.utils.create_node('KGTask', **task_props)
        if not task_uri:
            raise RuntimeError("Failed to create task")
        
        return task_uri
    
    def create_task_for_interaction(self, name: str, interaction_uri: str,
                                   description: str = None, task_type: str = None,
                                   priority: str = None) -> str:
        """
        Create a task and link it to an interaction.
        
        Args:
            name: Task name
            interaction_uri: URI of interaction to link to
            description: Task description
            task_type: Type of task
            priority: Task priority
            
        Returns:
            URI of created task
        """
        task_uri = self.create_task(name, description, task_type, priority)
        self.utils.link_to_interaction(task_uri, interaction_uri, "KGTask")
        return task_uri
    
    def update_task_status(self, task_uri: str, status: str) -> bool:
        """
        Update the status of a task.
        
        Args:
            task_uri: URI of the task
            status: New status (e.g., "pending", "in_progress", "completed", "cancelled")
            
        Returns:
            True if updated successfully
        """
        try:
            task_obj = self.kgraph.get_object(task_uri)
            if task_obj:
                task_obj.hasKGTaskStatus = status
                if status == "completed":
                    task_obj.hasKGTaskCompletedAt = self.utils.generate_timestamp()
                self.kgraph.update_object(task_obj)
                return True
            return False
        except Exception as e:
            print(f"Warning: Failed to update task status: {e}")
            return False
    
    def update_task_progress(self, task_uri: str, progress: float) -> bool:
        """
        Update the progress of a task.
        
        Args:
            task_uri: URI of the task
            progress: Progress percentage (0.0 to 1.0)
            
        Returns:
            True if updated successfully
        """
        try:
            task_obj = self.kgraph.get_object(task_uri)
            if task_obj:
                task_obj.hasKGTaskProgress = progress
                self.kgraph.update_object(task_obj)
                return True
            return False
        except Exception as e:
            print(f"Warning: Failed to update task progress: {e}")
            return False
    
    # ============================================================================
    # TASK RELATIONSHIPS
    # ============================================================================
    
    def link_task_to_interaction(self, task_uri: str, interaction_uri: str) -> str:
        """
        Link a task to an interaction.
        
        Args:
            task_uri: URI of the task
            interaction_uri: URI of the interaction
            
        Returns:
            URI of created edge
        """
        return self.utils.link_to_interaction(task_uri, interaction_uri, "KGTask")
    
    def create_subtask(self, parent_task_uri: str, name: str,
                      description: str = None, task_type: str = None) -> str:
        """
        Create a subtask linked to a parent task.
        
        Args:
            parent_task_uri: URI of the parent task
            name: Subtask name
            description: Subtask description
            task_type: Type of subtask
            
        Returns:
            URI of created subtask
        """
        subtask_uri = self.create_task(name, description, task_type)
        
        # Link subtask to parent
        self.utils.create_edge("Edge_hasKGTask", parent_task_uri, subtask_uri)
        
        return subtask_uri
    
    def get_subtasks(self, parent_task_uri: str) -> List[Dict[str, Any]]:
        """
        Get all subtasks for a parent task.
        
        Args:
            parent_task_uri: URI of the parent task
            
        Returns:
            List of subtask dictionaries
        """
        return self.utils.get_linked_objects(parent_task_uri, "KGTask", "Edge_hasKGTask")
    
    # ============================================================================
    # TASK QUERIES
    # ============================================================================
    
    def get_tasks_for_interaction(self, interaction_uri: str) -> List[Dict[str, Any]]:
        """
        Get all tasks for an interaction.
        
        Args:
            interaction_uri: URI of the interaction
            
        Returns:
            List of task dictionaries
        """
        return self.utils.get_linked_objects(interaction_uri, "KGTask")
    
    def get_task_details(self, task_uri: str) -> Dict[str, Any]:
        """
        Get detailed information about a task including subtasks.
        
        Args:
            task_uri: URI of the task
            
        Returns:
            Dictionary with task details
        """
        task_props = self.utils.get_object_properties(task_uri)
        subtasks = self.get_subtasks(task_uri)
        
        return {
            'task_uri': task_uri,
            'properties': task_props,
            'subtasks': subtasks,
            'subtask_count': len(subtasks)
        }
    
    def get_interaction_task_summary(self, interaction_uri: str) -> Dict[str, Any]:
        """
        Get a summary of all tasks for an interaction.
        
        Args:
            interaction_uri: URI of the interaction
            
        Returns:
            Dictionary with task summary
        """
        tasks = self.get_tasks_for_interaction(interaction_uri)
        
        summary = {
            'interaction_uri': interaction_uri,
            'total_tasks': len(tasks),
            'pending_tasks': [],
            'in_progress_tasks': [],
            'completed_tasks': [],
            'cancelled_tasks': []
        }
        
        for task in tasks:
            task_uri = task.get('object')
            if task_uri:
                task_details = self.get_task_details(task_uri)
                status = task_details['properties'].get('hasKGTaskStatus', 'unknown')
                
                if status == 'pending':
                    summary['pending_tasks'].append(task_details)
                elif status == 'in_progress':
                    summary['in_progress_tasks'].append(task_details)
                elif status == 'completed':
                    summary['completed_tasks'].append(task_details)
                elif status == 'cancelled':
                    summary['cancelled_tasks'].append(task_details)
        
        return summary
    
    # ============================================================================
    # SEARCH AND FILTER
    # ============================================================================
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for tasks using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of task search results
        """
        return self.utils.search_by_type(query, "KGTask", limit)
    
    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get all tasks with a specific status.
        
        Args:
            status: Task status to filter by
            
        Returns:
            List of task dictionaries
        """
        return self.utils.filter_by_property("KGTask", "hasKGTaskStatus", status)
    
    def get_tasks_by_type(self, task_type: str) -> List[Dict[str, Any]]:
        """
        Get all tasks of a specific type.
        
        Args:
            task_type: Task type to filter by
            
        Returns:
            List of task dictionaries
        """
        return self.utils.filter_by_property("KGTask", "hasKGTaskType", task_type)
    
    def get_tasks_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """
        Get all tasks with a specific priority.
        
        Args:
            priority: Task priority to filter by
            
        Returns:
            List of task dictionaries
        """
        return self.utils.filter_by_property("KGTask", "hasKGTaskPriority", priority)
    
    def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all tasks that are overdue (have a due date in the past and are not completed).
        
        Returns:
            List of overdue task dictionaries
        """
        # This would require a more complex SPARQL query to check dates
        # For now, return tasks that are not completed
        pending_tasks = self.get_tasks_by_status("pending")
        in_progress_tasks = self.get_tasks_by_status("in_progress")
        return pending_tasks + in_progress_tasks
