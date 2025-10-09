from src.app import create_app
import os

def main():
    app = create_app()
    
    # Get configuration from environment
    host = os.getenv('WORDUP_HOST', '127.0.0.1')
    port = int(os.getenv('WORDUP_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting WordUp on http://{host}:{port}")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()
