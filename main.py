#!/usr/bin/env python3
"""
World Engine - Main API Server Entry Point
"""

import os
import uvicorn
from api.service import create_app

def main():
    """Start the World Engine API server."""
    app = create_app()
    
    # Allow configuration of port via environment variable PORT
    port = int(os.environ.get("PORT", "8001"))
    print(f"Starting World Engine API Server on port {port}...")
    print(f"Access the Studio Interface at: http://localhost:{port}/web/studio.html")
    print(f"Access the Engine Only at: http://localhost:{port}/web/worldengine.html")
    print(f"API Documentation at: http://localhost:{port}/docs")

    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()