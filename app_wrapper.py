#!/usr/bin/env python3
"""
Railway deployment wrapper for Synergos AI
"""

import os
import sys

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the actual Flask app
from src.main import app

# Export for Gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)