"""
Physics System - CORRECTED IMPLEMENTATION
Fixes all critical gaps from SYSTEMS_AUDIT_CRITICAL_GAPS.md
"""

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from geometry import Vector3, Ray, GeometryEngine

# =============================================================================
# PHYSICS OBJECT BASE CLASS
# =============================================================================

@dataclass
class PhysicsObject:
    """
    Physics-enabled object with mass, velocity, acceleration

    CONTRACT: All external code assumes:
    - position, velocity, acceleration are mutable Vector3 objects
    - You can set position.y = value
    - Vector3 supports: +, -, *, magnitude(), normalize(), cross(), dot()
    """
    mass: float = 1.0
    position: Vector3 = field(default_factory=lambda: Vector3(0, 0, 0))
    velocity: Vector3 = field(default_factory=lambda: Vector3(0, 0, 0))
    acceleration: Vector3 = field(default_factory=lambda: Vector3(0, 0, 0))
    drag: float = 0.01  # Per-frame damping (multiplicative)
    radius: float = 0.5

    def apply_force(self, force: Vector3):
        """
        Apply force to object

        Force accumulates into acceleration. Integration consumes dt during
        integrate_velocity(). Do NOT pass dt—it's consumed during integration.
        """
        if self.mass > 0:
            self.acceleration = self.acceleration + (force * (1.0 / self.mass))

    def integrate_velocity(self, dt: float, damping: float = 0.99):
        """
        Integrate acceleration into velocity with damping

        v ← v + a*dt
        v ← v * damping  (per-frame drag)
        a ← 0  (forces consumed)
        """
        self.velocity = self.velocity + (self.acceleration * dt)
        self.velocity = self.velocity * damping
        self.acceleration = Vector3(0, 0, 0)  # Reset for next frame

    def integrate_position(self, dt: float):
        """
        Integrate velocity into position

        p ← p + v*dt
        """
        self.position = self.position + (self.velocity * dt)

    def get_kinetic_energy(self) -> float:
        """Return 0.5 * m * v²"""
        v_mag = self.velocity.magnitude()
        return 0.5 * self.mass * v_mag * v_mag

# =============================================================================
# PLAYER CLASS
# =============================================================================

@dataclass
class Player(PhysicsObject):
    """Player character with health, abilities, and movement"""

    max_hp: float = 100.0
    hp: float = field(default_factory=lambda: 100.0)
    is_dead: bool = False

    move_speed: float = 15.0  # Units per second
    sensitivity: float = 1.0
    invert_y: bool = False

    # Cooldowns for abilities (indexed by ability ID)
    cooldowns = field(default_factory=lambda: {1: 0.0, 2: 0.0, 3: 0.0})

    # Combat stats
    base_damage: float = 20.0
    crit_chance: float = 0.1

    def take_damage(self, damage, dt=1.0):
        """Take damage (clamped to >= 0)"""
        self.hp = max(0, self.hp - damage * dt)
        if self.hp <= 0:
            self.is_dead = True

    def heal(self, amount):
        """Heal player (clamped to <= max_hp)"""
        self.hp = min(self.max_hp, self.hp + amount)
        if self.hp > 0:
            self.is_dead = False

    def is_dead_check(self) -> bool:
        """Check if player is dead"""
        return self.is_dead

    def update_cooldowns(self, dt):
        """Decrease all cooldowns by dt"""
        if self.cooldowns:
            for ability_id in self.cooldowns:
                self.cooldowns[ability_id] = max(0, self.cooldowns[ability_id] - dt)

    def get_ability_ready(self, ability_id: int) -> bool:
        """Check if ability is ready (cooldown <= 0)"""
        if self.cooldowns is None:
            return False
        return self.cooldowns.get(ability_id, 0.0) <= 0

    def trigger_ability(self, ability_id: int, cooldown: float):
        """Trigger ability and set cooldown"""
        if self.cooldowns is not None:
            self.cooldowns[ability_id] = cooldown

# =============================================================================
# ENEMY CLASS
# =============================================================================

@dataclass
class Enemy(PhysicsObject):
    """Enemy character with health, AI, and loot"""

    max_hp: float = 50.0
    hp: float = field(default_factory=lambda: 50.0)

    contact_dps: float = 10.0  # Damage per second on contact
    chase_speed: float = 8.0   # Units per second

    xp_reward: float = 100.0
    drop_value: float = 10.0

    def take_damage(self, damage):
        """Take damage (clamped to >= 0)"""
        self.hp = max(0, self.hp - damage)

    def is_alive(self) -> bool:
        """Check if enemy is still alive"""
        return self.hp > 0

    def check_player_contact(self, player, dt):
        """
        Check for contact with player and apply damage if touched

        Uses symmetric sphere collision test: distance < r1 + r2
        """
        if not player or player.is_dead_check():
            return False

        distance = self.position.distance_to(player.position)
        required_distance = self.radius + player.radius

        if distance < required_distance:
            # Contact! Apply damage to player
            player.take_damage(self.contact_dps, dt)
            return True

        return False

    def update(self, player_pos, dt):
        """
        Update enemy AI: chase player toward their position

        Simple behavior: accelerate toward player at chase_speed
        """
        if not player_pos:
            return

        direction_to_player = (player_pos - self.position).normalize()
        chase_force = direction_to_player * self.chase_speed * self.mass
        self.apply_force(chase_force)

# =============================================================================
# PROJECTILE CLASS
# =============================================================================

@dataclass
class Projectile(PhysicsObject):
    """Projectile fired from player or environment"""

    damage: float = 25.0
    hit_radius: float = 0.3
    lifetime: float = 5.0
    remaining_lifetime: float = field(default_factory=lambda: 5.0)

    owner_id: int = -1  # ID of who fired this (to prevent self-hit)

    def update(self, dt):
        """Update projectile lifetime"""
        self.remaining_lifetime -= dt

    def is_expired(self) -> bool:
        """Check if projectile has exceeded lifetime"""
        return self.remaining_lifetime <= 0

    def check_enemy_hit(self, enemy):
        """
        Check for hit against enemy

        FIX: Use symmetric sphere collision (include enemy.radius)
        """
        if not enemy.is_alive():
            return False

        distance = self.position.distance_to(enemy.position)
        # FIXED: Include enemy radius (symmetric collision test)
        if distance < (self.hit_radius + enemy.radius):
            enemy.take_damage(self.damage)
            return True

        return False

# =============================================================================
# COLLISION RESOLUTION
# =============================================================================

class CollisionSystem:
    """Resolve collisions between objects"""

    def __init__(self, geometry_engine):
        self.geometry = geometry_engine

    def check_collision(self, obj1: PhysicsObject, obj2: PhysicsObject) -> bool:
        """Check if two objects are colliding (sphere-sphere)"""
        distance = obj1.position.distance_to(obj2.position)
        return distance < (obj1.radius + obj2.radius)

    def resolve_collisions(self, objects: List[PhysicsObject]):
        """
        Resolve collisions by pushing objects apart

        For sphere-sphere collisions, move each object along line of centers
        by half the overlap distance.
        """
        n = len(objects)
        for i in range(n):
            for j in range(i + 1, n):
                obj1, obj2 = objects[i], objects[j]

                distance = obj1.position.distance_to(obj2.position)
                min_distance = obj1.radius + obj2.radius

                if distance < min_distance:
                    # Overlap detected
                    # Compute pushout direction
                    if distance < 0.001:  # Degenerate case: same position
                        pushout_dir = Vector3(1, 0, 0)
                    else:
                        pushout_dir = (obj1.position - obj2.position).normalize()

                    # Compute pushout magnitude
                    overlap = min_distance - distance
                    pushout = overlap / 2.0

                    # Push both objects apart
                    obj1.position = obj1.position + (pushout_dir * pushout)
                    obj2.position = obj2.position + (pushout_dir * -pushout)

# =============================================================================
# CONSTRAINT SYSTEM
# =============================================================================

class ConstraintSystem:
    """Apply constraints like ground collision"""

    @staticmethod
    def constrain_to_ground(obj: PhysicsObject, height_function=None):
        """
        Constrain object to ground (y >= ground_height)

        FIX: When object is clamped to ground, zero downward velocity
        and acceleration to prevent infinite freefall buildup

        Args:
            obj: PhysicsObject to constrain
            height_function: Optional callable(x, z) -> height
        """
        if height_function:
            ground_height = height_function(obj.position.x, obj.position.z)
        else:
            ground_height = 0.0

        if obj.position.y < ground_height:
            # Object is below ground, clamp it
            obj.position.y = ground_height

            # CRITICAL FIX: Kill downward velocity/acceleration
            # Otherwise object accumulates infinite downward velocity
            # and the physics engine is technically in permanent freefall
            if obj.velocity.y < 0:
                obj.velocity.y = 0.0

            if obj.acceleration.y < 0:
                obj.acceleration.y = 0.0

    @staticmethod
    def clamp_velocity_magnitude(obj: PhysicsObject, max_velocity: float):
        """Clamp velocity to maximum magnitude"""
        velocity_mag = obj.velocity.magnitude()
        if velocity_mag > max_velocity:
            obj.velocity = obj.velocity * (max_velocity / velocity_mag)

# =============================================================================
# PHYSICS SIMULATOR
# =============================================================================

class PhysicsSimulator:
    """
    Main physics simulation loop

    Manages all dynamic objects, forces, constraints, collisions, and metrics
    """

    def __init__(self, config: Dict[str, Any]):
        self.gravity = config.get('gravity', -9.8)
        self.damping = config.get('damping', 0.99)
        self.max_velocity = config.get('max_velocity', 50.0)
        self.timestep = config.get('timestep', 1.0 / 60.0)

        # Fixed-timestep integration (optional but recommended)
        self.use_fixed_timestep = config.get('use_fixed_timestep', False)
        self.accumulator = 0.0

        # Objects
        self.player: Optional[Player] = None
        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []
        self.static_objects: List[PhysicsObject] = []

        # Systems
        self.geometry = GeometryEngine()
        self.collision_system = CollisionSystem(self.geometry)
        self.constraint_system = ConstraintSystem()

        # Metrics
        self.metrics = {
            'object_count': 0,
            'collision_count': 0,
            'physics_energy': 0.0,
            'average_velocity': 0.0,
        }

        # Camera data (for input translation)
        self.camera_data: Optional[Dict[str, Any]] = None

    def receive_camera_data(self, camera_data: Dict[str, Any]):
        """
        Receive camera frame data for physics updates

        Camera provides: position, forward, right, distance, angles
        Physics uses this to translate player input from camera space to world space

        Example:
            Input from WASD is in camera space (forward/right relative to camera)
            We rotate that into world space before applying to player
        """
        self.camera_data = camera_data

    def apply_player_input(self, move_direction: Vector3):
        """
        Apply player input as movement force

        FIX: Gap 8 - Player had no way to move. This is the interface.

        Args:
            move_direction: Normalized input direction (e.g., from WASD)
                          Usually computed as: camera_right * input.x + camera_forward * input.z
        """
        if not self.player or self.player.is_dead_check():
            return

        if move_direction.magnitude() < 0.01:  # Deadzone
            return

        desired_dir = move_direction.normalize()

        # Apply horizontal force (don't modify vertical)
        desired_force = desired_dir * self.player.move_speed * self.player.mass
        desired_force.y = 0.0  # Vertical motion is gravity + jumps only

        self.player.apply_force(desired_force)

    def set_player(self, player: Player):
        """Set the player object"""
        self.player = player

    def add_enemy(self, enemy: Enemy):
        """Add enemy to simulation"""
        self.enemies.append(enemy)

    def remove_enemy(self, enemy: Enemy):
        """Remove enemy from simulation"""
        if enemy in self.enemies:
            self.enemies.remove(enemy)

    def add_projectile(self, projectile: Projectile):
        """Add projectile to simulation"""
        self.projectiles.append(projectile)

    def add_static_object(self, obj: PhysicsObject):
        """Add static (non-moving) object"""
        self.static_objects.append(obj)

    def update(self, dt: float):
        """
        Update physics simulation

        Supports both fixed and variable timesteps
        """
        if self.use_fixed_timestep:
            self._update_fixed_timestep(dt)
        else:
            # Variable timestep, but clamped to prevent tunneling
            dt = min(dt, 0.1)  # Max 100ms per step
            self._integrate_physics(dt)

        self._update_metrics()

    def _update_fixed_timestep(self, dt: float):
        """Fixed timestep with accumulator (recommended for stability)"""
        # Clamp dt to prevent spiral if frame takes too long
        dt = min(dt, 0.1)

        self.accumulator += dt

        # Run fixed-size steps until caught up
        while self.accumulator >= self.timestep:
            self._integrate_physics(self.timestep)
            self.accumulator -= self.timestep

    def _integrate_physics(self, dt: float):
        """Single physics integration step"""
        # Apply gravity to all dynamic objects
        self._apply_gravity(dt)

        # Update player
        self._update_player(dt)

        # Update enemies
        self._update_enemies(dt)

        # Update projectiles
        self._update_projectiles(dt)

        # Integrate all dynamic objects
        self._integrate_all_objects(dt)

        # Apply constraints (ground collision)
        self._apply_constraints(dt)

        # Resolve object collisions
        self._resolve_collisions()

        # Cleanup dead enemies and expired projectiles
        self._cleanup()

    def _apply_gravity(self, dt: float):
        """Apply gravity force to all dynamic objects"""
        gravity_force = Vector3(0, self.gravity, 0)

        if self.player:
            self.player.apply_force(gravity_force * self.player.mass)

        for enemy in self.enemies:
            enemy.apply_force(gravity_force * enemy.mass)

        # Projectiles also experience gravity
        for projectile in self.projectiles:
            projectile.apply_force(gravity_force * projectile.mass)

    def _update_player(self, dt: float):
        """Update player-specific logic"""
        if not self.player:
            return

        # Update cooldowns
        self.player.update_cooldowns(dt)

    def _update_enemies(self, dt: float):
        """
        Update enemy AI

        FIX: Gap 4 - Stop updating enemies if player is dead
        """
        if not self.player or self.player.is_dead_check():
            return

        for enemy in self.enemies:
            # Check contact with player
            enemy.check_player_contact(self.player, dt)

            # Chase player
            enemy.update(self.player.position, dt)

    def _update_projectiles(self, dt: float):
        """Update projectiles and check collisions"""
        for projectile in self.projectiles:
            projectile.update(dt)

            # Check hits on enemies
            for enemy in self.enemies[:]:  # Copy list in case we remove
                if projectile.check_enemy_hit(enemy):
                    # Hit! Remove projectile
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
                    break

    def _integrate_all_objects(self, dt: float):
        """Integrate velocity and position for all dynamic objects"""
        all_dynamics = []

        if self.player:
            all_dynamics.append(self.player)

        all_dynamics.extend(self.enemies)
        all_dynamics.extend(self.projectiles)

        for obj in all_dynamics:
            obj.integrate_velocity(dt, self.damping)
            obj.integrate_position(dt)

            # Clamp velocity to maximum
            self.constraint_system.clamp_velocity_magnitude(obj, self.max_velocity)

    def _apply_constraints(self, dt: float):
        """Apply constraints like ground collision"""
        # All dynamic objects constrained to ground at y=0
        if self.player:
            self.constraint_system.constrain_to_ground(self.player)

        for enemy in self.enemies:
            self.constraint_system.constrain_to_ground(enemy)

        for projectile in self.projectiles:
            self.constraint_system.constrain_to_ground(projectile)

    def _resolve_collisions(self):
        """Resolve collisions between dynamic objects"""
        all_dynamics = []

        if self.player:
            all_dynamics.append(self.player)

        all_dynamics.extend(self.enemies)
        all_dynamics.extend(self.projectiles)

        self.collision_system.resolve_collisions(all_dynamics)

    def _cleanup(self):
        """Remove dead enemies and expired projectiles"""
        # Remove dead enemies
        self.enemies = [e for e in self.enemies if e.is_alive()]

        # Remove expired projectiles
        self.projectiles = [p for p in self.projectiles if not p.is_expired()]

    def _update_metrics(self):
        """
        Update simulation metrics

        FIX: Gap 5 - Consistent population (excluding static_objects for now)
        """
        # Object count
        self.metrics['object_count'] = (
            (1 if self.player else 0) +
            len(self.enemies) +
            len(self.projectiles)
        )

        # Kinetic energy (sum of 0.5*m*v^2 for all dynamics)
        total_energy = 0.0
        all_dynamics = []

        if self.player:
            all_dynamics.append(self.player)

        all_dynamics.extend(self.enemies)
        all_dynamics.extend(self.projectiles)

        for obj in all_dynamics:
            total_energy += obj.get_kinetic_energy()

        self.metrics['physics_energy'] = total_energy

        # Average velocity
        if all_dynamics:
            total_velocity = sum(obj.velocity.magnitude() for obj in all_dynamics)
            self.metrics['average_velocity'] = total_velocity / len(all_dynamics)
        else:
            self.metrics['average_velocity'] = 0.0

    def get_metrics(self) -> Dict[str, float]:
        """Return current simulation metrics"""
        return self.metrics.copy()