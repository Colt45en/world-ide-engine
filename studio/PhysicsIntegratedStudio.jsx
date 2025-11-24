/**
 * PhysicsIntegratedStudio.jsx - Studio Shell with Physics Integration
 * 
 * This shows how to integrate the usePhysicsAPI hook into your existing
 * World Engine Studio. Just import and use in your App component.
 */

import React, { useEffect, useState } from "react";
import { usePhysicsSimulation } from "./usePhysicsAPI";

/**
 * PhysicsPanel Component
 * Displays physics simulation state and controls
 */
export const PhysicsPanel = () => {
  const {
    isConnected,
    physicsState,
    entities,
    loading,
    spawnBody,
    stepSimulation,
    resetSimulation,
  } = usePhysicsSimulation();

  const [autoStep, setAutoStep] = useState(false);

  // Auto-step physics at 30 FPS
  useEffect(() => {
    if (!autoStep) return;
    
    const interval = setInterval(() => {
      stepSimulation();
    }, 33); // ~30 FPS

    return () => clearInterval(interval);
  }, [autoStep, stepSimulation]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded p-4 space-y-3">
      {/* Connection Status */}
      <div className="flex items-center gap-2">
        <div
          className={`w-3 h-3 rounded-full ${
            isConnected ? "bg-emerald-500" : "bg-rose-500"
          }`}
        />
        <span className="text-xs text-slate-400">
          Physics API: {isConnected ? "Connected" : "Offline"}
        </span>
      </div>

      {/* Physics State */}
      {physicsState && (
        <div className="space-y-2 text-xs font-mono">
          <div className="flex justify-between">
            <span className="text-slate-500">FRAME</span>
            <span className="text-cyan-400">{physicsState.frame}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">KINETIC ENERGY</span>
            <span className="text-cyan-400">
              {physicsState.total_kinetic_energy.toFixed(2)} J
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">COLLISIONS</span>
            <span className="text-cyan-400">{physicsState.collision_count}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">BODIES</span>
            <span className="text-cyan-400">{physicsState.entities_count}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">TIME</span>
            <span className="text-cyan-400">
              {physicsState.timestamp.toFixed(2)}s
            </span>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="space-y-2">
        <button
          onClick={() =>
            spawnBody(
              {
                x: (Math.random() - 0.5) * 10,
                y: 5,
                z: (Math.random() - 0.5) * 10,
              },
              `Body_${Date.now()}`
            )
          }
          disabled={!isConnected || loading}
          className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-700 text-white text-xs font-bold rounded transition"
        >
          {loading ? "..." : "SPAWN BODY"}
        </button>

        <button
          onClick={() => setAutoStep(!autoStep)}
          className={`w-full py-2 text-white text-xs font-bold rounded transition ${
            autoStep
              ? "bg-emerald-600 hover:bg-emerald-500"
              : "bg-slate-700 hover:bg-slate-600"
          }`}
        >
          {autoStep ? "RUNNING" : "START SIM"}
        </button>

        <button
          onClick={stepSimulation}
          disabled={!isConnected || autoStep || loading}
          className="w-full py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 text-slate-400 text-xs font-bold rounded transition"
        >
          STEP
        </button>

        <button
          onClick={resetSimulation}
          className="w-full py-2 bg-rose-900/30 hover:bg-rose-900/50 text-rose-400 text-xs font-bold rounded transition border border-rose-900"
        >
          RESET
        </button>
      </div>

      {/* Entity List */}
      {entities.length > 0 && (
        <div className="border-t border-slate-800 pt-2">
          <h4 className="text-[10px] font-bold text-slate-500 uppercase mb-2">
            Entities ({entities.length})
          </h4>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {entities.map((entity) => (
              <div
                key={entity.id}
                className="text-[10px] font-mono bg-slate-800/50 p-1 rounded border border-slate-700"
              >
                <div className="flex justify-between">
                  <span className="text-cyan-400">{entity.label}</span>
                  <span className="text-slate-500">ID: {entity.id}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>
                    Pos: ({entity.position.x.toFixed(1)}, {entity.position.y.toFixed(1)})
                  </span>
                  <span>KE: {entity.kinetic_energy.toFixed(1)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Integration Example: Add to your Studio App
 * 
 * In your main Studio App component, add this to the sidebar or 
 * performance panel:
 * 
 *   <PhysicsPanel />
 * 
 * Or wire physics state into terminal commands:
 */
export const physicsTerminalCommands = (utils) => {
  const { spawnBody, stepSimulation, physicsState } = utils;

  return {
    "physics:spawn": async (args) => {
      const [x = 0, y = 5, z = 0] = args.map(Number);
      await spawnBody({ x, y, z }, `Spawned_${Date.now()}`);
      return `Spawned physics body at (${x}, ${y}, ${z})`;
    },

    "physics:step": async () => {
      await stepSimulation();
      return `Physics stepped. Frame: ${physicsState?.frame || "?"}, KE: ${physicsState?.total_kinetic_energy?.toFixed(2) || "?"}`;
    },

    "physics:state": async () => {
      if (!physicsState) return "No physics state available";
      return `
Frame: ${physicsState.frame}
Kinetic Energy: ${physicsState.total_kinetic_energy.toFixed(2)} J
Collisions: ${physicsState.collision_count}
Bodies: ${physicsState.entities_count}
Time: ${physicsState.timestamp.toFixed(2)}s
      `;
    },
  };
};

/**
 * Hook Physics Entities into Node Graph
 * 
 * This function converts physics bodies to visual nodes
 * for your canvas-based node graph.
 */
export const mapPhysicsToNodes = (entities) => {
  return entities.map((entity) => ({
    id: entity.id,
    label: entity.label,
    // Scale physics coordinates to canvas (assuming 800x600 canvas centered)
    x: 400 + entity.position.x * 30,
    y: 300 - entity.position.y * 30,
    // Velocity as visual movement
    vx: entity.velocity.x * 0.5,
    vy: -entity.velocity.y * 0.5,
    radius: Math.max(3, entity.radius * 2),
    // Color by kinetic energy
    type:
      entity.kinetic_energy > 10
        ? "energetic"
        : entity.kinetic_energy > 1
        ? "active"
        : "idle",
    // Show collision count as visual indicator
    collisions: entity.collision_count,
    selected: false,
  }));
};

