import sys
import os

# Handle import with try/except to silence VS Code warnings
try:
    from dotenv import load_dotenv
except ImportError:
    # Fallback for type checking - this won't run in real code
    def load_dotenv(*args, **kwargs):
        """Load environment variables from .env file (type stub)"""
        pass

# Add the project root to the Python path to resolve imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Load environment variables from .env file
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Flask configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("FLASK_ENV", "development") == "development" 