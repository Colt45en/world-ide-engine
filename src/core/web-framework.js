/**
 * WebFramework - Web development and UI framework
 * Provides tools for building web interfaces and managing web projects
 */

class WebFramework {
  constructor(dataBus) {
    this.dataBus = dataBus;
    this.status = 'uninitialized';
    this.routes = new Map();
    this.components = new Map();
    this.middleware = [];
  }
  
  async initialize() {
    console.log('  🌐 Web Framework initializing...');
    this.status = 'ready';
    
    // Initialize default routes and components
    this.initializeDefaults();
    
    // Subscribe to web requests
    this.dataBus.subscribe('web:route', (data) => this.handleRoute(data));
    this.dataBus.subscribe('web:component', (data) => this.registerComponent(data));
    
    return this;
  }
  
  /**
   * Initialize default routes and components
   */
  initializeDefaults() {
    // Default routes
    this.addRoute('/', {
      name: 'Home',
      handler: this.homeHandler.bind(this)
    });
    
    this.addRoute('/editor', {
      name: 'Editor',
      handler: this.editorHandler.bind(this)
    });
    
    this.addRoute('/assets', {
      name: 'Assets',
      handler: this.assetsHandler.bind(this)
    });
    
    this.addRoute('/settings', {
      name: 'Settings',
      handler: this.settingsHandler.bind(this)
    });
    
    // Default components
    this.registerComponent({
      name: 'Button',
      props: ['label', 'onClick', 'variant'],
      template: '<button class="btn-{{variant}}">{{label}}</button>'
    });
    
    this.registerComponent({
      name: 'Panel',
      props: ['title', 'content'],
      template: '<div class="panel"><h3>{{title}}</h3><div>{{content}}</div></div>'
    });
    
    this.registerComponent({
      name: 'Viewport',
      props: ['scene', 'camera'],
      template: '<canvas class="viewport" data-scene="{{scene}}"></canvas>'
    });
  }
  
  /**
   * Add a route
   */
  addRoute(path, config) {
    this.routes.set(path, {
      path,
      ...config,
      createdAt: Date.now()
    });
    
    this.dataBus.publish('web:routeAdded', {
      path,
      name: config.name
    });
  }
  
  /**
   * Handle route request
   */
  handleRoute(data) {
    const { path, params = {} } = data;
    
    const route = this.routes.get(path);
    if (!route) {
      this.dataBus.publish('web:routeNotFound', { path });
      return null;
    }
    
    // Execute route handler
    const result = route.handler(params);
    
    this.dataBus.publish('web:routeHandled', {
      path,
      success: true
    });
    
    return result;
  }
  
  /**
   * Home page handler
   */
  homeHandler(params) {
    return {
      title: 'World Engine IDE',
      content: 'Welcome to the World Engine IDE - A fully connected development environment',
      components: ['Viewport', 'Panel']
    };
  }
  
  /**
   * Editor page handler
   */
  editorHandler(params) {
    return {
      title: 'Editor',
      content: 'Visual editor for creating and editing scenes',
      components: ['Viewport', 'Panel', 'Button'],
      tools: ['move', 'rotate', 'scale']
    };
  }
  
  /**
   * Assets page handler
   */
  assetsHandler(params) {
    return {
      title: 'Asset Browser',
      content: 'Browse and manage project assets',
      components: ['Panel', 'Button'],
      assetTypes: ['meshes', 'textures', 'materials', 'prefabs']
    };
  }
  
  /**
   * Settings page handler
   */
  settingsHandler(params) {
    return {
      title: 'Settings',
      content: 'Configure engine and project settings',
      components: ['Panel', 'Button'],
      sections: ['general', 'graphics', 'ai', 'performance']
    };
  }
  
  /**
   * Register a UI component
   */
  registerComponent(data) {
    const { name, props, template } = data;
    
    this.components.set(name, {
      name,
      props: props || [],
      template: template || '',
      createdAt: Date.now()
    });
    
    this.dataBus.publish('web:componentRegistered', {
      name
    });
    
    return name;
  }
  
  /**
   * Get component
   */
  getComponent(name) {
    return this.components.get(name);
  }
  
  /**
   * Add middleware
   */
  use(middleware) {
    this.middleware.push(middleware);
  }
  
  /**
   * Generate HTML for a component
   */
  renderComponent(name, props = {}) {
    const component = this.components.get(name);
    if (!component) {
      return '';
    }
    
    let html = component.template;
    
    // Replace props in template
    Object.entries(props).forEach(([key, value]) => {
      const regex = new RegExp(`{{${key}}}`, 'g');
      html = html.replace(regex, value);
    });
    
    return html;
  }
  
  /**
   * Generate page structure
   */
  generatePage(route) {
    return {
      html: `
<!DOCTYPE html>
<html>
<head>
  <title>${route.title || 'World Engine IDE'}</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
  <div id="app">
    <h1>${route.title}</h1>
    <p>${route.content}</p>
  </div>
</body>
</html>
      `.trim(),
      route
    };
  }
  
  /**
   * Get all routes
   */
  getRoutes() {
    return Array.from(this.routes.values());
  }
  
  /**
   * Get all components
   */
  getComponents() {
    return Array.from(this.components.values());
  }
}

export { WebFramework };
