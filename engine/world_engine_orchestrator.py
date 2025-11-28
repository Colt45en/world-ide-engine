"""
WorldEngineOrchestrator - Central coordination hub for the Nexus AI system.

Connects:
- MetaOrchestrator (semantic reasoning, token/morpheme processing)
- NexusCore (physics simulation, geometry, aesthetics)
- QTP Bridge (quantum thought pipeline for frame packets)
- Graphics/Rendering bridges

This module acts as the "brain" that makes the Nexus AI system flow and work
like an intelligent agent.
"""

from __future__ import annotations
import time
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

# Lazy imports to avoid circular dependencies
_lazy_imports = {}

def _get_meta_orchestrator():
    if 'MetaOrchestrator' not in _lazy_imports:
        try:
            from meta.orchestrator_v2 import MetaOrchestrator
            _lazy_imports['MetaOrchestrator'] = MetaOrchestrator
        except ImportError:
            _lazy_imports['MetaOrchestrator'] = None
    return _lazy_imports['MetaOrchestrator']

def _get_nexus_core():
    if 'NexusCore' not in _lazy_imports:
        try:
            from nexus.core import NexusCore, Vector3
            _lazy_imports['NexusCore'] = NexusCore
            _lazy_imports['Vector3'] = Vector3
        except ImportError:
            _lazy_imports['NexusCore'] = None
            _lazy_imports['Vector3'] = None
    return _lazy_imports.get('NexusCore'), _lazy_imports.get('Vector3')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_SPAWN_HEIGHT = 10.0  # Default Y position for spawned entities


class AgentState(Enum):
    """State of the Nexus Agent."""
    IDLE = "idle"
    PROCESSING = "processing"
    EXECUTING = "executing"
    WAITING = "waiting"
    ERROR = "error"


@dataclass
class AgentTask:
    """Represents a task for the agent to execute."""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: int = 0
    timestamp: float = field(default_factory=time.time)
    completed: bool = False
    result: Optional[Dict[str, Any]] = None


@dataclass
class AgentMemory:
    """Agent's working memory for context and history."""
    context: Dict[str, Any] = field(default_factory=dict)
    task_history: List[AgentTask] = field(default_factory=list)
    decision_log: List[Dict[str, Any]] = field(default_factory=list)
    max_history: int = 100
    
    def remember(self, key: str, value: Any) -> None:
        """Store a value in context memory."""
        self.context[key] = value
    
    def recall(self, key: str, default: Any = None) -> Any:
        """Recall a value from context memory."""
        return self.context.get(key, default)
    
    def log_decision(self, decision: Dict[str, Any]) -> None:
        """Log a decision made by the agent."""
        self.decision_log.append({
            **decision,
            'timestamp': time.time()
        })
        if len(self.decision_log) > self.max_history:
            self.decision_log.pop(0)
    
    def add_task(self, task: AgentTask) -> None:
        """Add completed task to history."""
        self.task_history.append(task)
        if len(self.task_history) > self.max_history:
            self.task_history.pop(0)


class NexusAgent:
    """
    The Nexus Agent - An AI agent that orchestrates the World Engine.
    
    The agent operates in a perception-reasoning-action loop:
    1. PERCEIVE: Receives input (text, commands, sensor data)
    2. REASON: Uses MetaOrchestrator for semantic analysis
    3. ACT: Executes through physics/rendering systems
    4. LEARN: Updates memory with outcomes
    """
    
    def __init__(self):
        self.state = AgentState.IDLE
        self.memory = AgentMemory()
        self.task_queue: List[AgentTask] = []
        self.action_handlers: Dict[str, Callable] = {}
        self._task_counter = 0
        
        # Initialize subsystems lazily
        self._meta_orchestrator = None
        self._nexus_core = None
        
        # Register default action handlers
        self._register_default_handlers()
        
        logger.info("NexusAgent initialized")
    
    @property
    def meta_orchestrator(self):
        """Lazy load MetaOrchestrator."""
        if self._meta_orchestrator is None:
            MetaOrchestrator = _get_meta_orchestrator()
            if MetaOrchestrator:
                self._meta_orchestrator = MetaOrchestrator()
        return self._meta_orchestrator
    
    @property
    def nexus_core(self):
        """Lazy load NexusCore."""
        if self._nexus_core is None:
            NexusCore, _ = _get_nexus_core()
            if NexusCore:
                self._nexus_core = NexusCore()
        return self._nexus_core
    
    def _register_default_handlers(self) -> None:
        """Register default action handlers."""
        self.register_action('process_text', self._handle_process_text)
        self.register_action('spawn_entity', self._handle_spawn_entity)
        self.register_action('step_physics', self._handle_step_physics)
        self.register_action('query_state', self._handle_query_state)
    
    def register_action(self, action_type: str, handler: Callable) -> None:
        """Register an action handler."""
        self.action_handlers[action_type] = handler
    
    def perceive(self, input_data: Dict[str, Any]) -> AgentTask:
        """
        PERCEIVE: Process incoming input and create a task.
        """
        self._task_counter += 1
        task_id = f"task_{self._task_counter}_{int(time.time()*1000)}"
        
        # Determine task type from input
        task_type = input_data.get('type', 'process_text')
        priority = input_data.get('priority', 0)
        
        task = AgentTask(
            task_id=task_id,
            task_type=task_type,
            payload=input_data,
            priority=priority
        )
        
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: -t.priority)
        
        logger.info(f"Perceived new task: {task_id} (type={task_type})")
        return task
    
    def reason(self, task: AgentTask) -> Dict[str, Any]:
        """
        REASON: Analyze the task using MetaOrchestrator.
        """
        self.state = AgentState.PROCESSING
        
        reasoning_result = {
            'task_id': task.task_id,
            'analysis': {},
            'decision': None,
            'actions': []
        }
        
        # Extract text content for semantic analysis
        text = task.payload.get('text', task.payload.get('input', ''))
        
        if text and self.meta_orchestrator:
            # Run through MetaOrchestrator for semantic analysis
            orchestrator_result = self.meta_orchestrator.orchestrate(text)
            reasoning_result['analysis'] = orchestrator_result
            reasoning_result['decision'] = orchestrator_result.get('decision', 'neutral')
            
            # Determine actions based on decision
            decision = orchestrator_result.get('decision', 'neutral')
            if decision == 'aggressive':
                reasoning_result['actions'] = ['spawn_entity', 'step_physics']
            elif decision == 'balanced':
                reasoning_result['actions'] = ['step_physics']
            else:
                reasoning_result['actions'] = ['query_state']
        else:
            reasoning_result['decision'] = 'passthrough'
            reasoning_result['actions'] = [task.task_type]
        
        # Log decision
        self.memory.log_decision({
            'task_id': task.task_id,
            'decision': reasoning_result['decision'],
            'actions': reasoning_result['actions']
        })
        
        logger.info(f"Reasoning complete: decision={reasoning_result['decision']}")
        return reasoning_result
    
    def act(self, task: AgentTask, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACT: Execute actions based on reasoning.
        """
        self.state = AgentState.EXECUTING
        results = {
            'task_id': task.task_id,
            'actions_executed': [],
            'outputs': {}
        }
        
        for action in reasoning.get('actions', []):
            handler = self.action_handlers.get(action)
            if handler:
                try:
                    output = handler(task, reasoning)
                    results['outputs'][action] = output
                    results['actions_executed'].append(action)
                except Exception as e:
                    logger.error(f"Action {action} failed: {e}")
                    results['outputs'][action] = {'error': str(e)}
        
        logger.info(f"Executed {len(results['actions_executed'])} actions")
        return results
    
    def learn(self, task: AgentTask, results: Dict[str, Any]) -> None:
        """
        LEARN: Update memory with task outcomes.
        """
        task.completed = True
        task.result = results
        self.memory.add_task(task)
        
        # Store useful context for future tasks
        if 'analysis' in results:
            self.memory.remember('last_analysis', results['analysis'])
        
        self.state = AgentState.IDLE
        logger.info(f"Task {task.task_id} completed and learned from")
    
    def step(self) -> Optional[Dict[str, Any]]:
        """
        Execute one complete perception-reasoning-action-learning cycle.
        """
        if not self.task_queue:
            return None
        
        task = self.task_queue.pop(0)
        
        # Execute the agent loop
        reasoning = self.reason(task)
        results = self.act(task, reasoning)
        self.learn(task, results)
        
        return {
            'task': task.task_id,
            'reasoning': reasoning,
            'results': results
        }
    
    # --- Action Handlers ---
    
    def _handle_process_text(self, task: AgentTask, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text processing action."""
        return {
            'processed': True,
            'analysis': reasoning.get('analysis', {})
        }
    
    def _handle_spawn_entity(self, task: AgentTask, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """Handle entity spawning action."""
        if not self.nexus_core:
            return {'spawned': False, 'error': 'NexusCore not available'}
        
        _, Vector3 = _get_nexus_core()
        if not Vector3:
            return {'spawned': False, 'error': 'Vector3 not available'}
        
        # Get physics params from reasoning
        physics_params = reasoning.get('analysis', {}).get('physics_params', {})
        velocity = physics_params.get('velocity', (0, 0, 0))
        mass = physics_params.get('mass', 1.0)
        
        # Spawn a body
        pos = Vector3(0, DEFAULT_SPAWN_HEIGHT, 0)  # Start above ground
        vel = Vector3(velocity[0], velocity[1], velocity[2]) if velocity else None
        
        body = self.nexus_core.spawn_body(
            position=pos,
            velocity=vel,
            mass=mass,
            radius=1.0
        )
        
        return {
            'spawned': True,
            'body_id': body.id,
            'position': (body.position.x, body.position.y, body.position.z)
        }
    
    def _handle_step_physics(self, task: AgentTask, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """Handle physics step action."""
        if not self.nexus_core:
            return {'stepped': False, 'error': 'NexusCore not available'}
        
        physics_state = self.nexus_core.update_physics(self.nexus_core.time_step)
        return {
            'stepped': True,
            'physics_state': physics_state
        }
    
    def _handle_query_state(self, task: AgentTask, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """Handle state query action."""
        state = {
            'agent_state': self.state.value,
            'tasks_pending': len(self.task_queue),
            'tasks_completed': len(self.memory.task_history),
            'decisions_made': len(self.memory.decision_log)
        }
        
        if self.nexus_core:
            state['physics'] = self.nexus_core.get_physics_state()
        
        if self.meta_orchestrator:
            state['orchestrator'] = self.meta_orchestrator.get_status()
        
        return state


class WorldEngineOrchestrator:
    """
    Main orchestrator for the World Engine.
    
    Coordinates:
    - NexusAgent for AI-driven behavior
    - Frame packet generation for streaming
    - System metrics and health monitoring
    """
    
    def __init__(self):
        self.agent = NexusAgent()
        self.frame_count = 0
        self.start_time = time.time()
        self.current_frame = None
        
        # Metrics
        self.metrics = {
            'frames_processed': 0,
            'agent_steps': 0,
            'errors': 0
        }
        
        logger.info("WorldEngineOrchestrator initialized")
    
    def step(self, frame_packet: Dict[str, Any]) -> None:
        """
        Process a frame packet and update the world state.
        
        Called by the bus server on each tick (~60Hz).
        """
        self.frame_count += 1
        self.current_frame = frame_packet
        self.metrics['frames_processed'] += 1
        
        # Check if there are agent tasks to process
        if self.agent.task_queue:
            try:
                self.agent.step()
                self.metrics['agent_steps'] += 1
            except Exception as e:
                logger.error(f"Agent step error: {e}")
                self.metrics['errors'] += 1
    
    def query(self, query_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a query request.
        
        Args:
            query_payload: Query parameters (e.g., {'type': 'process_text', 'text': 'hello'})
        
        Returns:
            Query result
        """
        # Create a task for the agent
        task = self.agent.perceive(query_payload)
        
        # Process immediately
        result = self.agent.step()
        
        return result or {'status': 'no_result'}
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        uptime = time.time() - self.start_time
        
        return {
            'uptime_seconds': uptime,
            'frame_count': self.frame_count,
            'fps': self.frame_count / uptime if uptime > 0 else 0,
            'agent_state': self.agent.state.value,
            'tasks_pending': len(self.agent.task_queue),
            'tasks_completed': len(self.agent.memory.task_history),
            **self.metrics
        }
    
    def get_current_frame(self) -> Dict[str, Any]:
        """Get the current frame packet."""
        return self.current_frame or {
            'tick': self.frame_count,
            'fps': 60,
            'entities': [],
            'world_state': {},
            'system_status': 'idle'
        }


__all__ = ['WorldEngineOrchestrator', 'NexusAgent', 'AgentState', 'AgentTask', 'AgentMemory']
