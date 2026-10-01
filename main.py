"""
FixLoop — Platform Main Entry Point
"""
import os
import sys
from app import create_app

app = create_app()

def main():
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    print(f"Starting FixLoop Platform on http://{host}:{port} (debug={debug})...")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()
