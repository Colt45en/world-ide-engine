# API Reference

## WorldEngine

Main class that orchestrates all subsystems.

### Constructor

```javascript
const engine = new WorldEngine();
```

### Methods

#### `initialize()`
Initializes all subsystems and sets up connections.

**Returns:** `Promise<WorldEngine>`

```javascript
await engine.initialize();
```

#### `getStatus()`
Returns the current status of all subsystems.

**Returns:** `Object`

```javascript
const status = engine.getStatus();
// {
//   initialized: true,
//   subsystems: { ... },
//   dataBusStats: { ... }
// }
```

#### `shutdown()`
Gracefully shuts down the engine.

```javascript
engine.shutdown();
```

---

## DataBus

Central communication hub for all subsystems.

### Methods

#### `subscribe(channel, callback)`
Subscribe to events on a specific channel.

**Parameters:**
- `channel` (string): Channel name or `'*'` for all channels
- `callback` (function): Function called when message is published

**Returns:** `Function` (unsubscribe function)

```javascript
const unsubscribe = dataBus.subscribe('math:calculation', (data) => {
  console.log('Calculation result:', data);
});

// Later: unsubscribe()
```

#### `publish(channel, data)`
Publish a message to a channel.

**Parameters:**
- `channel` (string): Channel name
- `data` (any): Data to publish

```javascript
dataBus.publish('math:compute', {
  operation: 'add',
  params: { a: 5, b: 3 }
});
```

#### `getStats()`
Get statistics about the DataBus.

**Returns:** `Object`

```javascript
const stats = dataBus.getStats();
// {
//   messagesSent: 100,
//   subscribersCount: 15,
//   channels: [...],
//   historySize: 100
// }
```

#### `getHistory(channel, limit)`
Get message history for a channel.

**Parameters:**
- `channel` (string, optional): Filter by channel
- `limit` (number, optional): Maximum messages (default: 100)

**Returns:** `Array`

```javascript
const history = dataBus.getHistory('math:calculation', 10);
```

---

## MathEngine

Pure mathematics computation engine.

### Methods

#### `compute(data)`
Perform mathematical computation.

**Parameters:**
- `data` (Object): Computation request
  - `operation` (string): Operation type
  - `params` (Object): Operation parameters

**Supported Operations:**
- `add`: Add vectors/numbers
- `multiply`: Multiply vectors/numbers
- `transform`: Create transformation matrix
- `distance`: Calculate distance between points

```javascript
mathEngine.compute({
  operation: 'distance',
  params: {
    p1: [0, 0, 0],
    p2: [3, 4, 0]
  }
});
```

#### `validateGeometry(data)`
Validate geometry data.

**Parameters:**
- `data` (Object): Geometry data with vertices, normals, uvs

**Returns:** `boolean`

---

## GraphicsEngine

Visual rendering and graphics processing.

### Methods

#### `render(data)`
Render a scene or object.

**Parameters:**
- `data` (Object): Render request
  - `type` (string): Object type
  - `geometry` (Object): Geometry data
  - `material` (string): Material name
  - `transform` (Object): Transform data

**Returns:** `Object` (render item)

```javascript
graphicsEngine.render({
  type: 'mesh',
  geometry: { type: 'cube' },
  material: 'default',
  transform: {
    position: [0, 0, 0],
    rotation: [0, 0, 0],
    scale: [1, 1, 1]
  }
});
```

#### `createMaterial(name, properties)`
Create a new material.

**Parameters:**
- `name` (string): Material name
- `properties` (Object): Material properties

```javascript
graphicsEngine.createMaterial('custom', {
  color: [1, 0, 0, 1],
  roughness: 0.5,
  metallic: 0.8
});
```

---

## PrefabPipeline

Template-based asset creation and management.

### Methods

#### `registerPrefab(id, definition)`
Register a new prefab template.

**Parameters:**
- `id` (string): Prefab identifier
- `definition` (Object): Prefab definition
  - `name` (string): Display name
  - `components` (Object): Component data

**Returns:** `string` (prefab id)

```javascript
prefabPipeline.registerPrefab('my-prefab', {
  name: 'My Prefab',
  components: {
    geometry: { type: 'cube' },
    material: 'default',
    transform: { position: [0, 0, 0] }
  }
});
```

#### `instantiate(data)`
Create an instance of a prefab.

**Parameters:**
- `data` (Object): Instantiation request
  - `prefabId` (string): Prefab to instantiate
  - `overrides` (Object, optional): Property overrides

**Returns:** `Object` (instance)

```javascript
const instance = prefabPipeline.instantiate({
  prefabId: 'my-prefab',
  overrides: {
    transform: { position: [5, 0, 0] }
  }
});
```

#### `getPrefabs()`
Get all registered prefabs.

**Returns:** `Array`

#### `getInstances()`
Get all active instances.

**Returns:** `Array`

---

## AIIntelligence

AI-powered analysis and assistance.

### Methods

#### `analyze(data, channel)`
Analyze data and provide insights.

**Parameters:**
- `data` (any): Data to analyze
- `channel` (string, optional): Data source channel

**Returns:** `Object` (analysis)

```javascript
const analysis = aiIntelligence.analyze({
  vertices: [...],
  renderQueue: [...]
});
```

#### `generateSuggestions(context)`
Generate suggestions based on context.

**Parameters:**
- `context` (Object): Current context

**Returns:** `Array` (suggestions)

```javascript
const suggestions = aiIntelligence.generateSuggestions({
  task: 'create_component'
});
```

#### `getSummary()`
Get analysis summary.

**Returns:** `Object`

---

## MetaBase

Comprehensive data storage and management.

### Methods

#### `store(data)`
Store data in the metabase.

**Parameters:**
- `data` (Object): Storage request
  - `collection` (string): Collection name
  - `id` (string): Item identifier
  - `value` (any): Data to store

**Returns:** `boolean`

```javascript
metaBase.store({
  collection: 'assets',
  id: 'asset_1',
  value: {
    name: 'My Asset',
    type: 'texture',
    path: '/assets/texture.png'
  }
});
```

#### `query(queryData)`
Query data from the metabase.

**Parameters:**
- `queryData` (Object): Query parameters
  - `collection` (string): Collection to query
  - `filter` (Object, optional): Filter criteria
  - `limit` (number, optional): Max results

**Returns:** `Array`

```javascript
const textures = metaBase.query({
  collection: 'assets',
  filter: { type: 'texture' },
  limit: 10
});
```

#### `get(collection, id)`
Get a single item by id.

**Parameters:**
- `collection` (string): Collection name
- `id` (string): Item identifier

**Returns:** `Object|null`

#### `export(collection)`
Export data from collection(s).

**Parameters:**
- `collection` (string, optional): Specific collection or all

**Returns:** `Object`

#### `import(data)`
Import data into metabase.

**Parameters:**
- `data` (Object): Data to import

---

## WebFramework

Web development tools and UI generation.

### Methods

#### `addRoute(path, config)`
Add a new route.

**Parameters:**
- `path` (string): Route path
- `config` (Object): Route configuration
  - `name` (string): Route name
  - `handler` (function): Route handler

```javascript
webFramework.addRoute('/custom', {
  name: 'Custom Page',
  handler: (params) => ({
    title: 'Custom',
    content: 'Content here'
  })
});
```

#### `handleRoute(data)`
Handle a route request.

**Parameters:**
- `data` (Object): Route request
  - `path` (string): Route path
  - `params` (Object, optional): Route parameters

**Returns:** `Object|null`

#### `registerComponent(data)`
Register a UI component.

**Parameters:**
- `data` (Object): Component definition
  - `name` (string): Component name
  - `props` (Array): Component properties
  - `template` (string): HTML template

**Returns:** `string` (component name)

#### `renderComponent(name, props)`
Render a component with props.

**Parameters:**
- `name` (string): Component name
- `props` (Object): Component properties

**Returns:** `string` (HTML)

---

## DataBus Channels

### Math Engine
- `math:compute` - Computation request
- `math:calculation` - Computation result
- `math:validation` - Geometry validation result

### Graphics Engine
- `graphics:render` - Render request
- `graphics:rendered` - Render completion
- `graphics:needsComputation` - Request computation
- `graphics:transformReady` - Transform ready
- `graphics:materialCreated` - Material created

### Prefab Pipeline
- `prefab:create` - Create prefab
- `prefab:instantiate` - Instantiate prefab
- `prefab:registered` - Prefab registered
- `prefab:instantiated` - Instance created
- `prefab:instanceDeleted` - Instance deleted

### AI Intelligence
- `ai:analyze` - Analysis request
- `ai:suggest` - Suggestion request
- `ai:insights` - Analysis insights
- `ai:suggestions` - Generated suggestions

### MetaBase
- `meta:store` - Store data
- `meta:query` - Query data
- `meta:delete` - Delete data
- `meta:stored` - Data stored
- `meta:queried` - Query completed
- `meta:deleted` - Data deleted
- `meta:imported` - Data imported

### Web Framework
- `web:route` - Navigate to route
- `web:component` - Register component
- `web:routeAdded` - Route added
- `web:routeHandled` - Route handled
- `web:routeNotFound` - Route not found
- `web:componentRegistered` - Component registered
