from flask import Blueprint, request, jsonify, current_app
from db.supabase_client import SupabaseClient
from services.analytics_service import AnalyticsService
from datetime import datetime, timedelta
import json
from typing import Dict, Any, Optional, List

# Create blueprint
analytics_bp = Blueprint('analytics', __name__)

# Create Supabase client
supabase_client = SupabaseClient()
analytics_service = AnalyticsService(supabase_client)

def parse_date_param(date_str: str, default_days_ago: int = 30) -> str:
    """Parse date parameter or return default date"""
    if date_str:
        return date_str
    else:
        # Default to X days ago
        default_date = datetime.now() - timedelta(days=default_days_ago)
        return default_date.strftime('%Y-%m-%d')

@analytics_bp.route('/analytics/summary', methods=['GET'])
def get_summary_data():
    """Get summary analytics for a time period"""
    start_date = parse_date_param(request.args.get('start_date'))
    end_date = parse_date_param(request.args.get('end_date'), 0)  # Default to today
    model = request.args.get('model', '*')  # * means all models
    task = request.args.get('task', '*')    # * means all tasks/endpoints
    interval = request.args.get('interval', 'day')  # day, week, month
    
    # Get summary data from database
    summary_data = analytics_service.get_summary(
        start_date, 
        end_date, 
        model, 
        task, 
        interval
    )
    
    return jsonify(summary_data)

@analytics_bp.route('/analytics/timeseries', methods=['GET'])
def get_timeseries_data():
    """Get time series data for token usage over time"""
    start_date = parse_date_param(request.args.get('start_date'))
    end_date = parse_date_param(request.args.get('end_date'), 0)  # Default to today
    interval = request.args.get('interval', 'day')  # hour, day, week, month
    metric = request.args.get('metric', 'tokens')  # tokens or cost
    # Ensure consistent handling of filter parameters with proper defaults
    model = request.args.get('model')
    if model == '' or model == 'null' or model == 'undefined':
        model = '*'
    
    task = request.args.get('task')
    if task == '' or task == 'null' or task == 'undefined':
        task = '*'
    
    # Log filter settings for debugging
    current_app.logger.info(f"Timeseries requested with filters: interval={interval}, metric={metric}, model={model}, task={task}")
    
    # Get time series data from analytics service
    try:
        result = analytics_service.get_timeseries(
            start_date, 
            end_date, 
            interval, 
            metric,
            model,
            task
        )
        
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error in timeseries API: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"data": [], "error": str(e)})

@analytics_bp.route('/analytics/models', methods=['GET'])
def get_model_distribution():
    """Get distribution of token usage by model"""
    start_date = parse_date_param(request.args.get('start_date'))
    end_date = parse_date_param(request.args.get('end_date'), 0)  # Default to today
    metric = request.args.get('metric', 'tokens')  # tokens or cost
    limit = int(request.args.get('limit', 10))  # Number of models to return
    model = request.args.get('model', '*')
    task = request.args.get('task', '*')
    interval = request.args.get('interval', 'day')  # day, week, month
    
    # Get model distribution from database
    model_data = analytics_service.get_model_distribution(
        start_date, 
        end_date, 
        metric,
        limit,
        model,
        task,
        interval
    )
    
    return jsonify(model_data)

@analytics_bp.route('/analytics/features', methods=['GET'])
def get_feature_usage():
    """Get distribution of token usage by endpoint/feature"""
    start_date = parse_date_param(request.args.get('start_date'))
    end_date = parse_date_param(request.args.get('end_date'), 0)  # Default to today
    metric = request.args.get('metric', 'tokens')  # tokens or cost
    limit = int(request.args.get('limit', 10))  # Number of features to return
    model = request.args.get('model', '*')
    task = request.args.get('task', '*')
    interval = request.args.get('interval', 'day')  # day, week, month
    
    # Get feature usage from database
    feature_data = analytics_service.get_feature_usage(
        start_date, 
        end_date, 
        metric,
        limit,
        model,
        task,
        interval
    )
    
    return jsonify(feature_data)

@analytics_bp.route('/analytics/cost-alternatives', methods=['GET'])
def get_cost_alternatives():
    """Get alternative model cost data for a specific model"""
    model = request.args.get('model')
    
    if not model:
        return jsonify({"error": "Model parameter is required"}), 400
        
    alternatives = supabase_client.get_model_alternatives(model)
    return jsonify({"alternatives": alternatives})

@analytics_bp.route('/analytics/logs', methods=['GET'])
def get_logs():
    """
    Get raw token usage logs with filtering
    """
    # Get query parameters with defaults
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
    # Include the full current day in end_date
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    model = request.args.get('model')
    endpoint_name = request.args.get('endpoint')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    try:
        logs = supabase_client.get_token_logs(
            start_date, 
            end_date, 
            model=model,
            endpoint_name=endpoint_name,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            "total": len(logs),
            "logs": logs
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/distinct', methods=['GET'])
def get_distinct_values():
    """
    Get distinct values for a given field
    
    Query parameters:
    - field: The field to get distinct values for (required)
    - start_date: Start date for filtering (optional)
    - end_date: End date for filtering (optional)
    
    Returns:
    - Array of distinct values
    """
    field = request.args.get('field')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not field:
        return jsonify({"error": "Field parameter is required"}), 400
    
    # Handle known fields for protection against SQL injection
    if field not in ['model', 'endpoint_name', 'api_provider']:
        return jsonify({"error": f"Invalid field: {field}"}), 400
        
    try:
        # Use date range if provided
        if start_date and end_date:
            distinct_values = supabase_client.get_distinct_values(field, start_date, end_date)
        else:
            # Default to last 90 days if no dates specified
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            distinct_values = supabase_client.get_distinct_values(field, start_date, end_date)
        
        return jsonify(distinct_values), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 