import math
from typing import List, Tuple, Optional
from physics.body import RigidBody, Vec3
from physics.epa import ContactInfo

class CollisionSolver:
    def __init__(self):
        self.contacts: List[ContactInfo] = []
        self.friction_coefficient = 0.4
        self.restitution = 0.6

    def addContact(self, contact: ContactInfo):
        self.contacts.append(contact)

    def clearContacts(self):
        self.contacts = []

    def _resolveContact(self, body_a: RigidBody, body_b: RigidBody, contact: ContactInfo):
        normal = Vec3(contact.normal[0], contact.normal[1], contact.normal[2])
        contact_point_a = Vec3(contact.world_point_a[0], contact.world_point_a[1], contact.world_point_a[2])
        contact_point_b = Vec3(contact.world_point_b[0], contact.world_point_b[1], contact.world_point_b[2])
        
        r_a = contact_point_a - body_a.position
        r_b = contact_point_b - body_b.position
        
        v_a = body_a.velocity + body_a.angular_velocity.cross(r_a)
        v_b = body_b.velocity + body_b.angular_velocity.cross(r_b)
        
        relative_velocity = v_a - v_b
        velocity_along_normal = relative_velocity.dot(normal)
        
        if velocity_along_normal >= 0:
            return
        
        r_a_cross_n = r_a.cross(normal)
        r_b_cross_n = r_b.cross(normal)
        
        inv_inertia_a_component = body_a.inv_inertia_world * r_a_cross_n
        inv_inertia_b_component = body_b.inv_inertia_world * r_b_cross_n
        
        inv_inertia_a_n = inv_inertia_a_component.cross(r_a)
        inv_inertia_b_n = inv_inertia_b_component.cross(r_b)
        
        effective_mass = body_a.inv_mass + body_b.inv_mass
        effective_mass += inv_inertia_a_n.dot(normal)
        effective_mass += inv_inertia_b_n.dot(normal)
        
        if effective_mass < 1e-6:
            return
        
        restitution = self.restitution
        impulse_magnitude = -(1.0 + restitution) * velocity_along_normal / effective_mass
        
        impulse = normal * impulse_magnitude
        
        body_a.applyImpulse(impulse * -1.0, contact_point_a)
        body_b.applyImpulse(impulse, contact_point_b)

    def solve(self, bodies: List[RigidBody]):
        for contact in self.contacts:
            body_a = contact.body_a
            body_b = contact.body_b
            self._resolveContact(body_a, body_b, contact)

class PhysicsWorld:
    def __init__(self, gravity: Vec3 = None):
        self.bodies: List[RigidBody] = []
        self.solver = CollisionSolver()
        self.gravity = gravity or Vec3(0, -9.81, 0)
        self.dt = 1.0 / 60.0

    def addBody(self, body: RigidBody):
        self.bodies.append(body)

    def removeBody(self, body: RigidBody):
        if body in self.bodies:
            self.bodies.remove(body)

    def update(self, dt: Optional[float] = None):
        if dt is None:
            dt = self.dt
        
        for body in self.bodies:
            body.gravity = self.gravity
            body.integrate(dt)
            body.setWorldCollider()
        
        self.detectCollisions()
        self.solver.solve(self.bodies)
        self.solver.clearContacts()

    def detectCollisions(self):
        from physics.gjk import GJK
        from physics.epa import EPA
        
        gjk = GJK()
        epa = EPA()
        
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                body_a = self.bodies[i]
                body_b = self.bodies[j]
                
                if body_a.collider is None or body_b.collider is None:
                    continue
                
                if gjk.colliding(body_a.collider, body_b.collider):
                    simplex = gjk.getSimplex()
                    contact = epa.expand(simplex, body_a.collider, body_b.collider)
                    
                    if contact:
                        contact.body_a = body_a
                        contact.body_b = body_b
                        self.solver.addContact(contact)

    def getBodies(self):
        return self.bodies

    def getBodyAt(self, position: Vec3, radius: float = 1.0) -> Optional[RigidBody]:
        for body in self.bodies:
            dist = (body.position - position).length()
            if dist < radius:
                return body
        return None
