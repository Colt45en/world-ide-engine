/**
 * World Engine IDE - Core System
 * A fully connected system that integrates math, graphics, prefabs, AI, metadata, and web development
 */

import { MathEngine } from './core/math-engine.js';
import { GraphicsEngine } from './core/graphics-engine.js';
import { PrefabPipeline } from './core/prefab-pipeline.js';
import { AIIntelligence } from './core/ai-intelligence.js';
import { MetaBase } from './core/meta-base.js';
import { WebFramework } from './core/web-framework.js';
import { DataBus } from './core/data-bus.js';

class WorldEngine {
  constructor() {
    console.log('🌍 Initializing World Engine IDE...');
    
    // Initialize the central data bus for system-wide data sharing
    this.dataBus = new DataBus();
    
    // Initialize all subsystems with shared data bus
    this.mathEngine = new MathEngine(this.dataBus);
    this.graphicsEngine = new GraphicsEngine(this.dataBus);
    this.prefabPipeline = new PrefabPipeline(this.dataBus);
    this.aiIntelligence = new AIIntelligence(this.dataBus);
    this.metaBase = new MetaBase(this.dataBus);
    this.webFramework = new WebFramework(this.dataBus);
    
    this.initialized = false;
  }
  
  async initialize() {
    console.log('⚙️  Initializing subsystems...');
    
    // Initialize all subsystems in parallel for performance
    await Promise.all([
      this.mathEngine.initialize(),
      this.graphicsEngine.initialize(),
      this.prefabPipeline.initialize(),
      this.aiIntelligence.initialize(),
      this.metaBase.initialize(),
      this.webFramework.initialize()
    ]);
    
    // Connect systems through the data bus
    this.setupSystemConnections();
    
    this.initialized = true;
    console.log('✅ World Engine IDE initialized successfully');
    
    return this;
  }
  
  setupSystemConnections() {
    console.log('🔗 Setting up system connections...');
    
    // Math engine outputs feed into graphics engine
    this.dataBus.subscribe('math:calculation', (data) => {
      this.graphicsEngine.processData(data);
    });
    
    // Graphics engine can request math computations
    this.dataBus.subscribe('graphics:needsComputation', (data) => {
      this.mathEngine.compute(data);
    });
    
    // Prefab pipeline uses both math and graphics
    this.dataBus.subscribe('prefab:create', (data) => {
      this.mathEngine.validateGeometry(data);
      this.graphicsEngine.render(data);
    });
    
    // AI intelligence monitors all systems
    this.dataBus.subscribe('*', (data) => {
      this.aiIntelligence.analyze(data);
    });
    
    // MetaBase stores all system data
    this.dataBus.subscribe('*:save', (data) => {
      this.metaBase.store(data);
    });
    
    console.log('✅ System connections established');
  }
  
  getStatus() {
    return {
      initialized: this.initialized,
      subsystems: {
        mathEngine: this.mathEngine.status,
        graphicsEngine: this.graphicsEngine.status,
        prefabPipeline: this.prefabPipeline.status,
        aiIntelligence: this.aiIntelligence.status,
        metaBase: this.metaBase.status,
        webFramework: this.webFramework.status
      },
      dataBusStats: this.dataBus.getStats()
    };
  }
  
  shutdown() {
    console.log('🛑 Shutting down World Engine...');
    this.dataBus.clear();
    this.initialized = false;
    console.log('✅ Shutdown complete');
  }
}

// Main entry point
async function main() {
  const engine = new WorldEngine();
  await engine.initialize();
  
  // Display system status
  const status = engine.getStatus();
  console.log('\n📊 System Status:', JSON.stringify(status, null, 2));
  
  // Keep the engine running
  console.log('\n🚀 World Engine IDE is running...');
  console.log('Press Ctrl+C to exit\n');
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n');
    engine.shutdown();
    process.exit(0);
  });
}

main().catch(console.error);

export { WorldEngine };
