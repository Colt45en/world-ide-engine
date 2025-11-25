import sys
sys.path.insert(0, 'C:\\\\fresh-world-engine')

from physics.body import RigidBody, Vec3, Quat
from physics.gjk import BoxCollider
from physics.solver import PhysicsWorld
from graphics.cad_renderer import CADRenderer, Vec3 as RendererVec3

def demo_physics_with_rendering():
    world = PhysicsWorld(gravity=Vec3(0, -9.81, 0))
    
    ground = RigidBody(Vec3(0, -2, 0), mass=0)
    ground_collider = BoxCollider((0, -2, 0), (10, 0.5, 10))
    ground.collider = ground_collider
    world.addBody(ground)
    
    box1 = RigidBody(Vec3(-3, 5, 0), mass=1.0)
    box1.setBoxInertia(1, 1, 1)
    box1_collider = BoxCollider((-3, 5, 0), (0.5, 0.5, 0.5))
    box1.collider = box1_collider
    box1.velocity = Vec3(3, 0, 0)
    world.addBody(box1)
    
    box2 = RigidBody(Vec3(3, 5, 0), mass=1.0)
    box2.setBoxInertia(1, 1, 1)
    box2_collider = BoxCollider((3, 5, 0), (0.5, 0.5, 0.5))
    box2.collider = box2_collider
    box2.velocity = Vec3(-3, 0, 0)
    world.addBody(box2)
    
    renderer = CADRenderer()
    
    print("=== Physics Integration Demo ===")
    print("Simulating two colliding cubes for 300 frames...")
    print()
    
    for frame in range(300):
        world.update(1.0 / 60.0)
        
        if frame % 60 == 0:
            print(f"Frame {frame}:")
            for i, body in enumerate(world.getBodies()):
                if body.inv_mass > 0:
                    print(f"  Body {i}: pos=({body.position.x:.2f}, {body.position.y:.2f}, {body.position.z:.2f}), "
                          f"vel=({body.velocity.x:.2f}, {body.velocity.y:.2f}, {body.velocity.z:.2f}), "
                          f"ang_vel=({body.angular_velocity.x:.2f}, {body.angular_velocity.y:.2f}, {body.angular_velocity.z:.2f})")
            print()
    
    print("Rendering collision state in CAD multi-view...")
    
    for body in world.getBodies():
        if body.inv_mass > 0:
            transform_pos = RendererVec3(body.position.x, body.position.y, body.position.z)
            
            R = body.orientation.toMat3()
            from graphics.cad_renderer import Mat4, Quat as RendererQuat
            
            quat = RendererQuat(body.orientation.w, body.orientation.x, body.orientation.y, body.orientation.z)
            
            print(f"Body at {transform_pos.x:.2f}, {transform_pos.y:.2f}, {transform_pos.z:.2f}")
            print(f"  Orientation: w={quat.w:.2f}, x={quat.x:.2f}, y={quat.y:.2f}, z={quat.z:.2f}")
            
            output = renderer.renderCAD([
                (transform_pos, (0.5, 0.5, 0.5), quat)
            ])
            
            if output:
                for viewport_name, projection_data in output.items():
                    print(f"  {viewport_name}: {len(projection_data)} vertices visible")

if __name__ == '__main__':
    demo_physics_with_rendering()
