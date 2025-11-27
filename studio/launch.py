"""
World Engine Studio - Master Launcher
Starts Physics API server and serves the HTML dashboard
"""

import os
import sys
import threading
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urljoin

# Ensure we're in the correct directory
STUDIO_DIR = Path(__file__).parent.absolute()
os.chdir(STUDIO_DIR)

# ============================================
# PHYSICS API SERVER
# ============================================
def start_physics_api():
    """Start FastAPI physics server on port 8001"""
    try:
        # Try to import and run the physics API
        sys.path.insert(0, str(STUDIO_DIR.parent))
        
        from api.nexus_physics_api import app
        import uvicorn
        
        print("🚀 Starting Physics API on http://localhost:8001")
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="warning")
    except ImportError as e:
        print(f"⚠️  Physics API not available: {e}")
        print("   Running in mock physics mode")
    except Exception as e:
        print(f"❌ Error starting Physics API: {e}")
        print("   Continuing with mock physics fallback...")

# ============================================
# WEB SERVER
# ============================================
class StudioHTTPHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for serving index.html"""
    
    def end_headers(self):
        # Disable caching for development
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # Serve index.html for root
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()
    
    def log_message(self, format, *args):
        # Suppress verbose logging
        if '200' in str(args):
            print(f"  📄 {args[0]}")

def start_web_server():
    """Start HTTP server on port 8000 for dashboard"""
    try:
        server = HTTPServer(('0.0.0.0', 8000), StudioHTTPHandler)
        print(f"✅ Dashboard server running on http://localhost:8000")
        print(f"   Serving from: {STUDIO_DIR}")
        server.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            print("⚠️  Port 8000 already in use. Dashboard may be running.")
        else:
            print(f"❌ Web server error: {e}")

# ============================================
# MAIN LAUNCHER
# ============================================
def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║        WORLD ENGINE STUDIO - MASTER DASHBOARD              ║
║                                                           ║
║  ⚙️  Physics Engine  |  🎨 Node Graph  |  💻 Terminal     ║
║  🔮 Keeper Nexus    |  ✨ Aesthetics   |  📈 Metrics      ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # Start Physics API in background thread
    api_thread = threading.Thread(target=start_physics_api, daemon=True)
    api_thread.start()

    # Give API a moment to start
    import time
    time.sleep(2)

    # Start Web Server in main thread
    try:
        start_web_server()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down World Engine Studio...")
        sys.exit(0)

if __name__ == '__main__':
    main()
