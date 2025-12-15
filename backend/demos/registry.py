"""Demo registry for managing available demos.

This module provides a centralized registry of all available demos.
Only demos registered here can be executed through the API.
"""
from typing import Dict, Any, Callable, Optional
from pydantic import BaseModel

from backend.schemas.base import DemoRecipe
from backend.schemas.demos import TCPHandshakeParams, ARPDemoParams, ICMPPingParams
from backend.demos.layer4 import execute_tcp_handshake


class RegisteredDemo:
    """A registered demo with its metadata and execution function."""
    
    def __init__(
        self,
        recipe: DemoRecipe,
        function: Callable,
        params_class: type[BaseModel]
    ):
        self.recipe = recipe
        self.function = function
        self.params_class = params_class
    
    def validate_params(self, params: Dict[str, Any]) -> BaseModel:
        """Validate parameters against the demo's schema."""
        return self.params_class(**params)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the demo with validated parameters."""
        validated_params = self.validate_params(params)
        return self.function(validated_params)


class DemoRegistry:
    """Central registry for all available demos."""
    
    def __init__(self):
        self._demos: Dict[str, RegisteredDemo] = {}
        self._initialize_demos()
    
    def _initialize_demos(self):
        """Register all available demos."""
        # Layer 4: TCP Handshake
        self.register(
            DemoRecipe(
                id="tcp-handshake",
                name="TCP 3-Way Handshake",
                description=(
                    "Demonstrates TCP connection establishment. "
                    "Performs a complete 3-way handshake (SYN, SYN-ACK, ACK) "
                    "with a target server and captures detailed packet information."
                ),
                category="layer4",
                max_runtime=30,
                requires_network=True,
                requires_root=True,
                parameters_schema=TCPHandshakeParams.model_json_schema()
            ),
            execute_tcp_handshake,
            TCPHandshakeParams
        )
        
        # Additional demos can be registered here
        # Example for future demos:
        # self.register(
        #     DemoRecipe(
        #         id="arp-resolution",
        #         name="ARP Resolution",
        #         description="Demonstrates ARP protocol for MAC address resolution",
        #         category="layer2",
        #         max_runtime=10,
        #         requires_network=True,
        #         requires_root=True,
        #         parameters_schema=ARPDemoParams.model_json_schema()
        #     ),
        #     execute_arp_demo,
        #     ARPDemoParams
        # )
    
    def register(
        self,
        recipe: DemoRecipe,
        function: Callable,
        params_class: type[BaseModel]
    ):
        """Register a new demo."""
        if recipe.id in self._demos:
            raise ValueError(f"Demo '{recipe.id}' is already registered")
        
        self._demos[recipe.id] = RegisteredDemo(recipe, function, params_class)
    
    def get_demo(self, demo_id: str) -> Optional[RegisteredDemo]:
        """Get a registered demo by ID."""
        return self._demos.get(demo_id)
    
    def list_demos(self) -> list[DemoRecipe]:
        """List all registered demos."""
        return [demo.recipe for demo in self._demos.values()]
    
    def get_recipe(self, demo_id: str) -> Optional[DemoRecipe]:
        """Get the recipe for a specific demo."""
        demo = self.get_demo(demo_id)
        return demo.recipe if demo else None
    
    def demo_exists(self, demo_id: str) -> bool:
        """Check if a demo is registered."""
        return demo_id in self._demos
    
    def execute_demo(self, demo_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a demo with validated parameters."""
        demo = self.get_demo(demo_id)
        if not demo:
            raise ValueError(f"Demo '{demo_id}' not found")
        
        return demo.execute(params)


# Global registry instance
_registry: Optional[DemoRegistry] = None


def get_registry() -> DemoRegistry:
    """Get the global demo registry instance."""
    global _registry
    if _registry is None:
        _registry = DemoRegistry()
    return _registry


def list_available_demos() -> list[DemoRecipe]:
    """Convenience function to list all available demos."""
    return get_registry().list_demos()


def get_demo_recipe(demo_id: str) -> Optional[DemoRecipe]:
    """Convenience function to get a demo recipe."""
    return get_registry().get_recipe(demo_id)


def execute_registered_demo(demo_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to execute a demo."""
    return get_registry().execute_demo(demo_id, params)
