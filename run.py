"""Application entry point."""

import os
from app import create_app


if __name__ == '__main__':
    app = create_app()
    
    # Configuration from environment
    debug = os.getenv('FLASK_ENV') == 'development'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )
