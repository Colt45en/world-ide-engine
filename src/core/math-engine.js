/**
 * MathEngine - Pure mathematics computation engine
 * Handles vectors, matrices, transformations, and geometric calculations
 */

class MathEngine {
  constructor(dataBus) {
    this.dataBus = dataBus;
    this.status = 'uninitialized';
    this.computationCache = new Map();
  }

  async initialize() {
    console.log('  📐 Math Engine initializing...');
    this.status = 'ready';

    // Subscribe to computation requests
    this.dataBus.subscribe('math:compute', (data) => this.compute(data));

    return this;
  }

  /**
   * Perform mathematical computation
   */
  compute(data) {
    const { operation, params } = data;
    let result;

    switch (operation) {
      case 'add':
        result = this.add(params);
        break;
      case 'multiply':
        result = this.multiply(params);
        break;
      case 'transform':
        result = this.transform(params);
        break;
      case 'distance':
        result = this.distance(params);
        break;
      default:
        result = { error: 'Unknown operation' };
    }

    // Publish result
    this.dataBus.publish('math:calculation', { operation, result });
    return result;
  }

  /**
   * Vector/Matrix addition
   */
  add(params) {
    const { a, b } = params;
    if (Array.isArray(a) && Array.isArray(b)) {
      return a.map((val, idx) => val + (b[idx] || 0));
    }
    return a + b;
  }

  /**
   * Vector/Matrix multiplication
   */
  multiply(params) {
    const { a, b } = params;
    if (Array.isArray(a) && Array.isArray(b)) {
      return a.map((val, idx) => val * (b[idx] || 1));
    }
    return a * b;
  }

  /**
   * 3D transformation matrix
   */
  transform(params) {
    const { position, rotation, scale } = params;
    return {
      position: position || [0, 0, 0],
      rotation: rotation || [0, 0, 0],
      scale: scale || [1, 1, 1],
      matrix: this.createTransformMatrix(position, rotation, scale)
    };
  }

  /**
   * Calculate distance between two points
   */
  distance(params) {
    const { p1, p2 } = params;
    const dx = p2[0] - p1[0];
    const dy = p2[1] - p1[1];
    const dz = (p2[2] || 0) - (p1[2] || 0);
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }

  /**
   * Möller–Trumbore ray-triangle intersection (JS version)
   * origin, dir, a, b, c are [x,y,z]
   * opts { twoSided?: boolean, tMin?: number, tMax?: number }
   * returns null or { t,u,v,w0,w1,w2,pos }
   */
  rayTriMT(origin, dir, a, b, c, opts = {}) {
    const twoSided = !!opts.twoSided;
    const tMin = opts.tMin ?? 1e-6;
    const tMax = opts.tMax ?? Infinity;
    const epsDet = 1e-12;

    const sub = (p, q) => [p[0] - q[0], p[1] - q[1], p[2] - q[2]];
    const dot = (p, q) => p[0] * q[0] + p[1] * q[1] + p[2] * q[2];
    const cross = (p, q) => [p[1] * q[2] - p[2] * q[1], p[2] * q[0] - p[0] * q[2], p[0] * q[1] - p[1] * q[0]];

    const ab = sub(b, a);
    const ac = sub(c, a);
    let pVec = cross(dir, ac);
    let det = dot(ab, pVec);

    if (!twoSided) {
      if (det <= epsDet) return null;
    } else {
      if (Math.abs(det) <= epsDet) return null;
    }

    let tvec = sub(origin, a);
    if (twoSided && det < 0) {
      // normalize sign so numerators behave the same for both faces
      det = -det;
      // flip tvec only (keeps pVec as computed from dir and ac)
      tvec = tvec.map(x => -x);
    }

    const invDet = 1.0 / det;
    const u = dot(tvec, pVec) * invDet;
    if (u < 0 || u > 1) return null;

    const qVec = cross(tvec, ab);
    const v = dot(dir, qVec) * invDet;
    if (v < 0 || u + v > 1) return null;

    const t = dot(ac, qVec) * invDet;
    if (t < tMin || t > tMax) return null;

    const w1 = u, w2 = v, w0 = 1 - u - v;
    const pos = [origin[0] + dir[0] * t, origin[1] + dir[1] * t, origin[2] + dir[2] * t];
    return { t, u, v, w0, w1, w2, pos };
  }

  /**
   * Create a 4x4 transformation matrix
   */
  createTransformMatrix(position = [0, 0, 0], rotation = [0, 0, 0], scale = [1, 1, 1]) {
    // Simplified 4x4 identity matrix with position and scale
    return [
      [scale[0], 0, 0, position[0]],
      [0, scale[1], 0, position[1]],
      [0, 0, scale[2], position[2]],
      [0, 0, 0, 1]
    ];
  }

  /**
   * Validate geometry data
   */
  validateGeometry(data) {
    const { vertices, normals, uvs } = data;
    const isValid = vertices && Array.isArray(vertices) && vertices.length > 0;

    this.dataBus.publish('math:validation', {
      valid: isValid,
      vertexCount: vertices ? vertices.length : 0
    });

    return isValid;
  }
}

export { MathEngine };

