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
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

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

    def get_model_alternatives(self, model: str) -> List[Dict[str, Any]]:
        """
        Get cheaper alternative models for a given model
        
        Args:
            model: The source model to find alternatives for
            
        Returns:
            List of alternative models with pricing information
        """
        # First check if the model exists in alternatives table
        response = self.client.table('model_alternatives') \
            .select('*') \
            .eq('source_model', model) \
            .order('similarity_score', desc=True) \
            .execute()
            
        if not response.data:
            return []
            
        # For each alternative, get the pricing info
        result = []
        for alt in response.data:
            # Get source model pricing
            source_pricing = self.get_model_pricing(model)
            
            # Get alternative model pricing
            alt_pricing = self.get_model_pricing(alt['alternative_model'])
            
            if source_pricing and alt_pricing:
                result.append({
                    'source_model': model,
                    'alternative_model': alt['alternative_model'],
                    'similarity_score': alt['similarity_score'],
                    'source_input_price': source_pricing['input_price'],
                    'source_output_price': source_pricing['output_price'],
                    'alt_input_price': alt_pricing['input_price'],
                    'alt_output_price': alt_pricing['output_price'],
                    'notes': alt['notes'],
                    'is_recommended': alt['is_recommended']
                })
                
        return result

    def insert_token_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a new token usage log into the token_logs table
        """
        response = self.client.table('token_logs') \
            .insert(log_data) \
            .execute()
        
        return response.data[0] if response.data else None

    def get_token_logs(self, start_date: str, end_date: str, 
                      model: Optional[str] = None, 
                      endpoint_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve token logs within a date range with optional filtering
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            model: Optional model name to filter by
            endpoint_name: Optional endpoint/feature name to filter by
            
        Returns:
            List of token log records
        """
        # Convert dates to include time for proper range query
        # Ensure we capture the full day range inclusive of end date
        start_datetime = f"{start_date}T00:00:00"
        end_datetime = f"{end_date}T23:59:59"
        
        # For debugging
        print(f"Querying logs from {start_datetime} to {end_datetime}")
        
        # Start building the query
        query = self.client.table('token_logs') \
            .select('*') \
            .gte('timestamp', start_datetime) \
            .lte('timestamp', end_datetime)
        
        # Add optional filters
        if model:
            query = query.eq('model', model)
        
        if endpoint_name:
            query = query.eq('endpoint_name', endpoint_name)
        
        # Execute the query
        response = query.execute()
        
        # For debugging
        if response.data:
            print(f"Found {len(response.data)} logs in date range")
        else:
            print("No logs found in date range")
            
        return response.data if response.data else []
    
    def get_token_stats(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get aggregated token statistics for the summary dashboard
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dictionary with aggregated token stats
        """
        logs = self.get_token_logs(start_date, end_date)
        
        if not logs:
            return {
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_cost": 0,
                "avg_latency_ms": 0
            }
        
        # Aggregate data
        total_tokens = sum(log.get('total_tokens', 0) for log in logs)
        prompt_tokens = sum(log.get('prompt_tokens', 0) for log in logs)
        completion_tokens = sum(log.get('completion_tokens', 0) for log in logs)
        total_cost = sum(log.get('total_cost', 0) for log in logs)
        
        # Calculate average latency
        total_latency = sum(log.get('latency_ms', 0) for log in logs)
        avg_latency = round(total_latency / len(logs)) if logs else 0
        
        return {
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_cost": round(total_cost, 2),
            "avg_latency_ms": avg_latency
        }
    
    def get_model_distribution(self, start_date: str, end_date: str, 
                               metric: str = 'tokens',
                               model: Optional[str] = None,
                               endpoint_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get token or cost distribution by model
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            metric: 'tokens' or 'cost'
            model: Optional model filter
            endpoint_name: Optional endpoint/feature filter
            
        Returns:
            List of model usage data
        """
        # Get logs with filtering
        logs = self.get_token_logs(
            start_date, 
            end_date, 
            model=model, 
            endpoint_name=endpoint_name
        )
        
        if not logs:
            return []
        
        # Group by model
        model_data = {}
        for log in logs:
            model_name = log.get('model', 'unknown')
            if model_name not in model_data:
                model_data[model_name] = {
                    'total_tokens': 0,
                    'total_cost': 0
                }
            
            model_data[model_name]['total_tokens'] += log.get('total_tokens', 0)
            model_data[model_name]['total_cost'] += log.get('total_cost', 0)
        
        # Calculate grand totals for percentages
        grand_total_tokens = sum(data['total_tokens'] for data in model_data.values())
        grand_total_cost = sum(data['total_cost'] for data in model_data.values())
        
        # Format result
        result = []
        for model_name, data in model_data.items():
            # Calculate percentages as values between 0-100
            tokens_percent = round((data['total_tokens'] / grand_total_tokens) * 100, 1) if grand_total_tokens > 0 else 0
            cost_percent = round((data['total_cost'] / grand_total_cost) * 100, 1) if grand_total_cost > 0 else 0
            
            result.append({
                'model': model_name,
                'value': data['total_tokens'] if metric == 'tokens' else data['total_cost'],
                'percent': tokens_percent if metric == 'tokens' else cost_percent,
                'cost': data['total_cost']
            })
        
        # Sort by value (tokens or cost) descending
        result.sort(key=lambda x: x['value'], reverse=True)
        
        return result
    
    def get_feature_distribution(self, start_date: str, end_date: str, 
                               metric: str = 'tokens',
                               model: Optional[str] = None,
                               endpoint_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get token or cost distribution by feature/endpoint
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            metric: 'tokens' or 'cost'
            model: Optional model filter
            endpoint_name: Optional endpoint/feature filter
            
        Returns:
            List of feature usage data
        """
        # Get logs with filtering
        logs = self.get_token_logs(
            start_date, 
            end_date, 
            model=model, 
            endpoint_name=endpoint_name
        )
        
        if not logs:
            return []
        
        # Group by endpoint/feature
        feature_data = {}
        for log in logs:
            feature = log.get('endpoint_name', 'default')
            if feature not in feature_data:
                feature_data[feature] = {
                    'total_tokens': 0,
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_cost': 0,
                    'request_count': 0,
                    'total_latency': 0,
                    'models': {}
                }
            
            # Update metrics
            feature_data[feature]['total_tokens'] += log.get('total_tokens', 0)
            feature_data[feature]['prompt_tokens'] += log.get('prompt_tokens', 0)
            feature_data[feature]['completion_tokens'] += log.get('completion_tokens', 0)
            feature_data[feature]['total_cost'] += log.get('total_cost', 0)
            feature_data[feature]['request_count'] += 1
            feature_data[feature]['total_latency'] += log.get('latency_ms', 0)
            
            # Track model usage
            model_name = log.get('model', 'unknown')
            if model_name not in feature_data[feature]['models']:
                feature_data[feature]['models'][model_name] = 0
            feature_data[feature]['models'][model_name] += 1
        
        # Format result
        result = []
        for feature_name, data in feature_data.items():
            # Get most commonly used model
            top_model = max(data['models'].items(), key=lambda x: x[1])[0] if data['models'] else 'unknown'
            
            # Calculate average latency
            avg_latency = round(data['total_latency'] / data['request_count']) if data['request_count'] > 0 else 0
            
            result.append({
                'feature': feature_name,
                'model': top_model,
                'total_tokens': data['total_tokens'],
                'prompt_tokens': data['prompt_tokens'],
                'completion_tokens': data['completion_tokens'],
                'cost': round(data['total_cost'], 2),
                'latency_ms': avg_latency,
                'request_count': data['request_count'],
                'value': data['total_tokens'] if metric == 'tokens' else data['total_cost']
            })
        
        # Sort by value (tokens or cost) descending
        result.sort(key=lambda x: x['value'], reverse=True)
        
        return result
        
    def get_timeseries_data(self, start_date: str, end_date: str, 
                           interval: str = 'day',
                           metric: str = 'tokens',
                           model: Optional[str] = None,
                           endpoint_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get time series data for token usage over time
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            interval: Time grouping ('hour', 'day', 'week', 'month')
            metric: 'tokens' or 'cost'
            model: Optional model filter
            endpoint_name: Optional endpoint/feature filter
            
        Returns:
            List of time series data points
        """
        print(f"Fetching timeseries data: interval={interval}, metric={metric}, dates={start_date} to {end_date}")
        
        try:
            # Get logs with filtering
            logs = self.get_token_logs(
                start_date, 
                end_date, 
                model=model, 
                endpoint_name=endpoint_name
            )
            
            if not logs:
                return {"data": []}
                
            # For hour-level granularity, we need a specific date
            if interval == 'day':
                # Special case: For daily view of hour data, use only end_date
                print(f"Day view requested with date range {start_date} to {end_date}. Using only {end_date} for hourly view.")
                
                # Collect logs for just this day by comparing date strings
                target_date_str = end_date  # Format: YYYY-MM-DD
                filtered_logs = []
                
                for log in logs:
                    log_timestamp = log.get('timestamp', '')
                    if log_timestamp and log_timestamp.startswith(target_date_str):
                        filtered_logs.append(log)
                
                logs = filtered_logs
                print(f"Found {len(logs)} logs for {end_date}")
            
            # Sort by timestamp
            logs.sort(key=lambda x: x.get('timestamp', ''))
            
            def extract_date_key(timestamp, interval_type):
                try:
                    # Parse the timestamp into a datetime object
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    
                    if interval_type == 'hour':
                        # Format: "12 PM"
                        return dt.strftime('%-I %p')
                    elif interval_type == 'day':
                        # Format: "May 16"
                        return dt.strftime('%b %-d')
                    elif interval_type == 'week':
                        # For the weekly view, format day of week + day number: "Sun 11"
                        # Sort order is important: Full day name, then day number
                        return dt.strftime('%a %-d')
                    elif interval_type == 'month':
                        # Format: "May 16"
                        return dt.strftime('%b %-d')
                    else:
                        # Default format: full date
                        return dt.strftime('%Y-%m-%d')
                except Exception as e:
                    print(f"Error formatting date key from timestamp {timestamp}: {str(e)}")
                    return "Unknown Date"
            
            def extract_display_date(timestamp, interval_type):
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    
                    if interval_type == 'hour':
                        # Format: "May 16, 12 PM"
                        return dt.strftime('%b %-d, %-I %p')
                    elif interval_type == 'day':
                        # Format: "May 16, 2025"
                        return dt.strftime('%b %-d, %Y')
                    elif interval_type == 'week':
                        # Format day of week with date: "Sunday, May 11" - Full weekday name for better readability
                        return dt.strftime('%A, %b %-d')
                    elif interval_type == 'month':
                        # Format: "May 16, 2025"
                        return dt.strftime('%b %-d, %Y')
                    else:
                        # Default format: full date
                        return dt.strftime('%Y-%m-%d')
                except Exception as e:
                    print(f"Error formatting display date from timestamp {timestamp}: {str(e)}")
                    return "Unknown Date"
            
            # Group data by time interval
            grouped_data = {}
            for log in logs:
                timestamp = log.get('timestamp', '')
                if not timestamp:
                    continue
                    
                # Extract key based on interval
                key = extract_date_key(timestamp, interval)
                display_date = extract_display_date(timestamp, interval)
                
                if key not in grouped_data:
                    grouped_data[key] = {
                        'display_key': key,
                        'display_date': display_date,
                        'value': 0,  # Total tokens or cost
                        'prompt_tokens': 0,
                        'completion_tokens': 0,
                        'cost': 0,
                        'alternative_cost': 0,  # New field for alternative model cost
                        'savings': 0  # New field for potential savings
                    }
                
                # Update metrics - ensure proper numerical handling with robust error handling
                try:
                    # Total tokens
                    tokens = log.get('total_tokens', 0)
                    if tokens is None:
                        tokens = 0
                    elif isinstance(tokens, str):
                        tokens = int(tokens)
                    
                    # Cost
                    cost = log.get('total_cost', 0)
                    if cost is None:
                        cost = 0
                    elif isinstance(cost, str):
                        cost = float(cost)
                    
                    # Prompt tokens
                    prompt_tokens = log.get('prompt_tokens', 0)
                    if prompt_tokens is None:
                        prompt_tokens = 0
                    elif isinstance(prompt_tokens, str):
                        prompt_tokens = int(prompt_tokens)
                    
                    # Completion tokens
                    completion_tokens = log.get('completion_tokens', 0)
                    if completion_tokens is None:
                        completion_tokens = 0
                    elif isinstance(completion_tokens, str):
                        completion_tokens = int(completion_tokens)
                    
                    # Update aggregated values
                    grouped_data[key]['value'] += tokens if metric == 'tokens' else cost
                    grouped_data[key]['prompt_tokens'] += prompt_tokens
                    grouped_data[key]['completion_tokens'] += completion_tokens
                    grouped_data[key]['cost'] += cost
                except Exception as e:
                    print(f"Error processing metrics for log entry: {str(e)}")
                    # Continue with next log entry
                
                # Calculate alternative model cost if we have pricing data
                if metric == 'cost':  # Only calculate for cost view
                    model_name = log.get('model', '')
                    if model_name:
                        try:
                            # Get alternatives for this model
                            alternatives = self.get_model_alternatives(model_name)
                            if alternatives:
                                # Use the first (highest similarity score) alternative
                                alt = alternatives[0]
                                prompt_tokens = log.get('prompt_tokens', 0)
                                completion_tokens = log.get('completion_tokens', 0)
                                
                                # Calculate what this request would have cost with alternative model
                                alt_input_cost = (prompt_tokens / 1000) * float(alt['alt_input_price'])
                                alt_output_cost = (completion_tokens / 1000) * float(alt['alt_output_price'])
                                alt_total_cost = alt_input_cost + alt_output_cost
                                
                                # Add to the alternative cost and savings
                                grouped_data[key]['alternative_cost'] += alt_total_cost
                                grouped_data[key]['savings'] += max(0, cost - alt_total_cost)
                        except Exception as e:
                            # If there's an error getting alternatives, just skip it
                            print(f"Error calculating alternative cost: {str(e)}")
                            continue
            
            # Convert to list and ensure sorted by date
            result = list(grouped_data.values())
            
            # Sort by display key, but need to handle different formats
            if interval == 'hour':
                # Convert to 24-hour format for sorting
                for item in result:
                    hour_str = item['display_key']
                    hour = int(hour_str.split()[0])
                    if 'PM' in hour_str and hour < 12:
                        hour += 12
                    elif 'AM' in hour_str and hour == 12:
                        hour = 0
                    item['sort_key'] = hour
                result.sort(key=lambda x: x['sort_key'])
                for item in result:
                    del item['sort_key']
            elif interval == 'day':
                # Sort by month and day
                for item in result:
                    month_day = item['display_key'].split()
                    month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(month_day[0])
                    day = int(month_day[1])
                    item['sort_key'] = month * 100 + day
                result.sort(key=lambda x: x['sort_key'])
                for item in result:
                    del item['sort_key']
            elif interval == 'week':
                # Sort by day of week
                weekday_order = {'Sun': 0, 'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6}
                for item in result:
                    if 'display_key' not in item or not item['display_key']:
                        item['sort_key'] = 9999  # Put invalid entries at the end
                        continue
                        
                    day_parts = item['display_key'].split()
                    weekday = day_parts[0] if day_parts else 'Unknown'  # 'Sun', 'Mon', etc.
                    
                    # Default to 0 if we can't parse the day number
                    day = 0
                    if len(day_parts) > 1:
                        try:
                            day = int(day_parts[1])
                        except (ValueError, TypeError):
                            print(f"Warning: Could not parse day number from '{item['display_key']}'")
                            
                    # Sort by weekday order first, then by day number
                    item['sort_key'] = weekday_order.get(weekday, 7) * 100 + day
                    
                # Sort by our computed sort key
                result.sort(key=lambda x: x.get('sort_key', 9999))
                
                # Clean up temporary sort keys
                for item in result:
                    if 'sort_key' in item:
                        del item['sort_key']
                        
                print(f"Week view sorted: {[item.get('display_key') for item in result]}")
            elif interval == 'month':
                for item in result:
                    month_day = item['display_key'].split()
                    month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(month_day[0])
                    # Handle different date formats - May 13 vs May 2025
                    if len(month_day) > 1:
                        try:
                            # If using day-based format (May 13)
                            if ',' in month_day[1]:
                                day = int(month_day[1].replace(',', ''))
                                item['sort_key'] = month * 100 + day
                            else:
                                # Using year-based format (May 2025)
                                year = int(month_day[1])
                                item['sort_key'] = year * 100 + month
                        except (ValueError, IndexError):
                            # Handle any parsing errors
                            item['sort_key'] = month * 100
                    else:
                        item['sort_key'] = month * 100
                result.sort(key=lambda x: x.get('sort_key', 0))
                for item in result:
                    if 'sort_key' in item:
                        del item['sort_key']
            
            print(f"Processing {len(logs)} logs for timeseries from {start_date} to {end_date}")
            print(f"Generated {len(result)} data points for {interval} view")
            
            # Always return a dictionary with a data field containing an array
            if not result:
                print("Warning: No data points generated, returning empty data array")
                # If there's no data, create a sample data point with 0 values
                # This helps the frontend still render a chart with a 0 value
                if interval == 'day':
                    display_key = datetime.now().strftime('%-I %p')
                    display_date = datetime.now().strftime('%b %-d, %-I %p')
                elif interval == 'week':
                    # Get the Sunday of this week
                    sunday = datetime.now() - timedelta(days=datetime.now().weekday() + 1)
                    display_key = sunday.strftime('%b %-d')
                    display_date = f"{sunday.strftime('%b %-d')} - {(sunday + timedelta(days=6)).strftime('%-d')}, {sunday.strftime('%Y')}"
                else:  # month
                    display_key = datetime.now().strftime('%b %Y')
                    display_date = datetime.now().strftime('%B %Y')
                
                sample_point = {
                    'display_key': display_key,
                    'display_date': display_date,
                    'value': 0,
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'cost': 0,
                    'alternative_cost': 0,
                    'savings': 0
                }
                
                return {"data": [sample_point]}
                
            return {"data": result}
        except Exception as e:
            # Log the error and return an empty dataset
            print(f"Error generating time series data: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"data": []}

    def get_distinct_values(self, field: str, start_date: str = None, end_date: str = None) -> List[str]:
        """
        Get distinct values for a field from the token_logs table
        
        Args:
            field: The field to get distinct values for
            start_date: Optional start date filter in YYYY-MM-DD format
            end_date: Optional end date filter in YYYY-MM-DD format
            
        Returns:
            List of distinct values
        """
        # If dates specified, use them, otherwise use recent logs
        if not (start_date and end_date):
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        # Convert dates to include time for proper range query
        start_datetime = f"{start_date}T00:00:00"
        end_datetime = f"{end_date}T23:59:59"
        
        # Get distinct values for the field
        query = self.client.table('token_logs') \
            .select(field) \
            .gte('timestamp', start_datetime) \
            .lte('timestamp', end_datetime) \
            .execute()
        
        if not query.data:
            return []
        
        # Extract unique values
        values = set()
        for item in query.data:
            if field in item and item[field]:
                values.add(item[field])
        
        return sorted(list(values)) 