from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

class AnalyticsService:
    """
    Service for analytics data processing and retrieval
    """
    
    def __init__(self, db_client):
        """
        Initialize with a database client
        """
        self.db_client = db_client
    
    def get_summary(self, start_date, end_date, model=None, task=None, interval='month'):
        """
        Get summary analytics for the dashboard overview with filtering and interval support
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            model: Optional model name filter
            task: Optional task/endpoint name filter
            interval: 'day', 'week', or 'month' - adjusts the date range accordingly
        """
        # Adjust date range based on interval
        if interval == 'day':
            # For day view, use only the end date
            start_date = end_date
            print(f"Day view requested: using only {end_date} for summary")
        elif interval == 'week' and start_date != end_date:
            # For week view, get the week containing the end date
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            # Calculate start of the week (Monday)
            start_of_week = end_dt - timedelta(days=end_dt.weekday())
            # Set the date range to the current week
            start_date = start_of_week.strftime('%Y-%m-%d')
            end_date = (start_of_week + timedelta(days=6)).strftime('%Y-%m-%d')
            print(f"Week view requested: using week from {start_date} to {end_date}")
        # month view uses the full date range by default
        
        # Calculate days in range
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        days = (end - start).days + 1
        
        # Get token logs with filtering
        logs = self.db_client.get_token_logs(
            start_date, 
            end_date,
            model=None if model == '*' else model,
            endpoint_name=None if task == '*' else task
        )
        
        if not logs:
            return {
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_cost": 0,
                "avg_latency_ms": 0,
                "top_model": {"name": "none", "usage_percent": 0},
                "time_period": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "days": days,
                    "interval": interval
                }
            }
            
        # Aggregate data
        total_tokens = sum(log.get('total_tokens', 0) for log in logs)
        prompt_tokens = sum(log.get('prompt_tokens', 0) for log in logs)
        completion_tokens = sum(log.get('completion_tokens', 0) for log in logs)
        total_cost = sum(log.get('total_cost', 0) for log in logs)
        
        # Calculate average latency
        total_latency = sum(log.get('latency_ms', 0) for log in logs)
        avg_latency = round(total_latency / len(logs)) if logs else 0
        
        # Find top model
        model_distribution = {}
        for log in logs:
            model_name = log.get('model', 'unknown')
            model_distribution[model_name] = model_distribution.get(model_name, 0) + log.get('total_tokens', 0)
        
        top_model = {"name": "none", "usage_percent": 0}
        if model_distribution:
            top_model_name = max(model_distribution, key=model_distribution.get)
            top_model_tokens = model_distribution[top_model_name]
            top_model_percent = round((top_model_tokens / total_tokens) * 100) if total_tokens > 0 else 0
            top_model = {
                "name": top_model_name,
                "usage_percent": top_model_percent
            }
        
        return {
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_cost": round(total_cost, 2),
            "avg_latency_ms": avg_latency,
            "top_model": top_model,
            "time_period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": days,
                "interval": interval
            }
        }
    
    def get_timeseries(self, start_date, end_date, interval, metric, model=None, task=None):
        """
        Get time series data with filtering support
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            interval: 'day', 'week', or 'month'
            metric: 'tokens' or 'cost'
            model: Optional model name filter
            task: Optional task/endpoint name filter
        """
        print(f"Fetching timeseries data: interval={interval}, metric={metric}, dates={start_date} to {end_date}")
        
        # If no date range specified, calculate appropriate defaults
        if not start_date or not end_date:
            today = datetime.now()
            
            if interval == 'day':
                # For daily view, use today
                start_date = today.strftime('%Y-%m-%d')
                end_date = today.strftime('%Y-%m-%d')
            elif interval == 'week':
                # Calculate the start of the week (Sunday)
                week_start = today - timedelta(days=today.weekday() + 1)
                week_end = week_start + timedelta(days=6)  # Saturday
                
                start_date = week_start.strftime('%Y-%m-%d')
                end_date = week_end.strftime('%Y-%m-%d')
            elif interval == 'month':
                # Calculate the start of the month
                month_start = today.replace(day=1)
                # Calculate the end of the month
                if today.month == 12:
                    next_month = today.replace(year=today.year + 1, month=1, day=1)
                else:
                    next_month = today.replace(month=today.month + 1, day=1)
                month_end = next_month - timedelta(days=1)
                
                start_date = month_start.strftime('%Y-%m-%d')
                end_date = month_end.strftime('%Y-%m-%d')
        
        print(f"Using date range: {start_date} to {end_date}")
        
        # For day view (hourly data), use just one day
        if interval == 'day' and start_date != end_date:
            # Use only the end date for day view to show hourly breakdown
            print(f"Day view requested with date range {start_date} to {end_date}. Using only {end_date} for hourly view.")
            start_date = end_date
            
        # Apply the model and task filters
        filtered_model = None if model == '*' else model
        filtered_task = None if task == '*' else task
            
        # Get the data using our simplified unified method
        data = self.db_client.get_timeseries_data(
            start_date, 
            end_date, 
            interval, 
            metric,
            model=filtered_model,
            endpoint_name=filtered_task
        )
        
        # Ensure we have a full set of data for the time period
        processed_data = self.fill_missing_data_points(start_date, end_date, interval, data, metric)
        
        # Debug the processed data
        if isinstance(processed_data, dict) and 'data' in processed_data:
            print(f"Returning {len(processed_data['data'])} time series data points")
            # Check for any inconsistencies in data structure
            for idx, point in enumerate(processed_data['data']):
                if not isinstance(point, dict):
                    print(f"Warning: Point {idx} is not a dictionary: {type(point)}")
                elif not all(k in point for k in ['display_key', 'value']):
                    print(f"Warning: Point {idx} missing required keys: {point.keys()}")
        else:
            print(f"Warning: Processed data is not in expected format: {type(processed_data)}")
        
        # Return in expected format for the frontend
        # Note: `data` field is already part of processed_data after fill_missing_data_points
        return {
            "data": processed_data.get('data', []) if isinstance(processed_data, dict) else [],
            "time_period": {
                "start_date": start_date,
                "end_date": end_date,
                "interval": interval
            }
        }
    
    def fill_missing_data_points(self, start_date, end_date, interval, existing_data, metric):
        """
        Validate and normalize time series data structure
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            interval: 'day', 'week', or 'month'
            existing_data: List of existing data points
            metric: 'tokens' or 'cost'
            
        Returns:
            Normalized data structure for frontend consumption
        """
        # Ensure we always return a valid data structure
        if not existing_data:
            return {"data": []}
        
        # If data is already a dict with data array, validate it
        if isinstance(existing_data, dict) and 'data' in existing_data:
            # Ensure the data field is a list
            if not isinstance(existing_data['data'], list):
                existing_data['data'] = []
                print("Warning: data.data was not a list, initialized empty list")
            
            # Ensure all data points have consistent structure (numeric values, etc.)
            for item in existing_data['data']:
                if isinstance(item, dict):
                    # Ensure all numeric fields are actually numbers
                    for field in ['value', 'prompt_tokens', 'completion_tokens', 'cost', 'alternative_cost', 'savings']:
                        if field in item and item[field] is not None:
                            try:
                                if field == 'cost' or field == 'alternative_cost' or field == 'savings':
                                    item[field] = float(item[field])
                                else:
                                    item[field] = int(item[field])
                            except (ValueError, TypeError):
                                # If conversion fails, set to 0
                                print(f"Warning: Failed to convert {field} value '{item[field]}' to number, using 0")
                                item[field] = 0 if field != 'cost' and field != 'alternative_cost' and field != 'savings' else 0.0
            
            print(f"Returning validated data dict with {len(existing_data['data'])} data points")
            return existing_data
        
        # If data is a list, wrap it in a dict
        if isinstance(existing_data, list):
            print(f"Wrapping list of {len(existing_data)} items in data dict")
            return {"data": existing_data}
        
        # Default fallback - log the issue
        print(f"Warning: Unknown data structure in fill_missing_data_points: {type(existing_data)}")
        return {"data": []}
    
    def get_model_distribution(self, start_date, end_date, metric, limit, model=None, task=None, interval='month'):
        """
        Get model distribution with filtering support
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            metric: 'tokens' or 'cost'
            limit: Max number of models to return
            model: Optional model name filter
            task: Optional task/endpoint name filter
            interval: 'day', 'week', or 'month' - adjusts the date range accordingly
        """
        # Adjust date range based on interval
        if interval == 'day':
            # For day view, use only the end date
            start_date = end_date
            print(f"Day view requested: using only {end_date} for model distribution")
        elif interval == 'week' and start_date != end_date:
            # For week view, get the week containing the end date
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            # Calculate start of the week (Monday)
            start_of_week = end_dt - timedelta(days=end_dt.weekday())
            # Set the date range to the current week
            start_date = start_of_week.strftime('%Y-%m-%d')
            end_date = (start_of_week + timedelta(days=6)).strftime('%Y-%m-%d')
            print(f"Week view requested: using week from {start_date} to {end_date} for model distribution")
        # month view uses the full date range by default
        
        # Apply the model and task filters
        filtered_model = None if model == '*' else model
        filtered_task = None if task == '*' else task
        
        # Get model distribution from Supabase with filtering
        models = self.db_client.get_model_distribution(
            start_date, 
            end_date, 
            metric,
            model=filtered_model,
            endpoint_name=filtered_task
        )
        
        # Split into main models and "other" category based on limit
        main_models = models[:limit] if models else []
        other_models = models[limit:] if len(models) > limit else []
        
        # Calculate "other" category
        other = {
            "value": sum(model["value"] for model in other_models),
            "percent": sum(model["percent"] for model in other_models),
            "cost": sum(model["cost"] for model in other_models)
        }
        
        return {
            "data": main_models,
            "other": other,
            "time_period": {
                "start_date": start_date,
                "end_date": end_date,
                "interval": interval
            }
        }
    
    def get_feature_usage(self, start_date, end_date, metric, limit, model=None, task=None, interval='month'):
        """
        Get feature usage with filtering support
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            metric: 'tokens' or 'cost'
            limit: Max number of features to return
            model: Optional model name filter
            task: Optional task/endpoint name filter
            interval: 'day', 'week', or 'month' - adjusts the date range accordingly
        """
        # Adjust date range based on interval
        if interval == 'day':
            # For day view, use only the end date
            start_date = end_date
            print(f"Day view requested: using only {end_date} for feature usage")
        elif interval == 'week' and start_date != end_date:
            # For week view, get the week containing the end date
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            # Calculate start of the week (Monday)
            start_of_week = end_dt - timedelta(days=end_dt.weekday())
            # Set the date range to the current week
            start_date = start_of_week.strftime('%Y-%m-%d')
            end_date = (start_of_week + timedelta(days=6)).strftime('%Y-%m-%d')
            print(f"Week view requested: using week from {start_date} to {end_date} for feature usage")
        # month view uses the full date range by default
        
        # Apply the model and task filters
        filtered_model = None if model == '*' else model
        filtered_task = None if task == '*' else task
        
        # Get feature distribution from Supabase with filtering
        features = self.db_client.get_feature_distribution(
            start_date, 
            end_date, 
            metric,
            model=filtered_model,
            endpoint_name=filtered_task
        )
        
        # Limit results as requested
        limited_features = features[:limit] if features else []
        
        return {
            "data": limited_features,
            "time_period": {
                "start_date": start_date,
                "end_date": end_date,
                "interval": interval
            }
        }
    
    def get_logs(self, start_date, end_date, model, feature, page, page_size, sort_by, sort_dir):
        """
        Get paginated and filterable logs
        """
        # Get all logs matching filters
        logs = self.db_client.get_token_logs(start_date, end_date, model, feature)
        
        # Sort logs
        reverse = sort_dir.lower() == 'desc'
        if sort_by in logs[0] if logs else False:
            logs.sort(key=lambda x: x.get(sort_by, x.get("timestamp")), reverse=reverse)
        else:
            # Default sort by timestamp if the sort_by field doesn't exist
            logs.sort(key=lambda x: x.get("timestamp"), reverse=reverse)
        
        # Calculate pagination
        total_items = len(logs)
        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
        
        # Get paginated subset
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_items)
        paginated_logs = logs[start_idx:end_idx] if logs else []
        
        # Process each log entry for consistent field names and types
        processed_logs = []
        for log in paginated_logs:
            processed_log = {
                "id": log.get("id"),
                "timestamp": log.get("timestamp"),
                "model": log.get("model"),
                "prompt_tokens": log.get("prompt_tokens", 0),
                "completion_tokens": log.get("completion_tokens", 0),
                "total_tokens": log.get("total_tokens", 0),
                "total_cost": log.get("total_cost", 0),
                "feature": log.get("endpoint_name", "default"),
                "latency_ms": log.get("latency_ms", 0)
            }
            processed_logs.append(processed_log)
        
        return {
            "data": processed_logs,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages
            },
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "model": model,
                "feature": feature
            }
        } 