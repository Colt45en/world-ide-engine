/**
 * MetaBase - Metadata and database management system
 * Stores and manages all system data, configurations, and assets
 */

class MetaBase {
  constructor(dataBus) {
    this.dataBus = dataBus;
    this.status = 'uninitialized';
    this.storage = new Map();
    this.indices = new Map();
    this.schemas = new Map();
  }
  
  async initialize() {
    console.log('  💾 MetaBase initializing...');
    this.status = 'ready';
    
    // Initialize schemas
    this.initializeSchemas();
    
    // Subscribe to storage requests
    this.dataBus.subscribe('meta:store', (data) => this.store(data));
    this.dataBus.subscribe('meta:query', (data) => this.query(data));
    this.dataBus.subscribe('meta:delete', (data) => this.delete(data));
    
    return this;
  }
  
  /**
   * Initialize data schemas
   */
  initializeSchemas() {
    this.schemas.set('asset', {
      type: 'asset',
      fields: ['id', 'name', 'type', 'path', 'metadata', 'createdAt', 'updatedAt']
    });
    
    this.schemas.set('prefab', {
      type: 'prefab',
      fields: ['id', 'name', 'components', 'tags', 'createdAt', 'updatedAt']
    });
    
    this.schemas.set('scene', {
      type: 'scene',
      fields: ['id', 'name', 'objects', 'settings', 'createdAt', 'updatedAt']
    });
    
    this.schemas.set('project', {
      type: 'project',
      fields: ['id', 'name', 'description', 'version', 'assets', 'createdAt', 'updatedAt']
    });
  }
  
  /**
   * Store data in the metabase
   */
  store(data) {
    const { collection, id, value } = data;
    
    if (!collection || !id) {
      console.error('Invalid store request: collection and id required');
      return false;
    }
    
    // Get or create collection
    if (!this.storage.has(collection)) {
      this.storage.set(collection, new Map());
      this.indices.set(collection, new Map());
    }
    
    const collectionData = this.storage.get(collection);
    const collectionIndex = this.indices.get(collection);
    
    // Add timestamps
    const enrichedValue = {
      ...value,
      id,
      updatedAt: Date.now(),
      createdAt: collectionData.has(id) ? collectionData.get(id).createdAt : Date.now()
    };
    
    // Store data
    collectionData.set(id, enrichedValue);
    
    // Update indices
    this.updateIndices(collection, id, enrichedValue);
    
    // Publish store event
    this.dataBus.publish('meta:stored', {
      collection,
      id,
      success: true
    });
    
    return true;
  }
  
  /**
   * Update search indices
   */
  updateIndices(collection, id, value) {
    const collectionIndex = this.indices.get(collection);
    
    // Index by type if available
    if (value.type) {
      if (!collectionIndex.has('type')) {
        collectionIndex.set('type', new Map());
      }
      const typeIndex = collectionIndex.get('type');
      if (!typeIndex.has(value.type)) {
        typeIndex.set(value.type, new Set());
      }
      typeIndex.get(value.type).add(id);
    }
    
    // Index by name if available
    if (value.name) {
      if (!collectionIndex.has('name')) {
        collectionIndex.set('name', new Map());
      }
      collectionIndex.get('name').set(value.name.toLowerCase(), id);
    }
  }
  
  /**
   * Query data from the metabase
   */
  query(queryData) {
    const { collection, filter = {}, limit = 100 } = queryData;
    
    if (!this.storage.has(collection)) {
      return [];
    }
    
    const collectionData = this.storage.get(collection);
    let results = Array.from(collectionData.values());
    
    // Apply filters
    Object.entries(filter).forEach(([key, value]) => {
      results = results.filter(item => item[key] === value);
    });
    
    // Apply limit
    results = results.slice(0, limit);
    
    // Publish query event
    this.dataBus.publish('meta:queried', {
      collection,
      resultCount: results.length
    });
    
    return results;
  }
  
  /**
   * Get a single item by id
   */
  get(collection, id) {
    if (!this.storage.has(collection)) {
      return null;
    }
    return this.storage.get(collection).get(id) || null;
  }
  
  /**
   * Delete data from the metabase
   */
  delete(data) {
    const { collection, id } = data;
    
    if (!this.storage.has(collection)) {
      return false;
    }
    
    const collectionData = this.storage.get(collection);
    const deleted = collectionData.delete(id);
    
    if (deleted) {
      this.dataBus.publish('meta:deleted', {
        collection,
        id
      });
    }
    
    return deleted;
  }
  
  /**
   * Get all collections
   */
  getCollections() {
    return Array.from(this.storage.keys());
  }
  
  /**
   * Get statistics
   */
  getStats() {
    const stats = {
      collections: this.storage.size,
      totalItems: 0,
      schemas: this.schemas.size
    };
    
    this.storage.forEach(collection => {
      stats.totalItems += collection.size;
    });
    
    return stats;
  }
  
  /**
   * Export data
   */
  export(collection = null) {
    if (collection) {
      const collectionData = this.storage.get(collection);
      return collectionData ? Object.fromEntries(collectionData) : null;
    }
    
    // Export all
    const exportData = {};
    this.storage.forEach((data, name) => {
      exportData[name] = Object.fromEntries(data);
    });
    return exportData;
  }
  
  /**
   * Import data
   */
  import(data) {
    Object.entries(data).forEach(([collection, items]) => {
      if (!this.storage.has(collection)) {
        this.storage.set(collection, new Map());
      }
      const collectionData = this.storage.get(collection);
      Object.entries(items).forEach(([id, value]) => {
        collectionData.set(id, value);
      });
    });
    
    this.dataBus.publish('meta:imported', {
      collections: Object.keys(data).length
    });
  }
}

export { MetaBase };
