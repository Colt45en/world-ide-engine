"""Graphics Integration Layer

Connects MetaOrchestrator render_transforms and color outputs to 3D scene representation.
Maps orchestrator decisions to visual properties (position, rotation, scale, color).
Provides a simple scene graph that can be used by rendering engines.
"""


class SceneObject:
    """Represents a single 3D object in the scene."""
    
    def __init__(self, obj_id: str, obj_type: str = "cube"):
        """Initialize a scene object.
        
        Args:
            obj_id: Unique identifier
            obj_type: Type of object (cube, sphere, mesh, etc.)
        """
        self.obj_id = obj_id
        self.obj_type = obj_type
        
        # Transform properties
        self.position = (0.0, 0.0, 0.0)
        self.rotation = (0.0, 0.0, 0.0)  # Euler angles in degrees
        self.scale = (1.0, 1.0, 1.0)
        
        # Material properties
        self.color = (1.0, 1.0, 1.0)  # RGB
        self.metallic = 0.0
        self.roughness = 0.5
        self.emission = (0.0, 0.0, 0.0)
        
        # Metadata
        self.visible = True
        self.cast_shadow = True
        self.receive_shadow = True
    
    def apply_transform(self, position: tuple = None, rotation: tuple = None, scale: tuple = None) -> None:
        """Apply transformation to object.
        
        Args:
            position: (x, y, z) position
            rotation: (x, y, z) rotation in degrees
            scale: (x, y, z) scale factors
        """
        if position is not None:
            self.position = position
        if rotation is not None:
            self.rotation = rotation
        if scale is not None:
            self.scale = scale
    
    def apply_material(self, color: tuple = None, metallic: float = None, roughness: float = None, emission: tuple = None) -> None:
        """Apply material properties to object.
        
        Args:
            color: (r, g, b) color [0, 1]
            metallic: Metallicness [0, 1]
            roughness: Surface roughness [0, 1]
            emission: (r, g, b) emission color
        """
        if color is not None:
            self.color = color
        if metallic is not None:
            self.metallic = max(0.0, min(1.0, metallic))
        if roughness is not None:
            self.roughness = max(0.0, min(1.0, roughness))
        if emission is not None:
            self.emission = emission
    
    def to_dict(self) -> dict:
        """Convert object to dictionary representation."""
        return {
            "id": self.obj_id,
            "type": self.obj_type,
            "transform": {
                "position": self.position,
                "rotation": self.rotation,
                "scale": self.scale
            },
            "material": {
                "color": self.color,
                "metallic": self.metallic,
                "roughness": self.roughness,
                "emission": self.emission
            },
            "properties": {
                "visible": self.visible,
                "cast_shadow": self.cast_shadow,
                "receive_shadow": self.receive_shadow
            }
        }


class SceneGraph:
    """Manages a collection of scene objects."""
    
    def __init__(self):
        """Initialize empty scene graph."""
        self.objects: dict[str, SceneObject] = {}
        self.lights: dict[str, dict] = {}
        self.update_count = 0
    
    def add_object(self, obj: SceneObject) -> None:
        """Add object to scene.
        
        Args:
            obj: SceneObject to add
        """
        self.objects[obj.obj_id] = obj
        self.update_count += 1
    
    def get_object(self, obj_id: str) -> SceneObject | None:
        """Get object by ID.
        
        Args:
            obj_id: Object identifier
            
        Returns:
            SceneObject or None if not found
        """
        return self.objects.get(obj_id)
    
    def add_light(self, light_id: str, light_type: str = "directional", position: tuple = (0, 0, 0), color: tuple = (1, 1, 1), intensity: float = 1.0) -> None:
        """Add light to scene.
        
        Args:
            light_id: Unique identifier
            light_type: Type of light (directional, point, spot)
            position: Light position
            color: Light color (r, g, b)
            intensity: Light intensity
        """
        self.lights[light_id] = {
            "type": light_type,
            "position": position,
            "color": color,
            "intensity": intensity
        }
        self.update_count += 1
    
    def get_render_command(self) -> dict:
        """Get complete render command for current scene state.
        
        Returns:
            Dictionary with all objects and lights ready for rendering
        """
        return {
            "objects": [obj.to_dict() for obj in self.objects.values()],
            "lights": list(self.lights.values()),
            "update_count": self.update_count
        }


class OrchestratorRenderBridge:
    """Bidirectional bridge between MetaOrchestrator and graphics system."""
    
    def __init__(self):
        """Initialize graphics bridge."""
        self.scene = SceneGraph()
        self.object_sources: dict[str, str] = {}  # obj_id -> source orchestrator input
        self.total_renders = 0
    
    def create_object_from_orchestrator(self, obj_id: str, orchestrator_state: dict, obj_type: str = "cube") -> SceneObject:
        """Create a new scene object configured by orchestrator state.
        
        Args:
            obj_id: Unique object identifier
            orchestrator_state: State dict from MetaOrchestrator.orchestrate()
            obj_type: Type of 3D object to create
            
        Returns:
            Created SceneObject
        """
        obj = SceneObject(obj_id, obj_type)
        
        # Extract render transforms
        render_transforms = orchestrator_state.get("render_transforms", {})
        position = render_transforms.get("position", (0, 0, 0))
        rotation = render_transforms.get("rotation", (0, 0, 0))
        scale = render_transforms.get("scale", (1, 1, 1))
        
        # Apply transform
        obj.apply_transform(position=position, rotation=rotation, scale=scale)
        
        # Extract colors from upflow automation
        colors = orchestrator_state.get("colors", {})
        primary_color = colors.get("primary", (1, 1, 1))
        
        # Convert from HSL to RGB if needed
        if isinstance(primary_color, dict):
            # HSL format: apply as-is for now (would need HSL->RGB conversion in production)
            rgb = (primary_color.get("h", 0.5), primary_color.get("s", 0.5), primary_color.get("l", 0.5))
        else:
            rgb = primary_color if primary_color else (1, 1, 1)
        
        obj.apply_material(color=rgb)
        
        # Track source
        self.object_sources[obj_id] = orchestrator_state.get("input_text", "")
        
        # Add to scene
        self.scene.add_object(obj)
        
        return obj
    
    def apply_orchestrator_to_object(self, obj_id: str, orchestrator_state: dict) -> None:
        """Apply orchestrator state to existing object.
        
        Args:
            obj_id: ID of object to update
            orchestrator_state: New orchestrator state
        """
        obj = self.scene.get_object(obj_id)
        if not obj:
            # Create if doesn't exist
            self.create_object_from_orchestrator(obj_id, orchestrator_state)
            return
        
        # Extract and apply render transforms
        render_transforms = orchestrator_state.get("render_transforms", {})
        if render_transforms:
            position = render_transforms.get("position", obj.position)
            rotation = render_transforms.get("rotation", obj.rotation)
            scale = render_transforms.get("scale", obj.scale)
            obj.apply_transform(position=position, rotation=rotation, scale=scale)
        
        # Extract and apply colors
        colors = orchestrator_state.get("colors", {})
        if colors:
            primary_color = colors.get("primary", obj.color)
            if isinstance(primary_color, dict):
                rgb = (primary_color.get("h", 0.5), primary_color.get("s", 0.5), primary_color.get("l", 0.5))
            else:
                rgb = primary_color
            obj.apply_material(color=rgb)
        
        # Update source
        self.object_sources[obj_id] = orchestrator_state.get("input_text", "")
    
    def get_render_command(self) -> dict:
        """Get current render command from scene.
        
        Returns:
            Dictionary with all render data
        """
        self.total_renders += 1
        return self.scene.get_render_command()
    
    def get_system_status(self) -> dict:
        """Get overall graphics system status.
        
        Returns:
            Status dictionary
        """
        return {
            "total_objects": len(self.scene.objects),
            "total_lights": len(self.scene.lights),
            "total_renders": self.total_renders,
            "scene_updates": self.scene.update_count,
            "objects": [
                {
                    "id": obj.obj_id,
                    "type": obj.obj_type,
                    "position": obj.position,
                    "color": obj.color
                }
                for obj in self.scene.objects.values()
            ]
        }
