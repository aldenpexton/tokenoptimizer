from typing import Dict, Any, Optional, Tuple
import datetime

def validate_log_payload(payload: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Validate the log payload and return a tuple of (is_valid, error_message, cleaned_data)
    
    Required fields:
    - model: str
    - prompt_tokens: int
    - completion_tokens: int
    - total_tokens: int
    - latency_ms: int
    
    Optional fields:
    - endpoint_name: str (defaults to 'default')
    - timestamp: str (defaults to current time)
    - api_provider: str (default is extracted from model name)
    """
    # Initialize cleaned data
    cleaned_data = {}
    
    # Check for required fields
    required_fields = [
        'model', 'prompt_tokens', 'completion_tokens', 
        'total_tokens', 'latency_ms'
    ]
    
    for field in required_fields:
        if field not in payload:
            return False, f"Missing required field: {field}", {}
    
    # Validate field types and clean data
    try:
        # Required fields
        cleaned_data['model'] = str(payload['model'])
        cleaned_data['prompt_tokens'] = int(payload['prompt_tokens'])
        cleaned_data['completion_tokens'] = int(payload['completion_tokens'])
        cleaned_data['total_tokens'] = int(payload['total_tokens'])
        cleaned_data['latency_ms'] = int(payload['latency_ms'])
        
        # Optional fields with defaults
        cleaned_data['endpoint_name'] = str(payload.get('endpoint_name', 'default'))
        
        # Parse timestamp if provided, otherwise use current time
        if 'timestamp' in payload:
            try:
                # Store as ISO format string, Supabase will handle conversion
                timestamp = payload['timestamp']
                # If it's a string, we'll keep it, if it's something else, convert to ISO
                if not isinstance(timestamp, str):
                    # If it's a datetime, convert to ISO
                    if isinstance(timestamp, datetime.datetime):
                        cleaned_data['timestamp'] = timestamp.isoformat()
                    else:
                        # Try to convert to string
                        cleaned_data['timestamp'] = str(timestamp)
                else:
                    cleaned_data['timestamp'] = timestamp
            except Exception:
                return False, "Invalid timestamp format", {}
        
        # Determine API provider from model name if not provided
        if 'api_provider' in payload:
            cleaned_data['api_provider'] = str(payload['api_provider'])
        else:
            # Simple heuristic to determine provider from model name
            model = cleaned_data['model'].lower()
            if 'gpt' in model:
                cleaned_data['api_provider'] = 'OpenAI'
            elif 'claude' in model:
                cleaned_data['api_provider'] = 'Anthropic'
            elif 'mistral' in model:
                cleaned_data['api_provider'] = 'Mistral'
            else:
                cleaned_data['api_provider'] = 'Unknown'
                
        # Validate token counts
        if cleaned_data['prompt_tokens'] < 0 or cleaned_data['completion_tokens'] < 0:
            return False, "Token counts cannot be negative", {}
            
        if cleaned_data['total_tokens'] != cleaned_data['prompt_tokens'] + cleaned_data['completion_tokens']:
            cleaned_data['total_tokens'] = cleaned_data['prompt_tokens'] + cleaned_data['completion_tokens']
        
        return True, None, cleaned_data
        
    except ValueError as e:
        return False, f"Type validation error: {str(e)}", {} 