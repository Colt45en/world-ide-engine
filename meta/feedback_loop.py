"""Recursive Feedback Loop System

Enables self-correcting orchestration through feedback cycles:
1. Orchestration produces: decision + embeddings + parameters
2. Feedback converter transforms outputs back to text
3. Text fed back to orchestrator as next input
4. System converges or diverges over N cycles
5. History tracked for analysis
"""

from meta.orchestrator_v2 import MetaOrchestrator


class FeedbackLoop:
    """Manages recursive orchestration feedback cycles."""
    
    def __init__(self, max_cycles: int = 5):
        self.orchestrator = MetaOrchestrator()
        self.max_cycles = max_cycles
        self.history: list[dict] = []
        self.current_cycle = 0
        
    def outputs_to_text(self, state: dict) -> str:
        """Convert orchestrator outputs back to text for feedback.
        
        Maps:
        - decision → action verb (aggressive→amplify, balanced→adjust, gentle→refine)
        - embeddings → adjective list
        - physics parameters → numeric descriptors
        - colors → color names
        """
        decision = state.get("decision", "balanced")
        embeddings = state.get("embeddings", [])
        physics_params = state.get("physics_params", {})
        colors = state.get("colors", {})
        
        # Decision → action verb
        action_map = {
            "aggressive": "amplify",
            "balanced": "adjust",
            "gentle": "refine"
        }
        action = action_map.get(decision, "process")
        
        # Embeddings → adjectives (first 3)
        adjectives = []
        if embeddings:
            if embeddings[0] > 0.7:
                adjectives.append("intense")
            if embeddings[1] > 0.6 if len(embeddings) > 1 else False:
                adjectives.append("dynamic")
            if embeddings[2] < 0.3 if len(embeddings) > 2 else False:
                adjectives.append("subtle")
        
        # Physics → numeric descriptor
        mass = physics_params.get("mass", 1.0)
        velocity = physics_params.get("velocity", (1.0,))
        vel_mag = velocity[0] if isinstance(velocity, (tuple, list)) else velocity
        
        if mass > 2.0:
            mass_desc = "heavy"
        elif mass < 0.5:
            mass_desc = "light"
        else:
            mass_desc = "medium"
        
        if vel_mag > 3.0:
            vel_desc = "high-speed"
        elif vel_mag < 1.0:
            vel_desc = "low-speed"
        else:
            vel_desc = "moderate-speed"
        
        # Build feedback text
        adj_str = " ".join(adjectives) if adjectives else "balanced"
        feedback_text = f"{action} {adj_str} {mass_desc} {vel_desc} system with physics"
        
        return feedback_text
    
    def run_feedback_loop(self, initial_input: str) -> dict:
        """Execute recursive feedback cycles.
        
        Args:
            initial_input: Starting text for orchestration
            
        Returns:
            Dictionary with cycle history and convergence analysis
        """
        print("\n" + "=" * 80)
        print(f"FEEDBACK LOOP: {self.max_cycles} CYCLES")
        print("=" * 80)
        
        current_input = initial_input
        
        for cycle_num in range(self.max_cycles):
            self.current_cycle = cycle_num + 1
            
            print(f"\n[CYCLE {self.current_cycle}]")
            print(f"  Input: {current_input}")
            
            # Orchestrate
            state = self.orchestrator.orchestrate(current_input)
            
            # Record cycle
            cycle_record = {
                "cycle": self.current_cycle,
                "input": current_input,
                "decision": state.get("decision", "unknown"),
                "embeddings": state.get("embeddings", []),
                "mass": state.get("physics_params", {}).get("mass", 0),
                "velocity": state.get("physics_params", {}).get("velocity", (0,)),
            }
            self.history.append(cycle_record)
            
            print(f"  Decision: {cycle_record['decision']}")
            
            # Calculate feedback for next cycle
            if cycle_num < self.max_cycles - 1:
                current_input = self.outputs_to_text(state)
            else:
                print(f"  [FINAL CYCLE - No feedback generated]")
        
        # Analyze convergence
        decisions = [h["decision"] for h in self.history]
        unique_decisions = len(set(decisions))
        
        print(f"\n" + "-" * 80)
        print("CONVERGENCE ANALYSIS")
        print("-" * 80)
        print(f"  Total cycles: {len(self.history)}")
        print(f"  Unique decisions: {unique_decisions}")
        print(f"  Decision sequence: {' → '.join(decisions)}")
        
        if unique_decisions == 1:
            print(f"  Status: ✓ CONVERGED to '{decisions[0]}'")
            convergence = "converged"
        elif unique_decisions == len(decisions):
            print(f"  Status: ✗ DIVERGING (all different)")
            convergence = "diverging"
        else:
            print(f"  Status: ~ OSCILLATING ({unique_decisions} states)")
            convergence = "oscillating"
        
        # Physics parameter evolution
        print(f"\n  Physics evolution:")
        for i, record in enumerate(self.history, 1):
            vel = record["velocity"]
            vel_mag = vel[0] if isinstance(vel, (tuple, list)) else vel
            print(f"    Cycle {i}: mass={record['mass']:.3f}, velocity={vel_mag:.3f} m/s")
        
        return {
            "history": self.history,
            "convergence": convergence,
            "final_decision": decisions[-1],
            "unique_decisions": unique_decisions,
        }


def demo_feedback_loop():
    """Demonstrate recursive feedback loop."""
    
    loop = FeedbackLoop(max_cycles=5)
    
    result = loop.run_feedback_loop("aggressive physics simulation")
    
    print("\n" + "=" * 80)
    print("FEEDBACK LOOP COMPLETE")
    print("=" * 80)
    print(f"\nFinal state:")
    print(f"  Decision: {result['final_decision']}")
    print(f"  Convergence: {result['convergence']}")
    print(f"  Cycles executed: {len(result['history'])}")
    
    return result


if __name__ == "__main__":
    demo_feedback_loop()
