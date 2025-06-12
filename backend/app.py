from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, UTC
from supabase import create_client, Client
from typing import List, Optional, Tuple, Dict, Any, TypedDict
from enum import Enum
from dataclasses import dataclass
import io
import csv
from zoneinfo import ZoneInfo
from postgrest import Client

# Load environment variables from root directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

# Use UTC timezone
UTC = ZoneInfo("UTC")

class TimeGranularity(Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

@dataclass
class FilterParams:
    """Data class for standardizing filter parameters across all endpoints"""
    time_granularity: TimeGranularity
    start_date: datetime
    end_date: datetime
    models: List[str]
    endpoints: List[str]
    providers: List[str]

class TokenOptimizerApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supabase: Client = None

# Initialize Flask app
app = TokenOptimizerApp(__name__)
CORS(app)

# Initialize Supabase client
supabase_url = "https://qregilyvkbwzvudfgxst.supabase.co"
supabase_key = os.getenv("SUPABASE_ANON_KEY")

print(f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_KEY length: {len(supabase_key) if supabase_key else 0}")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase credentials. Please check your .env file.")

app.supabase = create_client(supabase_url, supabase_key)

# Type definitions
class ModelMetrics(TypedDict):
    total_spend: float
    total_requests: int
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    input_cost: float
    output_cost: float
    avg_latency: Optional[float]
    error_rate: float  # We keep this for API compatibility but it will always be 0

class Recommendation(TypedDict):
    current_model: str
    recommended_model: str
    similarity_score: float
    potential_savings: float
    usage_count: int
    reason: Optional[str]

# Model characteristics for recommendations
MODEL_CHARACTERISTICS = {
    'gpt-4': {
        'capabilities': ['complex_reasoning', 'code_generation', 'creative_writing'],
        'cost_per_1k': 0.03,
        'alternatives': ['gpt-3.5-turbo-16k', 'gpt-3.5-turbo']
    },
    'gpt-4-32k': {
        'capabilities': ['complex_reasoning', 'code_generation', 'creative_writing', 'long_context'],
        'cost_per_1k': 0.06,
        'alternatives': ['gpt-4', 'gpt-3.5-turbo-16k']
    },
    'gpt-3.5-turbo': {
        'capabilities': ['general_purpose', 'chat', 'basic_tasks'],
        'cost_per_1k': 0.002,
        'alternatives': []
    },
    'gpt-3.5-turbo-16k': {
        'capabilities': ['general_purpose', 'chat', 'basic_tasks', 'medium_context'],
        'cost_per_1k': 0.003,
        'alternatives': ['gpt-3.5-turbo']
    },
    'claude-2': {
        'capabilities': ['complex_reasoning', 'code_generation', 'creative_writing', 'long_context'],
        'cost_per_1k': 0.08,
        'alternatives': ['claude-instant-1', 'gpt-4']
    },
    'claude-instant-1': {
        'capabilities': ['general_purpose', 'chat', 'basic_tasks'],
        'cost_per_1k': 0.0015,
        'alternatives': ['gpt-3.5-turbo']
    }
}

def parse_filters() -> FilterParams:
    """Parse and validate filter parameters from request"""
    try:
        # Get time granularity with validation
        granularity = request.args.get('granularity', TimeGranularity.DAY.value).lower()
        if granularity not in [e.value for e in TimeGranularity]:
            raise ValueError(f"Invalid granularity. Must be one of: {[e.value for e in TimeGranularity]}")
        time_granularity = TimeGranularity(granularity)

        # Parse end date with validation
        end_date = request.args.get('end_date')
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("Invalid end_date format. Must be ISO format (YYYY-MM-DDTHH:MM:SSZ)")
        else:
            end_date = datetime.now(UTC)

        # Parse start date if provided
        start_date = request.args.get('start_date')
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("Invalid start_date format. Must be ISO format (YYYY-MM-DDTHH:MM:SSZ)")
        else:
            # Calculate start date based on granularity only if not provided
            if time_granularity == TimeGranularity.YEAR:
                start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            elif time_granularity == TimeGranularity.MONTH:
                start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif time_granularity == TimeGranularity.WEEK:
                start_date = end_date - timedelta(days=end_date.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_granularity == TimeGranularity.DAY:
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            else:  # HOUR
                start_date = end_date.replace(minute=0, second=0, microsecond=0)

        # Get and validate model filters
        models = request.args.getlist('model')
        models = [model.strip() for model in models if model.strip()]

        # Get and validate endpoint filters
        endpoints = request.args.getlist('endpoint')
        endpoints = [endpoint.strip() for endpoint in endpoints if endpoint.strip()]

        # Get and validate provider filters
        providers = request.args.getlist('provider')
        providers = [provider.strip() for provider in providers if provider.strip()]

        return FilterParams(
            time_granularity=time_granularity,
            start_date=start_date,
            end_date=end_date,
            models=models,
            endpoints=endpoints,
            providers=providers
        )
    except Exception as e:
        raise ValueError(f"Error parsing filters: {str(e)}")

def get_time_group_format(granularity: TimeGranularity) -> str:
    """Get SQL timestamp format for grouping based on granularity"""
    formats = {
        TimeGranularity.YEAR: "YYYY-MM",  # Group by month within year
        TimeGranularity.MONTH: "YYYY-WW",  # Group by week within month
        TimeGranularity.WEEK: "YYYY-MM-DD",  # Group by day within week
        TimeGranularity.DAY: "HH24",  # Group by hour within day
        TimeGranularity.HOUR: "HH24:MI"  # Group by minute within hour
    }
    return formats[granularity]

def query_token_logs(filters: FilterParams) -> Tuple[List, int]:
    """Query token logs with filters"""
    # Start with base query
    query = app.supabase.table('token_logs').select("*", count="exact")

    # Apply date filters with timezone handling
    query = query.gte('timestamp', filters.start_date.astimezone(UTC).isoformat())
    query = query.lt('timestamp', filters.end_date.astimezone(UTC).isoformat())

    # Apply model filter (handle None values)
    if filters.models:
        query = query.in_('model', filters.models)

    # Apply endpoint filter (handle None values)
    if filters.endpoints:
        query = query.in_('endpoint_name', filters.endpoints)

    # Apply provider filter (handle None values)
    if filters.providers:
        query = query.in_('api_provider', filters.providers)

    # Add order by timestamp to ensure consistent data
    query = query.order('timestamp', desc=False)

    # Execute query with error handling
    try:
        response = query.execute()
        
        # Validate response data
        if not response.data:
            return [], 0
            
        # Ensure all required fields are present and handle type conversion
        validated_data = []
        for row in response.data:
            if all(key in row for key in ['timestamp', 'model', 'endpoint_name', 'total_cost']):
                # Convert numeric fields to proper types with fallbacks
                try:
                    row['total_cost'] = float(row.get('total_cost', 0))
                    row['input_cost'] = float(row.get('input_cost', 0))
                    row['output_cost'] = float(row.get('output_cost', 0))
                    row['total_tokens'] = int(row.get('total_tokens', 0))
                    row['prompt_tokens'] = int(row.get('prompt_tokens', 0))
                    row['completion_tokens'] = int(row.get('completion_tokens', 0))
                    row['latency_ms'] = int(row.get('latency_ms', 0))
                    validated_data.append(row)
                except (ValueError, TypeError):
                    print(f"Warning: Skipping row due to invalid numeric values: {row}")
                    continue
                
        return validated_data, len(validated_data)
    except Exception as e:
        print(f"Error querying token_logs: {str(e)}")
        return [], 0

def query_monthly_metrics() -> List[Dict[str, Any]]:
    """Query monthly aggregated metrics directly from the database"""
    try:
        print("Executing monthly metrics query...")
        current_year = datetime.now(UTC).year
        start_date = f"{current_year}-01-01"
        end_date = f"{current_year}-12-31"
        
        # Query all data for the current year
        response = app.supabase.table('token_logs').select(
            'timestamp',
            'total_cost',
            'total_tokens',
            'model',
            'endpoint_name',
            'api_provider'
        ).gte('timestamp', start_date).lte('timestamp', end_date).execute()
        
        print(f"Raw response count: {len(response.data) if response.data else 0}")
        
        if not response.data:
            return []
            
        # Initialize all months for the current year
        monthly_data = {}
        for month in range(1, 13):
            month_date = datetime(current_year, month, 1)
            month_key = month_date.strftime('%Y-%m')
            month_label = month_date.strftime('%B')
            monthly_data[month_key] = {
                'period': month_key,
                'period_label': month_label,
                'total_spend': 0,
                'total_requests': 0,
                'total_tokens': 0,
                'models_used': set(),
                'endpoints_used': set(),
                'providers_used': set()
            }
            
        # Process the data
        for row in response.data:
            timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
            month_key = timestamp.strftime('%Y-%m')
            
            if month_key in monthly_data:
                monthly_data[month_key]['total_spend'] += float(row['total_cost'])
                monthly_data[month_key]['total_requests'] += 1
                monthly_data[month_key]['total_tokens'] += int(row['total_tokens'])
                monthly_data[month_key]['models_used'].add(row['model'])
                monthly_data[month_key]['endpoints_used'].add(row['endpoint_name'])
                monthly_data[month_key]['providers_used'].add(row['api_provider'])
        
        # Convert sets to lists and prepare final result
        result = []
        for data in monthly_data.values():
            data['models_used'] = sorted(list(data['models_used']))
            data['endpoints_used'] = sorted(list(data['endpoints_used']))
            data['providers_used'] = sorted(list(data['providers_used']))
            result.append(data)
        
        # Sort by period
        result.sort(key=lambda x: x['period'])
        return result
        
    except Exception as e:
        print(f"Error querying monthly metrics: {str(e)}")
        print(f"Full error details: {repr(e)}")
        return []

@app.route('/api/filters')
def get_filters():
    """Get available filter options"""
    try:
        # Get all unique values including nulls
        response = app.supabase.table('token_logs').select('model, endpoint_name, api_provider').execute()
        
        # Get unique values preserving nulls
        unique_models = sorted(list({str(row.get('model', 'None')) for row in response.data}))
        unique_endpoints = sorted(list({str(row.get('endpoint_name', 'None')) for row in response.data}))
        unique_providers = sorted(list({str(row.get('api_provider', 'None')) for row in response.data}))

        return jsonify({
            'models': unique_models,
            'endpoints': unique_endpoints,
            'providers': unique_providers,
            'granularities': [g.value for g in TimeGranularity],
            'example_usage': {
                'filter_by_model': '?model=gpt-4&model=gpt-3.5-turbo',
                'filter_by_endpoint': '?endpoint=chat&endpoint=completions',
                'filter_by_provider': '?provider=OpenAI&provider=Anthropic',
                'filter_by_granularity': '?granularity=month',
                'filter_by_date': '?end_date=2024-03-20T00:00:00Z',
                'combine_filters': '?granularity=month&model=gpt-4&endpoint=chat&provider=OpenAI'
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(UTC).isoformat()
    })

@app.route('/api/metrics/summary')
def get_summary():
    """Get summary metrics for all time"""
    try:
        # Get all data without filtering
        response = app.supabase.table('token_logs').select(
            'total_cost',
            'total_tokens',
            'api_provider',
            'model',
            'endpoint_name'
        ).execute()
        
        if not response.data:
            return jsonify({
                'total_spend': 0,
                'total_requests': 0,
                'avg_cost_per_request': 0,
                'provider_breakdown': {},
                'model_breakdown': {},
                'endpoint_breakdown': {},
                'period': 'all time'
            })

        # Calculate totals
        total_spend = sum(float(row['total_cost']) for row in response.data)
        total_requests = len(response.data)
        avg_cost_per_request = total_spend / total_requests if total_requests > 0 else 0

        # Calculate provider breakdown
        provider_metrics = {}
        model_metrics = {}
        endpoint_metrics = {}

        for row in response.data:
            # Provider breakdown
            provider = row['api_provider']
            if provider not in provider_metrics:
                provider_metrics[provider] = {
                    'total_spend': 0,
                    'total_requests': 0,
                    'total_tokens': 0
                }
            provider_metrics[provider]['total_spend'] += float(row['total_cost'])
            provider_metrics[provider]['total_requests'] += 1
            provider_metrics[provider]['total_tokens'] += int(row['total_tokens'])

            # Model breakdown
            model = row['model']
            if model not in model_metrics:
                model_metrics[model] = {
                    'total_spend': 0,
                    'total_requests': 0,
                    'total_tokens': 0
                }
            model_metrics[model]['total_spend'] += float(row['total_cost'])
            model_metrics[model]['total_requests'] += 1
            model_metrics[model]['total_tokens'] += int(row['total_tokens'])

            # Endpoint breakdown
            endpoint = row['endpoint_name']
            if endpoint not in endpoint_metrics:
                endpoint_metrics[endpoint] = {
                    'total_spend': 0,
                    'total_requests': 0,
                    'total_tokens': 0
                }
            endpoint_metrics[endpoint]['total_spend'] += float(row['total_cost'])
            endpoint_metrics[endpoint]['total_requests'] += 1
            endpoint_metrics[endpoint]['total_tokens'] += int(row['total_tokens'])

        return jsonify({
            'total_spend': total_spend,
            'total_requests': total_requests,
            'avg_cost_per_request': avg_cost_per_request,
            'provider_breakdown': provider_metrics,
            'model_breakdown': model_metrics,
            'endpoint_breakdown': endpoint_metrics,
            'period': 'all time'
        })
    except Exception as e:
        print(f"Error in summary metrics: {str(e)}")
        print(f"Full error details: {repr(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/trend')
def get_metrics_trend():
    """Get monthly metrics trend"""
    try:
        data = query_monthly_metrics()
        
        if not data:
            return jsonify({
                'metrics': [],
                'period': 'all time'
            })

        return jsonify({
            'metrics': data,
            'period': 'all time'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/by-model')
def get_metrics_by_model():
    """Get metrics breakdown by model for the last 12 months"""
    try:
        query = """
        SELECT 
            model,
            sum(total_cost) as total_spend,
            count(*) as total_requests,
            sum(total_tokens) as total_tokens,
            array_agg(DISTINCT endpoint_name) as endpoints_used,
            array_agg(DISTINCT api_provider) as providers_used
        FROM token_logs
        WHERE timestamp >= date_trunc('month', current_date - interval '11 months')
        GROUP BY model
        ORDER BY total_spend DESC;
        """
        
        response = app.supabase.query(query).execute()
        data = response.data or []

        return jsonify({
            'metrics': data,
            'period': 'last 12 months'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/by-endpoint')
def get_metrics_by_endpoint():
    """Get metrics breakdown by endpoint for the last 12 months"""
    try:
        query = """
        SELECT 
            endpoint_name as endpoint,
            sum(total_cost) as total_spend,
            count(*) as total_requests,
            sum(total_tokens) as total_tokens,
            array_agg(DISTINCT model) as models_used,
            array_agg(DISTINCT api_provider) as providers_used
        FROM token_logs
        WHERE timestamp >= date_trunc('month', current_date - interval '11 months')
        GROUP BY endpoint_name
        ORDER BY total_spend DESC;
        """
        
        response = app.supabase.query(query).execute()
        data = response.data or []

        return jsonify({
            'metrics': data,
            'period': 'last 12 months'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_model_usage_metrics(start_date: str, end_date: str, models: Optional[List[str]] = None) -> Dict[str, ModelMetrics]:
    # First get all relevant logs
    query = app.supabase.table('token_logs').select(
        'model',
        'prompt_tokens',
        'completion_tokens',
        'total_tokens',
        'input_cost',
        'output_cost',
        'total_cost',
        'latency_ms'
    ).gte('timestamp', start_date).lte('timestamp', end_date)
    
    if models:
        query = query.in_('model', models)
    
    response = query.execute()
    
    # Process the data in Python
    metrics: Dict[str, Dict] = {}
    for row in response.data:
        model = row['model']
        if model not in metrics:
            metrics[model] = {
                'total_spend': 0.0,
                'total_requests': 0,
                'total_tokens': 0,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'input_cost': 0.0,
                'output_cost': 0.0,
                'latency_sum': 0.0
            }
        
        metrics[model]['total_spend'] += float(row['total_cost'])
        metrics[model]['total_requests'] += 1
        metrics[model]['total_tokens'] += int(row['total_tokens'])
        metrics[model]['prompt_tokens'] += int(row['prompt_tokens'])
        metrics[model]['completion_tokens'] += int(row['completion_tokens'])
        metrics[model]['input_cost'] += float(row['input_cost'])
        metrics[model]['output_cost'] += float(row['output_cost'])
        metrics[model]['latency_sum'] += float(row['latency_ms']) if row.get('latency_ms') else 0.0
    
    # Convert to final format
    result: Dict[str, ModelMetrics] = {}
    for model, data in metrics.items():
        result[model] = {
            'total_spend': data['total_spend'],
            'total_requests': data['total_requests'],
            'total_tokens': data['total_tokens'],
            'prompt_tokens': data['prompt_tokens'],
            'completion_tokens': data['completion_tokens'],
            'input_cost': data['input_cost'],
            'output_cost': data['output_cost'],
            'avg_latency': data['latency_sum'] / data['total_requests'] if data['total_requests'] > 0 else None,
            'error_rate': 0.0  # We don't have error data in the schema
        }
    
    return result

def analyze_model_usage(metrics: Dict[str, ModelMetrics]) -> List[Recommendation]:
    recommendations: List[Recommendation] = []
    
    # Get model alternatives and pricing from database
    alternatives = app.supabase.table('model_alternatives').select(
        'source_model',
        'alternative_model',
        'similarity_score'
    ).eq('is_recommended', True).execute()

    pricing = app.supabase.table('model_pricing').select(
        'model',
        'input_price',
        'output_price'
    ).eq('is_active', True).execute()

    # Build pricing lookup
    price_lookup = {
        row['model']: {
            'input_price': row['input_price'],
            'output_price': row['output_price']
        } for row in pricing.data
    }
    
    for model, model_metrics in metrics.items():
        # Find recommended alternatives for this model
        model_alternatives = [alt for alt in alternatives.data if alt['source_model'] == model]
        
        for alt in model_alternatives:
            alt_model = alt['alternative_model']
            if alt_model in price_lookup:
                # Calculate potential savings using actual pricing
                current_pricing = price_lookup[model]
                alt_pricing = price_lookup[alt_model]
                
                # Calculate savings based on input and output costs separately
                current_input_cost = model_metrics['prompt_tokens'] * current_pricing['input_price'] / 1000
                current_output_cost = model_metrics['completion_tokens'] * current_pricing['output_price'] / 1000
                
                alt_input_cost = model_metrics['prompt_tokens'] * alt_pricing['input_price'] / 1000
                alt_output_cost = model_metrics['completion_tokens'] * alt_pricing['output_price'] / 1000
                
                potential_savings = (current_input_cost + current_output_cost) - (alt_input_cost + alt_output_cost)
                
                # Only recommend if savings are significant (>10%)
                if potential_savings > (model_metrics['total_spend'] * 0.1):
                    recommendations.append({
                        'current_model': model,
                        'recommended_model': alt_model,
                        'similarity_score': alt['similarity_score'],
                        'potential_savings': potential_savings,
                        'usage_count': model_metrics['total_requests'],
                        'reason': f"Switch to save {potential_savings:.2f} based on your usage pattern"
                    })
    
    # Sort recommendations by potential savings
    recommendations.sort(key=lambda x: x['potential_savings'], reverse=True)
    return recommendations

@app.route('/api/recommendations')
def get_recommendations():
    # Get query parameters
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    start_date = request.args.get('start_date', (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d'))
    models = request.args.getlist('model')
    
    # Get usage metrics for the period
    metrics = get_model_usage_metrics(start_date, end_date, models if models else None)
    
    # Generate recommendations
    recommendations = analyze_model_usage(metrics)
    
    # Calculate total potential savings
    total_potential_savings = sum(rec['potential_savings'] for rec in recommendations)
    
    return jsonify({
        'recommendations': recommendations,
        'total_potential_savings': total_potential_savings,
        'filters': {
            'granularity': '30d',
            'start_date': start_date,
            'end_date': end_date,
            'models': models,
            'endpoints': request.args.getlist('endpoint')
        }
    })

@app.route('/api/logs')
def get_logs():
    """Get detailed token usage logs with alternative models"""
    try:
        # Get pagination parameters with validation
        try:
            page = max(1, int(request.args.get('page', 1)))
            per_page = max(1, min(100, int(request.args.get('per_page', 50))))
        except ValueError:
            return jsonify({'error': 'Invalid pagination parameters'}), 400
            
        sort_by = request.args.get('sort_by', 'timestamp')
        sort_desc = request.args.get('sort_desc', 'true').lower() == 'true'
        
        # Validate sort_by field
        valid_sort_fields = ['timestamp', 'total_cost', 'total_tokens', 'latency_ms']
        if sort_by not in valid_sort_fields:
            return jsonify({'error': f'Invalid sort field. Must be one of: {valid_sort_fields}'}), 400
        
        # Get filters
        try:
            filters = parse_filters()
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # Start query
        query = app.supabase.table('token_logs').select(
            "*",
            count="exact"
        )
        
        # Apply filters
        query = query.gte('timestamp', filters.start_date.isoformat())
        query = query.lt('timestamp', filters.end_date.isoformat())
        
        if filters.models:
            query = query.in_('model', filters.models)
        
        if filters.endpoints:
            query = query.in_('endpoint_name', filters.endpoints)
            
        if filters.providers:
            query = query.in_('api_provider', filters.providers)
        
        # Apply sorting
        query = query.order(sort_by, desc=sort_desc)
        
        # Get total count first
        count_response = query.execute()
        total_count = count_response.count or 0
        
        # Calculate pagination
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
        page = min(page, total_pages)  # Ensure page doesn't exceed total pages
        
        # Apply pagination
        start = (page - 1) * per_page
        end = start + per_page - 1
        
        # Only apply range if we have data
        if total_count > 0:
            query = query.range(start, end)
        
        # Execute query
        response = query.execute()
        logs = response.data or []
        
        return jsonify({
            'logs': logs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_records': total_count
            },
            'filters': {
                'granularity': filters.time_granularity.value,
                'start_date': filters.start_date.isoformat(),
                'end_date': filters.end_date.isoformat(),
                'models': filters.models,
                'endpoints': filters.endpoints,
                'providers': filters.providers,
                'sort_by': sort_by,
                'sort_desc': sort_desc
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Always use port 5002 unless explicitly overridden by environment variable
    port = int(os.getenv('PORT', '5002'))
    print(f"\nStarting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 