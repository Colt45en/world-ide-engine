#!/usr/bin/env python3
"""
Launch Studio - Quick launch script for the web interface.
Opens the default browser to the studio interface.
"""

import os
import socket
import webbrowser
import time
import threading
import uvicorn
from api.service import create_app


def start_server(port: int):
    """Start the API server in a thread on the given port."""
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


def find_free_port() -> int:
    """Find an available TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_for_url(url: str, timeout: int = 10) -> bool:
    """Poll the given URL until it's reachable or timeout.

    Uses simple socket-level checks and HTTP handshake for readiness.
    """
    import urllib.request

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status < 400:
                    return True
        except Exception:
            time.sleep(0.25)
    return False


def main():
    """Launch the studio interface."""
    print("🚀 Starting World Engine Studio...")
    
    # Choose port: environment allows override, otherwise pick a free port
    port_env = os.environ.get("PORT")
    try:
        port = int(port_env) if port_env else find_free_port()
    except Exception:
        port = 8001

    # Start server in background thread
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Wait for server to be ready (health endpoint) and then open browser
    url = f"http://localhost:{port}/web/studio.html"
    health_url = f"http://127.0.0.1:{port}/api/health"

    print(f"⏳ Waiting for server to become available at {health_url}...")
    if not wait_for_url(health_url, timeout=12):
        # fallback to /web/studio.html if health endpoint isn't available
        print("⚠️ Server health check timed out, trying studio URL directly.")
        wait_for_url(url, timeout=6)

    print(f"📱 Opening browser at: {url}")
    webbrowser.open(url)
    
    print("\n✅ Studio is running!")
    print("   Studio Interface: http://localhost:8001/web/studio.html")
    print("   Engine Only: http://localhost:8001/web/worldengine.html")
    print("   API Docs: http://localhost:8001/docs")
    print("\nPress Ctrl+C to stop the server.")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")


if __name__ == "__main__":
    main()
