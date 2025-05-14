import sys
import os
# Add the project root to the Python path to resolve imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Handle import with try/except to silence VS Code warnings
try:
    from supabase import create_client
except ImportError:
    # Type stub for IDE
    def create_client(url, key, **kwargs):
        """Create a Supabase client (type stub)"""
        class FakeClient:
            def table(self, name):
                class FakeTable:
                    def select(self, *args): return self
                    def eq(self, *args): return self
                    def limit(self, *args): return self
                    def execute(self):
                        class FakeResponse:
                            data = []
                        return FakeResponse()
                return FakeTable()
        return FakeClient()

from config.config import SUPABASE_URL, SUPABASE_KEY
from typing import Dict, Any, Optional

class SupabaseClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance.client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return cls._instance

    def get_model_pricing(self, model: str) -> Optional[Dict[str, Any]]:
        """
        Get pricing information for a specific model from the model_pricing table
        """
        response = self.client.table('model_pricing') \
            .select('*') \
            .eq('model', model) \
            .eq('is_active', True) \
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    def insert_token_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a new token usage log into the token_logs table
        """
        response = self.client.table('token_logs') \
            .insert(log_data) \
            .execute()
        
        return response.data[0] if response.data else None 