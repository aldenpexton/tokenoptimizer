from datetime import datetime, timedelta

class AnalyticsService:
    """
    Service for analytics data processing and retrieval
    """
    
    def __init__(self, db_client):
        """
        Initialize with a database client
        """
        self.db_client = db_client
    
    def get_summary(self, start_date, end_date):
        """
        Get summary analytics for the dashboard overview
        """
        # For now, return mock data. In production, query the database.
        # Calculate days in range
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        days = (end - start).days + 1
        
        return {
            "total_tokens": 1250000,
            "prompt_tokens": 500000,
            "completion_tokens": 750000,
            "total_cost": 24.85,
            "avg_latency_ms": 245,
            "top_model": {
                "name": "claude-3-haiku",
                "usage_percent": 67
            },
            "time_period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": days
            }
        }
    
    def get_timeseries(self, start_date, end_date, interval, metric):
        """
        Get time series data for token usage
        """
        # For now, return mock data. In production, query the database.
        # Generate sample data for each day in range
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        data = []
        current = start
        while current <= end:
            # Generate some sample data with slight variations
            base_value = 42500
            variation = int(base_value * 0.2 * ((current.day % 7) / 7))
            
            prompt_tokens = 17500 + int(variation * 0.4)
            completion_tokens = 25000 + int(variation * 0.6)
            total_tokens = prompt_tokens + completion_tokens
            
            data.append({
                "date": current.strftime('%Y-%m-%d'),
                "value": total_tokens if metric == 'tokens' else 0.85 + (variation * 0.001),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "cost": 0.85 + (variation * 0.001)
            })
            
            current += timedelta(days=1)
        
        return {
            "data": data,
            "time_period": {
                "start_date": start_date,
                "end_date": end_date,
                "interval": interval
            }
        }
    
    def get_model_distribution(self, start_date, end_date, metric, limit):
        """
        Get distribution of token usage by model
        """
        # For now, return mock data. In production, query the database.
        models = [
            {
                "model": "claude-3-haiku",
                "value": 835000 if metric == 'tokens' else 16.7,
                "percent": 67,
                "cost": 16.7
            },
            {
                "model": "gpt-4",
                "value": 250000 if metric == 'tokens' else 7.5,
                "percent": 20,
                "cost": 7.5
            },
            {
                "model": "gpt-3.5-turbo",
                "value": 125000 if metric == 'tokens' else 0.25,
                "percent": 10,
                "cost": 0.25
            },
            {
                "model": "mistral-large",
                "value": 40000 if metric == 'tokens' else 0.4,
                "percent": 3,
                "cost": 0.4
            }
        ]
        
        return {
            "data": models[:limit],
            "other": {
                "value": 0,
                "percent": 0,
                "cost": 0
            } if len(models) <= limit else {
                "value": sum(m["value"] for m in models[limit:]),
                "percent": sum(m["percent"] for m in models[limit:]),
                "cost": sum(m["cost"] for m in models[limit:])
            },
            "time_period": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
    
    def get_feature_usage(self, start_date, end_date, metric, limit):
        """
        Get token usage breakdown by feature/endpoint
        """
        # For now, return mock data. In production, query the database.
        features = [
            {
                "feature": "document_chat",
                "total_tokens": 750000,
                "prompt_tokens": 250000,
                "completion_tokens": 500000,
                "total_cost": 15.0,
                "request_count": 1250,
                "avg_latency_ms": 325,
                "percent": 60
            },
            {
                "feature": "search_assistant",
                "total_tokens": 250000,
                "prompt_tokens": 100000,
                "completion_tokens": 150000,
                "total_cost": 5.0,
                "request_count": 800,
                "avg_latency_ms": 275,
                "percent": 20
            },
            {
                "feature": "content_generation",
                "total_tokens": 125000,
                "prompt_tokens": 50000,
                "completion_tokens": 75000,
                "total_cost": 2.5,
                "request_count": 350,
                "avg_latency_ms": 225,
                "percent": 10
            },
            {
                "feature": "data_analysis",
                "total_tokens": 75000,
                "prompt_tokens": 35000,
                "completion_tokens": 40000,
                "total_cost": 1.5,
                "request_count": 180,
                "avg_latency_ms": 285,
                "percent": 6
            },
            {
                "feature": "code_assistant",
                "total_tokens": 50000,
                "prompt_tokens": 25000,
                "completion_tokens": 25000,
                "total_cost": 0.85,
                "request_count": 120,
                "avg_latency_ms": 315,
                "percent": 4
            }
        ]
        
        return {
            "data": features[:limit],
            "time_period": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
    
    def get_logs(self, start_date, end_date, model, feature, page, page_size, sort_by, sort_dir):
        """
        Get paginated and filterable logs
        """
        # For now, return mock data. In production, query the database.
        logs = []
        
        # Generate 100 sample logs
        for i in range(1, 101):
            # Alternate between a few models
            models = ["claude-3-haiku", "gpt-4", "gpt-3.5-turbo", "mistral-large"]
            model_idx = i % len(models)
            
            # Alternate between a few features
            features = ["document_chat", "search_assistant", "content_generation", "data_analysis", "code_assistant"]
            feature_idx = i % len(features)
            
            # Create sample log entry with varying data
            log_date = datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=(i % 30), hours=(i % 24))
            prompt_tokens = 250 + (i * 5) % 500
            completion_tokens = 300 + (i * 7) % 800
            
            logs.append({
                "id": f"log-{i:03d}",
                "timestamp": log_date.isoformat(),
                "model": models[model_idx],
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "total_cost": round((prompt_tokens + completion_tokens) * 0.00001 * (model_idx + 1), 5),
                "feature": features[feature_idx],
                "latency_ms": 150 + (i * 3) % 300
            })
        
        # Filter by date range
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Include end date
        logs = [log for log in logs if start_dt <= datetime.fromisoformat(log["timestamp"]) < end_dt]
        
        # Filter by model if specified
        if model:
            logs = [log for log in logs if log["model"] == model]
        
        # Filter by feature if specified
        if feature:
            logs = [log for log in logs if log["feature"] == feature]
        
        # Sort logs
        reverse = sort_dir == 'desc'
        logs.sort(key=lambda x: x.get(sort_by, x.get("timestamp")), reverse=reverse)
        
        # Calculate pagination
        total_items = len(logs)
        total_pages = (total_items + page_size - 1) // page_size
        
        # Get paginated subset
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_items)
        paginated_logs = logs[start_idx:end_idx]
        
        return {
            "data": paginated_logs,
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