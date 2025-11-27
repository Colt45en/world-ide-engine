/**
 * usePhysicsAPI.js - React hooks to connect Studio with Nexus Physics API
 * Handles: spawning bodies, stepping simulation, fetching state
 */

import { useState, useEffect, useCallback } from "react";

const API_URL = process.env.REACT_APP_PHYSICS_API || "http://localhost:8001";

export const usePhysicsSimulation = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [physicsState, setPhysicsState] = useState(null);
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_URL}/health`);
        if (res.ok) {
          setIsConnected(true);
        }
      } catch (e) {
        console.warn("Physics API not available:", e.message);
        setIsConnected(false);
      }
    };
    
    checkHealth();
    const interval = setInterval(checkHealth, 5000); // Ping every 5s
    return () => clearInterval(interval);
  }, []);

  // Fetch current state
  const fetchState = useCallback(async () => {
    if (!isConnected) return;
    try {
      const res = await fetch(`${API_URL}/physics/state`);
      const data = await res.json();
      if (data.success) {
        setPhysicsState(data.state);
      }
    } catch (e) {
      setError(e.message);
    }
  }, [isConnected]);

  // Fetch entities
  const fetchEntities = useCallback(async () => {
    if (!isConnected) return;
    try {
      const res = await fetch(`${API_URL}/physics/entities`);
      const data = await res.json();
      if (data.success) {
        setEntities(data.entities);
      }
    } catch (e) {
      setError(e.message);
    }
  }, [isConnected]);

  // Spawn a physics body
  const spawnBody = useCallback(
    async (position, label = "Body", options = {}) => {
      if (!isConnected) return null;
      
      setLoading(true);
      try {
        const res = await fetch(`${API_URL}/physics/spawn`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            position,
            label,
            mass: options.mass || 1.0,
            radius: options.radius || 1.0,
            is_static: options.is_static || false,
            restitution: options.restitution || 0.8,
          }),
        });
        
        const data = await res.json();
        if (data.success) {
          await fetchEntities();
          return data.body;
        }
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    },
    [isConnected, fetchEntities]
  );

  // Step the simulation
  const stepSimulation = useCallback(async () => {
    if (!isConnected) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/physics/step`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dt: null }),
      });
      
      const data = await res.json();
      if (data.success) {
        setPhysicsState(data.state);
        await fetchEntities();
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [isConnected, fetchEntities]);

  // Reset simulation
  const resetSimulation = useCallback(async () => {
    if (!isConnected) return;
    try {
      const res = await fetch(`${API_URL}/physics/reset`, {
        method: "POST",
      });
      const data = await res.json();
      if (data.success) {
        setEntities([]);
        setPhysicsState(null);
      }
    } catch (e) {
      setError(e.message);
    }
  }, [isConnected]);

  return {
    isConnected,
    physicsState,
    entities,
    loading,
    error,
    fetchState,
    fetchEntities,
    spawnBody,
    stepSimulation,
    resetSimulation,
  };
};

// Integration with Keeper Nexus API
export const applyPhysicsProphecy = async (prophecy) => {
  try {
    const res = await fetch(`${API_URL}/prophecy/apply_physics`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prophecy }),
    });
    return await res.json();
  } catch (e) {
    console.error("Prophecy application failed:", e);
    return null;
  }
};
