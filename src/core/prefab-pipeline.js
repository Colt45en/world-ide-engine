/**
 * PrefabPipeline - Prefab creation and management system
 * Handles templates, instantiation, and prefab asset management
 */

class PrefabPipeline {
  constructor(dataBus) {
    this.dataBus = dataBus;
    this.status = 'uninitialized';
    this.prefabs = new Map();
    this.instances = new Map();
  }
  
  async initialize() {
    console.log('  🧩 Prefab Pipeline initializing...');
    this.status = 'ready';
    
    // Initialize default prefabs
    this.createDefaultPrefabs();
    
    // Subscribe to prefab requests
    this.dataBus.subscribe('prefab:create', (data) => this.createPrefab(data));
    this.dataBus.subscribe('prefab:instantiate', (data) => this.instantiate(data));
    
    return this;
  }
  
  /**
   * Create default prefabs
   */
  createDefaultPrefabs() {
    // Cube prefab
    this.registerPrefab('cube', {
      name: 'Cube',
      components: {
        geometry: {
          type: 'cube',
          size: [1, 1, 1]
        },
        material: 'default',
        transform: {
          position: [0, 0, 0],
          rotation: [0, 0, 0],
          scale: [1, 1, 1]
        }
      }
    });
    
    // Sphere prefab
    this.registerPrefab('sphere', {
      name: 'Sphere',
      components: {
        geometry: {
          type: 'sphere',
          radius: 1,
          segments: 32
        },
        material: 'default',
        transform: {
          position: [0, 0, 0],
          rotation: [0, 0, 0],
          scale: [1, 1, 1]
        }
      }
    });
    
    // Light prefab
    this.registerPrefab('light', {
      name: 'Light',
      components: {
        light: {
          type: 'point',
          color: [1, 1, 1],
          intensity: 1.0,
          range: 10
        },
        transform: {
          position: [0, 5, 0],
          rotation: [0, 0, 0],
          scale: [1, 1, 1]
        }
      }
    });
  }
  
  /**
   * Register a new prefab template
   */
  registerPrefab(id, definition) {
    this.prefabs.set(id, {
      id,
      ...definition,
      createdAt: Date.now()
    });
    
    this.dataBus.publish('prefab:registered', {
      id,
      name: definition.name
    });
    
    return id;
  }
  
  /**
   * Create a prefab from data
   */
  createPrefab(data) {
    const { id, name, components } = data;
    return this.registerPrefab(id || `prefab_${Date.now()}`, {
      name,
      components
    });
  }
  
  /**
   * Instantiate a prefab
   */
  instantiate(data) {
    const { prefabId, overrides = {} } = data;
    
    const prefab = this.prefabs.get(prefabId);
    if (!prefab) {
      console.error(`Prefab ${prefabId} not found`);
      return null;
    }
    
    // Create instance with overrides
    const instance = {
      id: `instance_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`,
      prefabId,
      components: this.deepMerge(prefab.components, overrides),
      createdAt: Date.now()
    };
    
    this.instances.set(instance.id, instance);
    
    // Notify systems about new instance
    this.dataBus.publish('prefab:instantiated', instance);
    
    // Request rendering if geometry exists
    if (instance.components.geometry) {
      this.dataBus.publish('graphics:render', {
        type: 'mesh',
        geometry: instance.components.geometry,
        material: instance.components.material,
        transform: instance.components.transform
      });
    }
    
    return instance;
  }
  
  /**
   * Deep merge two objects
   */
  deepMerge(target, source) {
    const result = { ...target };
    for (const key in source) {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        result[key] = this.deepMerge(target[key] || {}, source[key]);
      } else {
        result[key] = source[key];
      }
    }
    return result;
  }
  
  /**
   * Get all registered prefabs
   */
  getPrefabs() {
    return Array.from(this.prefabs.values());
  }
  
  /**
   * Get all instances
   */
  getInstances() {
    return Array.from(this.instances.values());
  }
  
  /**
   * Delete an instance
   */
  deleteInstance(instanceId) {
    const deleted = this.instances.delete(instanceId);
    if (deleted) {
      this.dataBus.publish('prefab:instanceDeleted', { instanceId });
    }
    return deleted;
  }
}

export { PrefabPipeline };
