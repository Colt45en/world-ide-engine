/**
 * Example: Basic World Engine Usage
 * Demonstrates core functionality and system integration
 */

import { WorldEngine } from '../src/index.js';

async function basicExample() {
  console.log('=== World Engine Basic Example ===\n');
  
  // Initialize the engine
  const engine = new WorldEngine();
  await engine.initialize();
  
  // 1. Math Engine Example
  console.log('\n1. Math Engine - Distance Calculation');
  engine.dataBus.subscribe('math:calculation', (data) => {
    if (data.operation === 'distance') {
      console.log(`   Distance result: ${data.result}`);
    }
  });
  
  engine.dataBus.publish('math:compute', {
    operation: 'distance',
    params: {
      p1: [0, 0, 0],
      p2: [3, 4, 0]
    }
  });
  
  // 2. Graphics Engine Example
  console.log('\n2. Graphics Engine - Create Material');
  engine.graphicsEngine.createMaterial('custom-metal', {
    name: 'Custom Metal',
    color: [0.8, 0.8, 0.9, 1.0],
    roughness: 0.2,
    metallic: 1.0
  });
  
  // 3. Prefab Pipeline Example
  console.log('\n3. Prefab Pipeline - Create and Instantiate');
  
  // Create a custom prefab
  engine.prefabPipeline.registerPrefab('lamp', {
    name: 'Desk Lamp',
    components: {
      light: {
        type: 'spot',
        color: [1.0, 0.9, 0.7],
        intensity: 2.0
      },
      geometry: {
        type: 'cylinder',
        radius: 0.5,
        height: 2.0
      },
      transform: {
        position: [0, 1, 0],
        rotation: [0, 0, 0],
        scale: [1, 1, 1]
      }
    }
  });
  
  // Instantiate the prefab
  const lampInstance = engine.prefabPipeline.instantiate({
    prefabId: 'lamp',
    overrides: {
      transform: {
        position: [5, 0, 5]
      }
    }
  });
  
  console.log(`   Created lamp instance: ${lampInstance.id}`);
  
  // 4. MetaBase Example
  console.log('\n4. MetaBase - Store and Query Data');
  
  // Store multiple assets
  ['texture1', 'texture2', 'model1'].forEach((id, index) => {
    engine.dataBus.publish('meta:store', {
      collection: 'assets',
      id,
      value: {
        name: `Asset ${index + 1}`,
        type: index < 2 ? 'texture' : 'model',
        path: `/assets/${id}`,
        size: Math.floor(Math.random() * 1000000)
      }
    });
  });
  
  // Query textures
  const textures = engine.metaBase.query({
    collection: 'assets',
    filter: { type: 'texture' }
  });
  
  console.log(`   Found ${textures.length} textures`);
  
  // 5. Web Framework Example
  console.log('\n5. Web Framework - Custom Route');
  
  engine.webFramework.addRoute('/custom-view', {
    name: 'Custom View',
    handler: (params) => ({
      title: 'My Custom View',
      content: 'This is a custom page in the World Engine',
      data: params
    })
  });
  
  const pageData = engine.webFramework.handleRoute({
    path: '/custom-view',
    params: { userId: 123 }
  });
  
  console.log(`   Route handled: ${pageData.title}`);
  
  // 6. AI Intelligence Example
  console.log('\n6. AI Intelligence - Analysis');
  
  // Subscribe to AI insights
  engine.dataBus.subscribe('ai:insights', (analysis) => {
    console.log(`   AI Insight: ${analysis.insights.length} suggestions found`);
    analysis.insights.forEach(insight => {
      console.log(`     - ${insight.message}`);
    });
  });
  
  // Trigger analysis
  engine.aiIntelligence.analyze({
    vertices: new Array(15000).fill([0, 0, 0]),
    renderQueue: new Array(150).fill({})
  });
  
  // 7. System Status
  console.log('\n7. System Status');
  const status = engine.getStatus();
  console.log('   All systems:', Object.keys(status.subsystems).every(
    key => status.subsystems[key] === 'ready'
  ) ? '✅ Ready' : '⚠️  Not Ready');
  
  console.log(`   DataBus channels: ${status.dataBusStats.channels.length}`);
  console.log(`   Messages sent: ${status.dataBusStats.messagesSent}`);
  
  console.log('\n=== Example Complete ===\n');
  
  // Shutdown
  setTimeout(() => {
    engine.shutdown();
    process.exit(0);
  }, 1000);
}

// Run the example
basicExample().catch(console.error);
