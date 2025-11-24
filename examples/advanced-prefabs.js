/**
 * Example: Advanced Prefab System
 * Demonstrates complex prefab creation, inheritance, and scene building
 */

import { WorldEngine } from '../src/index.js';

async function advancedPrefabExample() {
  console.log('=== Advanced Prefab System Example ===\n');
  
  const engine = new WorldEngine();
  await engine.initialize();
  
  // Create a building prefab with multiple components
  console.log('1. Creating complex building prefab...');
  engine.prefabPipeline.registerPrefab('office-building', {
    name: 'Office Building',
    components: {
      geometry: {
        type: 'cube',
        size: [10, 20, 10]
      },
      material: 'default',
      transform: {
        position: [0, 10, 0],
        rotation: [0, 0, 0],
        scale: [1, 1, 1]
      },
      metadata: {
        floors: 5,
        windows: 40,
        doors: 2
      }
    }
  });
  
  // Create a street light prefab
  console.log('2. Creating street light prefab...');
  engine.prefabPipeline.registerPrefab('street-light', {
    name: 'Street Light',
    components: {
      light: {
        type: 'point',
        color: [1, 0.9, 0.7],
        intensity: 3.0,
        range: 15
      },
      geometry: {
        type: 'cylinder',
        radius: 0.2,
        height: 5
      },
      transform: {
        position: [0, 2.5, 0],
        rotation: [0, 0, 0],
        scale: [1, 1, 1]
      }
    }
  });
  
  // Create a vehicle prefab
  console.log('3. Creating vehicle prefab...');
  engine.prefabPipeline.registerPrefab('car', {
    name: 'Car',
    components: {
      geometry: {
        type: 'cube',
        size: [2, 1, 4]
      },
      material: 'custom-metal',
      transform: {
        position: [0, 0.5, 0],
        rotation: [0, 0, 0],
        scale: [1, 1, 1]
      },
      physics: {
        mass: 1200,
        velocity: [0, 0, 0]
      }
    }
  });
  
  // Build a city scene
  console.log('\n4. Building city scene...');
  const sceneObjects = [];
  
  // Add buildings in a grid
  for (let x = -20; x <= 20; x += 15) {
    for (let z = -20; z <= 20; z += 15) {
      const building = engine.prefabPipeline.instantiate({
        prefabId: 'office-building',
        overrides: {
          transform: {
            position: [x, 10, z],
            scale: [1, Math.random() * 0.5 + 0.8, 1]
          }
        }
      });
      sceneObjects.push(building);
    }
  }
  
  console.log(`   Created ${sceneObjects.length} buildings`);
  
  // Add street lights
  const lights = [];
  for (let x = -25; x <= 25; x += 10) {
    for (let z = -25; z <= 25; z += 10) {
      const light = engine.prefabPipeline.instantiate({
        prefabId: 'street-light',
        overrides: {
          transform: {
            position: [x, 2.5, z]
          }
        }
      });
      lights.push(light);
    }
  }
  
  console.log(`   Created ${lights.length} street lights`);
  
  // Add vehicles
  const vehicles = [];
  for (let i = 0; i < 10; i++) {
    const car = engine.prefabPipeline.instantiate({
      prefabId: 'car',
      overrides: {
        transform: {
          position: [
            Math.random() * 40 - 20,
            0.5,
            Math.random() * 40 - 20
          ],
          rotation: [0, Math.random() * Math.PI * 2, 0]
        }
      }
    });
    vehicles.push(car);
  }
  
  console.log(`   Created ${vehicles.length} vehicles`);
  
  // Store the scene in MetaBase
  console.log('\n5. Storing scene in MetaBase...');
  engine.dataBus.publish('meta:store', {
    collection: 'scenes',
    id: 'city-scene-1',
    value: {
      name: 'City Scene',
      description: 'A procedurally generated city with buildings, lights, and vehicles',
      objects: [
        ...sceneObjects.map(o => o.id),
        ...lights.map(l => l.id),
        ...vehicles.map(v => v.id)
      ],
      settings: {
        ambientLight: [0.2, 0.2, 0.3],
        skyColor: [0.5, 0.7, 1.0]
      }
    }
  });
  
  // Get AI suggestions
  console.log('\n6. Getting AI optimization suggestions...');
  engine.aiIntelligence.generateSuggestions({
    task: 'scene_optimization',
    objectCount: sceneObjects.length + lights.length + vehicles.length
  });
  
  // Query scene data
  const scenes = engine.metaBase.query({
    collection: 'scenes'
  });
  
  console.log(`\n7. Scene created successfully!`);
  console.log(`   Total objects in scene: ${sceneObjects.length + lights.length + vehicles.length}`);
  console.log(`   Scenes in database: ${scenes.length}`);
  
  // Display prefab statistics
  const allPrefabs = engine.prefabPipeline.getPrefabs();
  const allInstances = engine.prefabPipeline.getInstances();
  
  console.log(`\n8. Prefab Statistics:`);
  console.log(`   Registered prefabs: ${allPrefabs.length}`);
  console.log(`   Active instances: ${allInstances.length}`);
  allPrefabs.forEach(prefab => {
    const instanceCount = allInstances.filter(
      inst => inst.prefabId === prefab.id
    ).length;
    console.log(`     - ${prefab.name}: ${instanceCount} instances`);
  });
  
  console.log('\n=== Example Complete ===\n');
  
  // Shutdown
  setTimeout(() => {
    engine.shutdown();
    process.exit(0);
  }, 1000);
}

// Run the example
advancedPrefabExample().catch(console.error);
