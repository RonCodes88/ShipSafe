"""Base agent class template for all ShipSafe agents."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict
from graph.state import ScanState


class AgentConfig:
    """Configuration for agent instances."""
    
    def __init__(self, **kwargs):
        self.config = kwargs


def setup_logger(name: str) -> logging.Logger:
    """Set up a logger for an agent."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


class BaseAgent(ABC):
    """
    Base class for all agents in the ShipSafe vulnerability scanner.
    
    All agents should inherit from this class and implement the _execute method.
    """
    
    def __init__(self, config: AgentConfig = None):
        """
        Initialize the agent.
        
        Args:
            config: Agent configuration object
        """
        self.config = config or AgentConfig()
        self.logger = setup_logger(self.__class__.__name__)
    
    async def process(self, state: ScanState) -> ScanState:
        """
        Process state and return updated state.
        
        This method wraps the agent's _execute method with error handling
        and state tracking.
        
        Args:
            state: Current scan state
            
        Returns:
            Updated scan state
        """
        try:
            self.logger.info(f"Processing with {self.__class__.__name__}")
            
            # Track agent invocation
            if "agent_trace" not in state:
                state["agent_trace"] = []
            state["agent_trace"].append(self.__class__.__name__)
            
            # Execute agent logic
            result = await self._execute(state)
            
            # Update state with result
            updated_state = self._update_state(state, result)
            
            self.logger.info(f"{self.__class__.__name__} completed successfully")
            return updated_state
            
        except Exception as e:
            self.logger.error(f"Error in {self.__class__.__name__}: {e}", exc_info=True)
            
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"{self.__class__.__name__}:{str(e)}")
            
            return state
    
    @abstractmethod
    async def _execute(self, state: ScanState) -> Dict[str, Any]:
        """
        Execute the agent's core logic.
        
        This method should be overridden by subclasses to implement
        agent-specific behavior.
        
        Args:
            state: Current scan state
            
        Returns:
            Dictionary with results to be merged into state
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _execute method"
        )
    
    def _update_state(self, state: ScanState, result: Dict[str, Any]) -> ScanState:
        """
        Update state with execution results.
        
        Args:
            state: Current scan state
            result: Results from _execute method
            
        Returns:
            Updated scan state
        """
        # Merge result into state
        for key, value in result.items():
            if key in state and isinstance(state[key], list) and isinstance(value, list):
                # Append to existing lists
                state[key].extend(value)
            else:
                # Replace or add new keys
                state[key] = value
        
        return state

