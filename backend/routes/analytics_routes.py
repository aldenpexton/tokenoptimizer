from flask import Blueprint, request, jsonify
from db.supabase_client import SupabaseClient
from services.analytics_service import AnalyticsService
from datetime import datetime, timedelta

# Create blueprint
analytics_bp = Blueprint('analytics', __name__)

# Initialize services
supabase_client = SupabaseClient()
analytics_service = AnalyticsService(supabase_client)

@analytics_bp.route('/analytics/summary', methods=['GET'])
def get_summary():
    """
    Get summary analytics of token usage
    """
    # Get query parameters with defaults
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        summary_data = analytics_service.get_summary(start_date, end_date)
        return jsonify(summary_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/analytics/timeseries', methods=['GET'])
def get_timeseries():
    """
    Get time series data of token usage
    """
    # Get query parameters with defaults
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    interval = request.args.get('interval', 'day')
    metric = request.args.get('metric', 'tokens')
    
    try:
        timeseries_data = analytics_service.get_timeseries(start_date, end_date, interval, metric)
        return jsonify(timeseries_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/analytics/models', methods=['GET'])
def get_models():
    """
    Get model distribution data
    """
    # Get query parameters with defaults
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    metric = request.args.get('metric', 'tokens')
    limit = int(request.args.get('limit', 10))
    
    try:
        models_data = analytics_service.get_model_distribution(start_date, end_date, metric, limit)
        return jsonify(models_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/analytics/features', methods=['GET'])
def get_features():
    """
    Get feature usage data
    """
    # Get query parameters with defaults
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    metric = request.args.get('metric', 'tokens')
    limit = int(request.args.get('limit', 10))
    
    try:
        features_data = analytics_service.get_feature_usage(start_date, end_date, metric, limit)
        return jsonify(features_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/analytics/logs', methods=['GET'])
def get_logs():
    """
    Get detailed logs with pagination
    """
    # Get query parameters with defaults
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    model = request.args.get('model')
    feature = request.args.get('feature')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    sort_by = request.args.get('sort_by', 'timestamp')
    sort_dir = request.args.get('sort_dir', 'desc')
    
    try:
        logs_data = analytics_service.get_logs(
            start_date, end_date, model, feature, 
            page, page_size, sort_by, sort_dir
        )
        return jsonify(logs_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 