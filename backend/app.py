from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, UTC, timezone as tz
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from typing import List, Optional, Tuple, Dict, Any, TypedDict
from enum import Enum
from dataclasses import dataclass
import io
import csv
from zoneinfo import ZoneInfo
from postgrest import Client
from functools import lru_cache
import hashlib
import gc
import psutil
import time

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

def create_app():
    # Initialize Flask app
    app = TokenOptimizerApp(__name__)
    
    # Configure CORS with allowed origins
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "https://www.tokenoptimizer.com",
                "http://localhost:3000",  # For local development
                "http://localhost:5173",   # For Vite's default port
                "http://localhost:3002"    # Added for CORS testing
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    # Load environment variables from root directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    print(f"Loading .env from: {env_path}")
    load_dotenv(env_path)

    # Initialize Supabase client
    supabase_url = "https://qregilyvkbwzvudfgxst.supabase.co"
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SUPABASE_KEY length: {len(supabase_key) if supabase_key else 0}")

    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials. Please check your .env file.")

    try:
        # Initialize with minimal configuration and memory settings
        app.supabase = create_client(
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            options=ClientOptions(
                auto_refresh_token=False,     # Disable auto refresh to save memory
                persist_session=False         # Disable session persistence
            )
        )
    except Exception as e:
        print(f"Error initializing Supabase client: {str(e)}")
        raise e

    # Add garbage collection for memory management
    gc.enable()
    gc.collect()

    # Add request cleanup
    @app.after_request
    def cleanup_after_request(response):
        cleanup_cache()
        gc.collect()
        return response

    # Add memory-efficient query helper
    def execute_query_with_limit(query, limit=50):
        """Execute query with pagination to prevent memory issues"""
        try:
            return query.limit(limit).execute()
        except Exception as e:
            print(f"Query error: {str(e)}")
            return None

    # Add memory cleanup for cache
    def cleanup_cache():
        """Cleanup LRU cache when memory usage is high"""
        process = psutil.Process(os.getpid())
        memory_percent = process.memory_percent()
        
        # More aggressive cache cleanup
        if memory_percent > 70:  # Lower threshold for proactive cleanup
            get_cached_metrics_summary.cache_clear()
            get_cached_metrics_trend.cache_clear()
            get_cached_recommendations.cache_clear()
            gc.collect()
        
        # Emergency cleanup
        if memory_percent > 85:
            get_cached_metrics_summary.cache_clear()
            get_cached_metrics_trend.cache_clear()
            get_cached_recommendations.cache_clear()
            gc.collect()
            
            # Clear all module-level caches
            for cache_name, cache_func in list(globals().items()):
                if hasattr(cache_func, 'cache_clear'):
                    cache_func.cache_clear()
            
            # Aggressive garbage collection
            gc.collect(generation=2)

    # Modify existing query functions to use pagination
    def query_token_logs(filters: FilterParams) -> Tuple[List, int]:
        """Query token logs with filters and memory optimization"""
        try:
            # Start with base query and select only needed columns
            query = app.supabase.table('token_logs').select(
                "timestamp, model, endpoint_name, api_provider, prompt_tokens, completion_tokens, total_tokens, latency_ms, input_cost, output_cost",
                count="exact"
            )

            # Apply date filters with timezone handling
            query = query.gte('timestamp', filters.start_date.astimezone(UTC).isoformat())
            query = query.lt('timestamp', filters.end_date.astimezone(UTC).isoformat())

            # Apply filters
            if filters.models:
                query = query.in_('model', filters.models)
            if filters.endpoints:
                query = query.in_('endpoint_name', filters.endpoints)
            if filters.providers:
                query = query.in_('api_provider', filters.providers)

            # Initialize result containers
            all_data = []
            total_count = 0
            page_size = 1000  # Process 1000 records at a time
            
            # Paginate through results
            for start in range(0, 10000, page_size):  # Cap at 10000 records for safety
                response = query.range(start, start + page_size - 1).execute()
                
                if not response.data:
                    break
                    
                all_data.extend(response.data)
                total_count = response.count
                
                # Force garbage collection after each page
                gc.collect()
                
                # Break if we've got all records
                if len(all_data) >= total_count:
                    break

            return all_data, total_count

        except Exception as e:
            print(f"Error querying token logs: {str(e)}")
            return [], 0

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
            # If dates are provided in the request, use those
            end_date = request.args.get('end_date')
            start_date = request.args.get('start_date')
            
            # Parse time granularity
            granularity = request.args.get('granularity', 'month').lower()
            try:
                time_granularity = TimeGranularity(granularity)
            except ValueError:
                time_granularity = TimeGranularity.MONTH
            
            # If dates are not provided, determine them from the data
            if not (start_date and end_date):
                # Query the min and max timestamps
                response = app.supabase.table('token_logs').select(
                    'timestamp'
                ).order('timestamp', desc=True).limit(1).execute()
                
                if response.data:
                    max_date = datetime.fromisoformat(response.data[0]['timestamp'].replace('Z', '+00:00'))
                else:
                    max_date = datetime.now(UTC)
                    
                response = app.supabase.table('token_logs').select(
                    'timestamp'
                ).order('timestamp', desc=False).limit(1).execute()
                
                if response.data:
                    min_date = datetime.fromisoformat(response.data[0]['timestamp'].replace('Z', '+00:00'))
                else:
                    min_date = max_date - timedelta(days=365)
                
                # Use the actual data range if no dates provided
                if not end_date:
                    end_date = max_date.isoformat()
                if not start_date:
                    start_date = min_date.isoformat()
                
                print(f"Using date range from data: {start_date} to {end_date}")
            
            # Clean and validate models (handle both 'model' and 'models')
            models = [
                model.strip()
                for model in (request.args.getlist('model') + request.args.getlist('models'))
                if model and model.strip()
            ]
            
            # Clean and validate endpoints (handle both 'endpoint' and 'endpoints')
            endpoints = [
                endpoint.strip()
                for endpoint in (request.args.getlist('endpoint') + request.args.getlist('endpoints'))
                if endpoint and endpoint.strip()
            ]
            
            # Clean and validate providers (handle both 'provider' and 'providers')
            providers = [
                provider.strip()
                for provider in (request.args.getlist('provider') + request.args.getlist('providers'))
                if provider and provider.strip()
            ]
            
            # Parse and validate dates
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                
                # Ensure start_date is before end_date
                if start_date > end_date:
                    start_date, end_date = end_date, start_date
                    
                # Ensure dates are in UTC
                start_date = start_date.astimezone(UTC)
                end_date = end_date.astimezone(UTC)
                
            except ValueError as e:
                raise ValueError(f"Invalid date format: {str(e)}")
            
            # Remove duplicates while preserving order
            models = list(dict.fromkeys(models))
            endpoints = list(dict.fromkeys(endpoints))
            providers = list(dict.fromkeys(providers))
            
            return FilterParams(
                time_granularity=time_granularity,
                start_date=start_date,
                end_date=end_date,
                models=models,
                endpoints=endpoints,
                providers=providers
            )
        except Exception as e:
            print(f"Error parsing filters: {str(e)}")
            print(f"Request args: {dict(request.args)}")
            raise ValueError(f"Failed to parse filters: {str(e)}")

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

    # Cache key generator
    def make_cache_key(*args, **kwargs):
        # Convert args and kwargs to strings and sort for consistency
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        # Create a hash of the key parts
        return hashlib.md5("".join(key_parts).encode()).hexdigest()

    # Cache decorators with TTL and increased cache size
    @lru_cache(maxsize=32)
    def get_cached_metrics_summary(cache_key: str, ttl_hash: str):
        """Cache for metrics summary with 2 minute TTL"""
        return get_metrics_summary_internal()

    @lru_cache(maxsize=32)
    def get_cached_metrics_trend(cache_key: str, ttl_hash: str):
        """Cache for metrics trend with 2 minute TTL"""
        return get_metrics_trend_internal()

    @lru_cache(maxsize=32)
    def get_cached_recommendations(cache_key: str, ttl_hash: str):
        """Cache for recommendations with 2 minute TTL"""
        return get_recommendations_internal()

    # TTL hash generator (changes every 2 minutes)
    def get_ttl_hash(minutes=2):
        """Return the same value within `minutes` time period"""
        return round(time.time() / (minutes * 60))

    @app.route('/api/filters')
    def get_filters():
        """Get available filter options with their relationships"""
        try:
            # Get all unique values including nulls
            response = app.supabase.table('token_logs').select('model, endpoint_name, api_provider').execute()
            
            if not response.data:
                return jsonify({
                    'models': [],
                    'endpoints': [],
                    'providers': [],
                    'relationships': {
                        'model_endpoints': {},
                        'model_providers': {},
                        'endpoint_providers': {},
                        'provider_models': {},
                        'provider_endpoints': {},
                        'endpoint_models': {}
                    }
                })

            # Build relationships
            model_endpoints = {}  # model -> endpoints
            model_providers = {}  # model -> providers
            endpoint_providers = {}  # endpoint -> providers
            provider_models = {}  # provider -> models
            provider_endpoints = {}  # provider -> endpoints
            endpoint_models = {}  # endpoint -> models

            # Process each log to build relationships
            for row in response.data:
                model = str(row.get('model', 'None'))
                endpoint = str(row.get('endpoint_name', 'None'))
                provider = str(row.get('api_provider', 'None'))

                # Model relationships
                if model not in model_endpoints:
                    model_endpoints[model] = set()
                model_endpoints[model].add(endpoint)

                if model not in model_providers:
                    model_providers[model] = set()
                model_providers[model].add(provider)

                # Endpoint relationships
                if endpoint not in endpoint_providers:
                    endpoint_providers[endpoint] = set()
                endpoint_providers[endpoint].add(provider)

                if endpoint not in endpoint_models:
                    endpoint_models[endpoint] = set()
                endpoint_models[endpoint].add(model)

                # Provider relationships
                if provider not in provider_models:
                    provider_models[provider] = set()
                provider_models[provider].add(model)

                if provider not in provider_endpoints:
                    provider_endpoints[provider] = set()
                provider_endpoints[provider].add(endpoint)

            # Convert sets to sorted lists
            relationships = {
                'model_endpoints': {k: sorted(list(v)) for k, v in model_endpoints.items()},
                'model_providers': {k: sorted(list(v)) for k, v in model_providers.items()},
                'endpoint_providers': {k: sorted(list(v)) for k, v in endpoint_providers.items()},
                'provider_models': {k: sorted(list(v)) for k, v in provider_models.items()},
                'provider_endpoints': {k: sorted(list(v)) for k, v in provider_endpoints.items()},
                'endpoint_models': {k: sorted(list(v)) for k, v in endpoint_models.items()}
            }

            # Get unique values preserving nulls
            unique_models = sorted(list(model_endpoints.keys()))
            unique_endpoints = sorted(list(endpoint_providers.keys()))
            unique_providers = sorted(list(provider_models.keys()))

            return jsonify({
                'models': unique_models,
                'endpoints': unique_endpoints,
                'providers': unique_providers,
                'relationships': relationships,
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
        process = psutil.Process(os.getpid())
        memory_percent = process.memory_percent()
        
        if memory_percent > 90:  # Critical memory usage
            cleanup_cache()  # Force cache cleanup
            gc.collect()
        
        return jsonify({
            'status': 'healthy',
            'memory_usage': memory_percent,
            'timestamp': datetime.now(UTC).isoformat()
        })

    @app.route('/api/metrics/summary')
    def get_metrics_summary():
        """Get summary metrics with filters"""
        try:
            # Parse filters
            filters = parse_filters()
            
            # Generate cache key from filters
            cache_key = make_cache_key(
                'summary',
                filters.start_date.isoformat(),
                filters.end_date.isoformat(),
                *sorted(filters.models or []),
                *sorted(filters.endpoints or []),
                *sorted(filters.providers or [])
            )
            
            # Get cached or fresh data
            data = get_cached_metrics_summary(cache_key, get_ttl_hash())
            
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/metrics/trend')
    def get_metrics_trend():
        """Get metrics trend with filters"""
        try:
            # Parse filters
            filters = parse_filters()
            
            # Generate cache key from filters
            cache_key = make_cache_key(
                'trend',
                filters.start_date.isoformat(),
                filters.end_date.isoformat(),
                *sorted(filters.models or []),
                *sorted(filters.endpoints or []),
                *sorted(filters.providers or [])
            )
            
            # Get cached or fresh data
            data = get_cached_metrics_trend(cache_key, get_ttl_hash())
            
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/metrics/by-model')
    def get_metrics_by_model():
        """Get metrics breakdown by model for the last 12 months"""
        try:
            # Calculate date range
            end_date = datetime.now(UTC)
            start_date = end_date - timedelta(days=365)
            
            # Query data using table API
            response = app.supabase.table('token_logs').select(
                'model',
                'total_cost',
                'total_tokens',
                'endpoint_name',
                'api_provider'
            ).gte(
                'timestamp', 
                start_date.isoformat()
            ).lte(
                'timestamp',
                end_date.isoformat()
            ).execute()
            
            if not response.data:
                return jsonify({
                    'metrics': [],
                    'period': 'last 12 months'
                })
            
            # Aggregate data by model
            model_metrics = {}
            for row in response.data:
                model = row['model']
                if model not in model_metrics:
                    model_metrics[model] = {
                        'model': model,
                        'total_spend': 0,
                        'total_requests': 0,
                        'total_tokens': 0,
                        'endpoints_used': set(),
                        'providers_used': set()
                    }
                
                metrics = model_metrics[model]
                metrics['total_spend'] += float(row['total_cost'])
                metrics['total_requests'] += 1
                metrics['total_tokens'] += int(row['total_tokens'])
                metrics['endpoints_used'].add(row['endpoint_name'])
                metrics['providers_used'].add(row['api_provider'])
            
            # Convert sets to lists and prepare final result
            result = []
            for metrics in model_metrics.values():
                metrics['endpoints_used'] = sorted(list(metrics['endpoints_used']))
                metrics['providers_used'] = sorted(list(metrics['providers_used']))
                result.append(metrics)
            
            # Sort by total spend
            result.sort(key=lambda x: x['total_spend'], reverse=True)
            
            return jsonify({
                'metrics': result,
                'period': 'last 12 months'
            })
        except Exception as e:
            print(f"Error in metrics by model: {str(e)}")
            print(f"Full error details: {repr(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/metrics/by-endpoint')
    def get_metrics_by_endpoint():
        """Get metrics breakdown by endpoint for the last 12 months"""
        try:
            # Calculate date range
            end_date = datetime.now(UTC)
            start_date = end_date - timedelta(days=365)
            
            # Query data using table API
            response = app.supabase.table('token_logs').select(
                'endpoint_name',
                'total_cost',
                'total_tokens',
                'model',
                'api_provider'
            ).gte(
                'timestamp', 
                start_date.isoformat()
            ).lte(
                'timestamp',
                end_date.isoformat()
            ).execute()
            
            if not response.data:
                return jsonify({
                    'metrics': [],
                    'period': 'last 12 months'
                })
            
            # Aggregate data by endpoint
            endpoint_metrics = {}
            for row in response.data:
                endpoint = row['endpoint_name']
                if endpoint not in endpoint_metrics:
                    endpoint_metrics[endpoint] = {
                        'endpoint': endpoint,
                        'total_spend': 0,
                        'total_requests': 0,
                        'total_tokens': 0,
                        'models_used': set(),
                        'providers_used': set()
                    }
                
                metrics = endpoint_metrics[endpoint]
                metrics['total_spend'] += float(row['total_cost'])
                metrics['total_requests'] += 1
                metrics['total_tokens'] += int(row['total_tokens'])
                metrics['models_used'].add(row['model'])
                metrics['providers_used'].add(row['api_provider'])
            
            # Convert sets to lists and prepare final result
            result = []
            for metrics in endpoint_metrics.values():
                metrics['models_used'] = sorted(list(metrics['models_used']))
                metrics['providers_used'] = sorted(list(metrics['providers_used']))
                result.append(metrics)
            
            # Sort by total spend
            result.sort(key=lambda x: x['total_spend'], reverse=True)
            
            return jsonify({
                'metrics': result,
                'period': 'last 12 months'
            })
        except Exception as e:
            print(f"Error in metrics by endpoint: {str(e)}")
            print(f"Full error details: {repr(e)}")
            return jsonify({'error': str(e)}), 500

    def get_model_usage_metrics(start_date: str, end_date: str, models: Optional[List[str]] = None) -> Dict[str, ModelMetrics]:
        """Get usage metrics for models in the given date range"""
        try:
            # Build query with filters
            query = app.supabase.table('token_logs').select(
                'model',
                'total_cost',
                'total_tokens',
                'prompt_tokens',
                'completion_tokens',
                'input_cost',
                'output_cost',
                'latency_ms'
            )
            
            # Apply date filters
            query = query.gte('timestamp', start_date)
            query = query.lt('timestamp', end_date)
            
            # Apply model filter
            if models:
                query = query.in_('model', models)
            
            # Execute query
            response = query.execute()
            
            if not response.data:
                return {}
            
            # Calculate metrics per model
            model_metrics = {}
            for row in response.data:
                model = row['model']
                if model not in model_metrics:
                    model_metrics[model] = {
                        'total_spend': 0,
                        'total_requests': 0,
                        'total_tokens': 0,
                        'prompt_tokens': 0,
                        'completion_tokens': 0,
                        'input_cost': 0,
                        'output_cost': 0,
                        'avg_latency': 0,
                        'latency_samples': 0
                    }
                
                metrics = model_metrics[model]
                metrics['total_spend'] += float(row['total_cost'])
                metrics['total_requests'] += 1
                metrics['total_tokens'] += int(row['total_tokens'])
                metrics['prompt_tokens'] += int(row['prompt_tokens'])
                metrics['completion_tokens'] += int(row['completion_tokens'])
                metrics['input_cost'] += float(row['input_cost'])
                metrics['output_cost'] += float(row['output_cost'])
                
                # Handle latency calculation
                if row['latency_ms'] is not None:
                    latency = float(row['latency_ms'])
                    current_avg = metrics['avg_latency']
                    current_samples = metrics['latency_samples']
                    
                    # Update running average
                    metrics['avg_latency'] = (current_avg * current_samples + latency) / (current_samples + 1)
                    metrics['latency_samples'] += 1
                
            # Clean up latency calculation
            for metrics in model_metrics.values():
                if metrics['latency_samples'] == 0:
                    metrics['avg_latency'] = 0
                del metrics['latency_samples']
            
            return model_metrics
        except Exception as e:
            print(f"Error in get_model_usage_metrics: {str(e)}")
            print(f"Full error details: {repr(e)}")
            return {}

    def get_metrics_summary_internal():
        """Internal function to get metrics summary from database"""
        try:
            # Parse filters
            filters = parse_filters()
            
            # Build base query with filters
            query = app.supabase.table('token_logs').select(
                'total_cost',
                'total_tokens',
                'api_provider',
                'model',
                'endpoint_name'
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

            # Initialize aggregation dictionaries
            provider_metrics = {}
            model_metrics = {}
            endpoint_metrics = {}
            total_spend = 0
            total_requests = 0
            
            # Process data in chunks
            page_size = 5000
            start = 0
            
            while True:
                response = query.range(start, start + page_size - 1).execute()
                if not response.data:
                    break
                    
                # Process chunk
                for row in response.data:
                    spend = float(row['total_cost'] or 0)
                    tokens = int(row['total_tokens'] or 0)
                    
                    # Update totals
                    total_spend += spend
                    total_requests += 1
                    
                    # Update provider metrics
                    provider = row['api_provider']
                    if provider not in provider_metrics:
                        provider_metrics[provider] = {'total_spend': 0, 'total_requests': 0, 'total_tokens': 0}
                    provider_metrics[provider]['total_spend'] += spend
                    provider_metrics[provider]['total_requests'] += 1
                    provider_metrics[provider]['total_tokens'] += tokens
                    
                    # Update model metrics
                    model = row['model']
                    if model not in model_metrics:
                        model_metrics[model] = {'total_spend': 0, 'total_requests': 0, 'total_tokens': 0}
                    model_metrics[model]['total_spend'] += spend
                    model_metrics[model]['total_requests'] += 1
                    model_metrics[model]['total_tokens'] += tokens
                    
                    # Update endpoint metrics
                    endpoint = row['endpoint_name']
                    if endpoint not in endpoint_metrics:
                        endpoint_metrics[endpoint] = {'total_spend': 0, 'total_requests': 0, 'total_tokens': 0}
                    endpoint_metrics[endpoint]['total_spend'] += spend
                    endpoint_metrics[endpoint]['total_requests'] += 1
                    endpoint_metrics[endpoint]['total_tokens'] += tokens
                
                # Move to next page
                start += page_size
                
                # Force garbage collection between chunks
                gc.collect()

            return {
                'total_spend': total_spend,
                'total_requests': total_requests,
                'avg_cost_per_request': total_spend / total_requests if total_requests > 0 else 0,
                'provider_breakdown': provider_metrics,
                'model_breakdown': model_metrics,
                'endpoint_breakdown': endpoint_metrics,
                'period': 'filtered'
            }
        except Exception as e:
            print(f"Error in get_metrics_summary_internal: {str(e)}")
            return {
                'error': str(e),
                'total_spend': 0,
                'total_requests': 0,
                'avg_cost_per_request': 0,
                'provider_breakdown': {},
                'model_breakdown': {},
                'endpoint_breakdown': {},
                'period': 'filtered'
            }

    def get_metrics_trend_internal():
        """Internal function to get metrics trend from database"""
        try:
            # Parse filters
            filters = parse_filters()
            print(f"Trend filters - start: {filters.start_date}, end: {filters.end_date}, granularity: {filters.time_granularity}")
            
            # Initialize time buckets
            time_buckets = {}
            current = filters.start_date
            while current < filters.end_date:
                # Create bucket key based on granularity
                if filters.time_granularity == TimeGranularity.HOUR:
                    bucket_key = current.strftime('%Y-%m-%d %H:00:00')
                elif filters.time_granularity == TimeGranularity.DAY:
                    bucket_key = current.strftime('%Y-%m-%d 00:00:00')
                elif filters.time_granularity == TimeGranularity.WEEK:
                    # Get start of week
                    week_start = current - timedelta(days=current.weekday())
                    bucket_key = week_start.strftime('%Y-%m-%d 00:00:00')
                elif filters.time_granularity == TimeGranularity.MONTH:
                    bucket_key = current.strftime('%Y-%m-01 00:00:00')
                else:  # YEAR
                    bucket_key = current.strftime('%Y-01-01 00:00:00')
                
                time_buckets[bucket_key] = {
                    'total_spend': 0,
                    'total_requests': 0,
                    'total_tokens': 0
                }
                
                # Increment current based on granularity
                if filters.time_granularity == TimeGranularity.HOUR:
                    current += timedelta(hours=1)
                elif filters.time_granularity == TimeGranularity.DAY:
                    current += timedelta(days=1)
                elif filters.time_granularity == TimeGranularity.WEEK:
                    current += timedelta(weeks=1)
                elif filters.time_granularity == TimeGranularity.MONTH:
                    if current.month == 12:
                        current = current.replace(year=current.year + 1, month=1)
                    else:
                        current = current.replace(month=current.month + 1)
                else:  # YEAR
                    current = current.replace(year=current.year + 1)
            
            print(f"Created {len(time_buckets)} time buckets")
            
            # Build base query
            query = app.supabase.table('token_logs').select(
                'timestamp',
                'total_cost',
                'total_tokens'
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
            
            # Process data in chunks
            page_size = 5000
            start = 0
            total_rows = 0
            
            while True:
                response = query.range(start, start + page_size - 1).execute()
                if not response.data:
                    break
                
                chunk_size = len(response.data)
                total_rows += chunk_size
                print(f"Processing chunk of {chunk_size} rows (total so far: {total_rows})")
                
                # Process chunk
                for row in response.data:
                    timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                    
                    # Create bucket key based on granularity
                    if filters.time_granularity == TimeGranularity.HOUR:
                        bucket_key = timestamp.strftime('%Y-%m-%d %H:00:00')
                    elif filters.time_granularity == TimeGranularity.DAY:
                        bucket_key = timestamp.strftime('%Y-%m-%d 00:00:00')
                    elif filters.time_granularity == TimeGranularity.WEEK:
                        # Get start of week
                        week_start = timestamp - timedelta(days=timestamp.weekday())
                        bucket_key = week_start.strftime('%Y-%m-%d 00:00:00')
                    elif filters.time_granularity == TimeGranularity.MONTH:
                        bucket_key = timestamp.strftime('%Y-%m-01 00:00:00')
                    else:  # YEAR
                        bucket_key = timestamp.strftime('%Y-01-01 00:00:00')
                    
                    if bucket_key in time_buckets:
                        time_buckets[bucket_key]['total_spend'] += float(row['total_cost'] or 0)
                        time_buckets[bucket_key]['total_requests'] += 1
                        time_buckets[bucket_key]['total_tokens'] += int(row['total_tokens'] or 0)
                    else:
                        print(f"Warning: Data point at {timestamp} ({bucket_key}) falls outside bucket range")
                
                # Move to next page
                start += page_size
                
                # Force garbage collection between chunks
                gc.collect()
            
            print(f"Processed {total_rows} total rows")
            
            # Convert buckets to sorted list
            metrics = []
            for bucket_key, bucket_metrics in sorted(time_buckets.items()):
                # Format the period label based on granularity
                try:
                    timestamp = datetime.strptime(bucket_key, '%Y-%m-%d %H:00:00')
                    if filters.time_granularity == TimeGranularity.HOUR:
                        period_label = timestamp.strftime('%I %p')
                    elif filters.time_granularity == TimeGranularity.DAY:
                        period_label = timestamp.strftime('%b %d')
                    elif filters.time_granularity == TimeGranularity.WEEK:
                        period_label = f"Week of {timestamp.strftime('%b %d')}"
                    elif filters.time_granularity == TimeGranularity.MONTH:
                        period_label = timestamp.strftime('%b %Y')
                    else:  # YEAR
                        period_label = timestamp.strftime('%Y')
                except ValueError as e:
                    print(f"Error parsing date {bucket_key}: {str(e)}")
                    period_label = bucket_key

                metrics.append({
                    'period': bucket_key,
                    'period_label': period_label,
                    'total_spend': bucket_metrics['total_spend'],
                    'total_requests': bucket_metrics['total_requests'],
                    'total_tokens': bucket_metrics['total_tokens'],
                    'models_used': [],  # We'll add this later if needed
                    'endpoints_used': [],  # We'll add this later if needed
                    'providers_used': []  # We'll add this later if needed
                })
            
            print(f"Returning {len(metrics)} metrics buckets")
            return {
                'metrics': metrics,
                'period': filters.time_granularity.value
            }
        except Exception as e:
            print(f"Error in get_metrics_trend_internal: {str(e)}")
            print(f"Full error details: {repr(e)}")
            return {
                'error': str(e),
                'metrics': [],
                'period': filters.time_granularity.value
            }

    def analyze_model_usage(metrics: Dict[str, ModelMetrics]) -> List[Recommendation]:
        recommendations: List[Recommendation] = []
        
        try:
            # Get model alternatives
            alternatives = app.supabase.table('model_alternatives').select(
                'source_model',
                'alternative_model',
                'similarity_score'
            ).eq('is_recommended', True).execute()
            
            # Get pricing data
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
            
            # Process each model's metrics
            for model, model_metrics in metrics.items():
                # Find alternatives for this model
                model_alts = [alt for alt in alternatives.data if alt['source_model'] == model]
                
                for alt in model_alts:
                    alt_model = alt['alternative_model']
                    if alt_model in price_lookup:
                        # Calculate savings using pricing lookup
                        current_pricing = price_lookup[model]
                        alt_pricing = price_lookup[alt_model]
                        
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
                            
                            # Force garbage collection after each significant operation
                            if len(recommendations) % 10 == 0:
                                gc.collect()
            
            # Sort recommendations by potential savings
            recommendations.sort(key=lambda x: x['potential_savings'], reverse=True)
            return recommendations  # Return all recommendations
            
        except Exception as e:
            print(f"Error in analyze_model_usage: {str(e)}")
            return []

    @app.route('/api/recommendations')
    def get_recommendations():
        """Get recommendations with filters"""
        try:
            # Parse filters
            filters = parse_filters()
            
            # Generate cache key from filters
            cache_key = make_cache_key(
                'recommendations',
                filters.start_date.isoformat(),
                filters.end_date.isoformat(),
                *sorted(filters.models or []),
                *sorted(filters.endpoints or []),
                *sorted(filters.providers or [])
            )
            
            # Get cached or fresh data
            data = get_cached_recommendations(cache_key, get_ttl_hash())
            
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Internal functions that do the actual work
    def get_recommendations_internal():
        """Internal function to get recommendations from database"""
        try:
            # Parse filters
            filters = parse_filters()
            
            # Get usage metrics for the period
            metrics = get_model_usage_metrics(filters.start_date.isoformat(), filters.end_date.isoformat(), filters.models if filters.models else None)
            
            # Generate recommendations
            recommendations = analyze_model_usage(metrics)
            
            # Calculate total potential savings
            total_potential_savings = sum(rec['potential_savings'] for rec in recommendations)
            
            return {
                'recommendations': recommendations,
                'total_potential_savings': total_potential_savings,
                'filters': {
                    'granularity': '30d',
                    'start_date': filters.start_date.isoformat(),
                    'end_date': filters.end_date.isoformat(),
                    'models': filters.models,
                    'endpoints': filters.endpoints
                }
            }
        except Exception as e:
            print(f"Error in recommendations: {str(e)}")
            print(f"Full error details: {repr(e)}")
            raise

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

    # Add memory monitoring endpoint
    @app.route('/api/system/memory', methods=['GET'])
    def get_memory_stats():
        """Get current memory usage statistics"""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return jsonify({
            'rss': memory_info.rss / 1024 / 1024,  # RSS in MB
            'vms': memory_info.vms / 1024 / 1024,  # VMS in MB
            'percent': process.memory_percent(),
            'num_threads': process.num_threads(),
            'connections': len(process.connections()),
            'open_files': len(process.open_files()),
            'timestamp': datetime.now(tz.utc).isoformat()
        })

    return app

# Only create the app if running directly (not through gunicorn)
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5002) 