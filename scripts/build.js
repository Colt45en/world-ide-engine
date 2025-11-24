/**
 * Build script for World Engine IDE
 * Simple validation and preparation for distribution
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.join(__dirname, '..');

console.log('🔨 Building World Engine IDE...\n');

// Validate all core modules exist
const coreModules = [
  'src/index.js',
  'src/core/data-bus.js',
  'src/core/math-engine.js',
  'src/core/graphics-engine.js',
  'src/core/prefab-pipeline.js',
  'src/core/ai-intelligence.js',
  'src/core/meta-base.js',
  'src/core/web-framework.js'
];

console.log('✓ Checking core modules...');
let allModulesExist = true;

for (const module of coreModules) {
  const modulePath = path.join(rootDir, module);
  if (!fs.existsSync(modulePath)) {
    console.error(`  ✗ Missing: ${module}`);
    allModulesExist = false;
  } else {
    console.log(`  ✓ ${module}`);
  }
}

if (!allModulesExist) {
  console.error('\n❌ Build failed: Missing modules');
  process.exit(1);
}

// Check examples
console.log('\n✓ Checking examples...');
const examples = [
  'examples/basic-usage.js',
  'examples/advanced-prefabs.js'
];

for (const example of examples) {
  const examplePath = path.join(rootDir, example);
  if (fs.existsSync(examplePath)) {
    console.log(`  ✓ ${example}`);
  }
}

// Check documentation
console.log('\n✓ Checking documentation...');
const docs = [
  'README.md',
  'docs/ARCHITECTURE.md'
];

for (const doc of docs) {
  const docPath = path.join(rootDir, doc);
  if (fs.existsSync(docPath)) {
    console.log(`  ✓ ${doc}`);
  }
}

// Validate package.json
console.log('\n✓ Validating package.json...');
const packageJsonPath = path.join(rootDir, 'package.json');
if (fs.existsSync(packageJsonPath)) {
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  console.log(`  ✓ Package: ${packageJson.name} v${packageJson.version}`);
  console.log(`  ✓ Type: ${packageJson.type}`);
}

console.log('\n✅ Build successful!');
console.log('\nWorld Engine IDE is ready to use.');
console.log('\nQuick Start:');
console.log('  npm start              - Run the engine');
console.log('  node examples/basic-usage.js - Run basic example');
console.log('  node examples/advanced-prefabs.js - Run advanced example');
console.log('\n');
