"""
Database queries for the TokenOptimizer dashboard.
Follows the requirements for data retrieval and aggregation.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta

def get_spend_by_model(supabase, start_date: str) -> List[Dict[str, Any]]:
    """Get total spend grouped by model."""
    response = supabase.table('token_logs').select(
        "model, total_cost"
    ).gte('timestamp', start_date).execute()
    
    # Aggregate by model
    model_spend = {}
    for row in response.data:
        model = row['model']
        cost = row['total_cost']
        model_spend[model] = model_spend.get(model, 0) + cost
    
    # Convert to list of dictionaries
    return [{'model': k, 'total_cost': v} for k, v in model_spend.items()]

def get_spend_by_endpoint(supabase, start_date: str) -> List[Dict[str, Any]]:
    """Get total spend grouped by endpoint."""
    response = supabase.table('token_logs').select(
        "endpoint_name, total_cost"
    ).gte('timestamp', start_date).execute()
    
    # Aggregate by endpoint
    endpoint_spend = {}
    for row in response.data:
        endpoint = row['endpoint_name']
        cost = row['total_cost']
        endpoint_spend[endpoint] = endpoint_spend.get(endpoint, 0) + cost
    
    # Convert to list of dictionaries
    return [{'endpoint': k, 'total_cost': v} for k, v in endpoint_spend.items()]

def get_spend_trend(supabase, start_date: str) -> List[Dict[str, Any]]:
    """Get daily spend trend."""
    response = supabase.table('token_logs').select(
        "timestamp, total_cost"
    ).gte('timestamp', start_date).execute()
    
    # Aggregate by day
    daily_spend = {}
    for row in response.data:
        date = row['timestamp'][:10]  # Get just the date part
        cost = row['total_cost']
        daily_spend[date] = daily_spend.get(date, 0) + cost
    
    # Convert to list of dictionaries
    return [{'date': k, 'total_cost': v} for k, v in sorted(daily_spend.items())]

def get_model_alternatives(supabase) -> List[Dict[str, Any]]:
    """Get recommended model alternatives."""
    response = supabase.table('model_alternatives').select(
        "*"
    ).eq('is_recommended', True).execute()
    
    return response.data 