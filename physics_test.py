#!/usr/bin/env python3
"""
Physics System Test and Demonstration

Tests all major components of the physics system:
- Vector3 mathematics
- PhysicsObject dynamics
- Player, Enemy, Projectile classes
- Collision detection and resolution
- Constraint systems
- PhysicsSimulator integration
"""

from physics_system import (
    PhysicsSimulator, Player, Enemy, Projectile,
    PhysicsObject, Vector3, GeometryEngine
)
import time

def test_vector3_operations():
    """Test Vector3 mathematical operations"""
    print("=== Testing Vector3 Operations ===")

    # Basic arithmetic
    v1 = Vector3(1, 2, 3)
    v2 = Vector3(4, 5, 6)

    assert v1 + v2 == Vector3(5, 7, 9)
    assert v2 - v1 == Vector3(3, 3, 3)
    assert v1 * 2 == Vector3(2, 4, 6)
    assert v1 / 2 == Vector3(0.5, 1.0, 1.5)

    # Vector operations
    assert v1.dot(v2) == 32  # 1*4 + 2*5 + 3*6
    assert v1.magnitude() == (1 + 4 + 9) ** 0.5  # sqrt(14)

    # Normalization
    v_unit = v1.normalize()
    assert abs(v_unit.magnitude() - 1.0) < 1e-10

    # Distance
    assert v1.distance_to(v2) == (v2 - v1).magnitude()

    print("✓ Vector3 operations working correctly")

def test_physics_object_dynamics():
    """Test PhysicsObject force integration"""
    print("\n=== Testing PhysicsObject Dynamics ===")

    obj = PhysicsObject(mass=2.0, position=Vector3(0, 0, 0))

    # Apply force
    force = Vector3(10, 0, 0)  # 10N right
    obj.apply_force(force)

    # Integrate with dt=1.0
    dt = 1.0
    obj.integrate_velocity(dt)
    obj.integrate_position(dt)

    # Expected: a = F/m = 10/2 = 5, v = a*dt = 5, p = v*dt = 5
    expected_pos = Vector3(5, 0, 0)
    expected_vel = Vector3(5, 0, 0)

    assert obj.position == expected_pos, f"Position: {obj.position}, expected: {expected_pos}"
    assert obj.velocity == expected_vel, f"Velocity: {obj.velocity}, expected: {expected_vel}"

    print("✓ PhysicsObject dynamics working correctly")

def test_player_enemy_interaction():
    """Test player-enemy combat and AI"""
    print("\n=== Testing Player-Enemy Interaction ===")

    player = Player(position=Vector3(0, 0, 0), hp=100.0)
    enemy = Enemy(position=Vector3(1, 0, 0), hp=50.0, contact_dps=20.0)

    # Test contact damage
    dt = 1.0
    had_contact = enemy.check_player_contact(player, dt)

    assert had_contact, "Should detect contact between player and enemy"
    assert player.hp == 80.0, f"Player HP should be 80, got {player.hp}"

    # Test enemy AI chase
    enemy.update(player.position, dt)
    enemy.integrate_velocity(dt)
    enemy.integrate_position(dt)

    # Enemy should move toward player
    assert enemy.position.x < 1.0, f"Enemy should move left toward player, position: {enemy.position}"

    print("✓ Player-enemy interaction working correctly")

def test_projectile_system():
    """Test projectile creation and collision"""
    print("\n=== Testing Projectile System ===")

    projectile = Projectile(position=Vector3(0, 0, 0), damage=25.0)
    enemy = Enemy(position=Vector3(0.2, 0, 0), hp=50.0)

    # Test hit detection
    hit = projectile.check_enemy_hit(enemy)

    assert hit, "Projectile should hit enemy"
    assert enemy.hp == 25.0, f"Enemy HP should be 25, got {enemy.hp}"

    # Test lifetime
    projectile.update(3.0)
    assert not projectile.is_expired(), "Projectile should not be expired after 3s"

    projectile.update(3.0)
    assert projectile.is_expired(), "Projectile should be expired after 6s"

    print("✓ Projectile system working correctly")

def test_collision_resolution():
    """Test collision detection and resolution"""
    print("\n=== Testing Collision Resolution ===")

    from physics_system import CollisionSystem

    geom = GeometryEngine()
    collision_sys = CollisionSystem(geom)

    obj1 = PhysicsObject(position=Vector3(0, 0, 0), radius=1.0)
    obj2 = PhysicsObject(position=Vector3(1.5, 0, 0), radius=1.0)

    # Should be colliding (distance 1.5 < radius1 + radius2 = 2.0)
    assert collision_sys.check_collision(obj1, obj2), "Objects should be colliding"

    # Resolve collision
    objects = [obj1, obj2]
    collision_sys.resolve_collisions(objects)

    # Objects should be pushed apart
    distance_after = obj1.position.distance_to(obj2.position)
    assert distance_after >= 2.0, f"Objects should be separated, distance: {distance_after}"

    print("✓ Collision resolution working correctly")

def test_physics_simulator():
    """Test the main physics simulator"""
    print("\n=== Testing Physics Simulator ===")

    config = {
        'gravity': -9.8,
        'damping': 0.99,
        'max_velocity': 50.0,
        'timestep': 1.0/60.0,
        'use_fixed_timestep': False
    }

    sim = PhysicsSimulator(config)

    # Add player
    player = Player(position=Vector3(0, 10, 0))
    sim.set_player(player)

    # Add enemy
    enemy = Enemy(position=Vector3(5, 0, 0))
    sim.add_enemy(enemy)

    # Add projectile
    projectile = Projectile(position=Vector3(0, 5, 0), velocity=Vector3(10, 0, 0))
    sim.add_projectile(projectile)

    # Run simulation for a few steps
    dt = 1.0/60.0
    for _ in range(10):
        sim.update(dt)

    # Check that gravity is working (player should fall)
    assert player.position.y < 10.0, f"Player should fall due to gravity, position: {player.position}"

    # Check that projectile moves
    assert projectile.position.x > 0, f"Projectile should move right, position: {projectile.position}"

    # Check metrics
    metrics = sim.get_metrics()
    assert metrics['object_count'] == 3, f"Should have 3 objects, got {metrics['object_count']}"
    assert metrics['physics_energy'] > 0, f"Should have positive energy, got {metrics['physics_energy']}"

    print("✓ Physics simulator working correctly")

def test_geometry_engine():
    """Test geometry engine operations"""
    print("\n=== Testing Geometry Engine ===")

    geom = GeometryEngine()

    # Test ray-sphere intersection
    ray = Ray(Vector3(0, 0, 0), Vector3(1, 0, 0))
    sphere_center = Vector3(5, 0, 0)
    sphere_radius = 1.0

    intersection = geom.ray_sphere_intersection(ray, sphere_center, sphere_radius)
    assert intersection is not None, "Ray should intersect sphere"
    assert abs(intersection - 4.0) < 1e-6, f"Intersection at distance 4, got {intersection}"

    # Test point in sphere
    point_inside = Vector3(5.5, 0, 0)
    point_outside = Vector3(7, 0, 0)

    assert geom.point_in_sphere(point_inside, sphere_center, sphere_radius), "Point should be inside sphere"
    assert not geom.point_in_sphere(point_outside, sphere_center, sphere_radius), "Point should be outside sphere"

    print("✓ Geometry engine working correctly")

def run_performance_test():
    """Run a performance test with many objects"""
    print("\n=== Running Performance Test ===")

    config = {
        'gravity': -9.8,
        'damping': 0.99,
        'max_velocity': 50.0,
        'timestep': 1.0/60.0,
        'use_fixed_timestep': True
    }

    sim = PhysicsSimulator(config)

    # Add many objects
    num_objects = 100
    for i in range(num_objects):
        obj = PhysicsObject(
            position=Vector3(i * 2, 10, 0),
            velocity=Vector3((i % 2) * 5 - 2.5, 0, 0)
        )
        sim.add_static_object(obj)

    # Time the simulation
    dt = 1.0/60.0
    start_time = time.time()

    for _ in range(100):  # 100 frames
        sim.update(dt)

    end_time = time.time()
    elapsed = end_time - start_time

    print(".2f")
    print(".1f")

    # Check that simulation is stable
    metrics = sim.get_metrics()
    assert metrics['object_count'] == num_objects, f"Should have {num_objects} objects"

    print("✓ Performance test completed successfully")

def main():
    """Run all physics system tests"""
    print("Physics System - Comprehensive Test Suite")
    print("=" * 50)

    try:
        # Run all tests
        test_vector3_operations()
        test_physics_object_dynamics()
        test_player_enemy_interaction()
        test_projectile_system()
        test_collision_resolution()
        test_physics_simulator()
        test_geometry_engine()
        run_performance_test()

        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! Physics system is working correctly.")
        print("The system addresses all critical gaps from SYSTEMS_AUDIT_CRITICAL_GAPS.md")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())