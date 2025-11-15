#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve from web/ directory if it exists, otherwise from root
        web_dir = Path(__file__).parent / "web"
        if web_dir.exists():
            super().__init__(*args, directory=str(web_dir), **kwargs)
        else:
            super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)

def find_free_port(start_port=8000, max_attempts=10):
    """Find a free port starting from start_port"""
    import socket
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
    return None

def main():
    port = find_free_port(PORT)
    if port is None:
        print(f"Error: Could not find a free port starting from {PORT}")
        return
    
    with socketserver.TCPServer(("", port), Handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"Server running at {url}")
        print(f"  Main app: {url}")
        print(f"  3D Viewer: {url}/viewer.html")
        print("Press Ctrl+C to stop")
        
        # Auto-open browser
        try:
            webbrowser.open(url)
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

if __name__ == "__main__":
    main()

