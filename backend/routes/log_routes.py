from flask import Blueprint, request, jsonify
from db.supabase_client import SupabaseClient
from services.pricing_service import PricingService
from utils.validators import validate_log_payload

# Create blueprint
log_bp = Blueprint('log', __name__)

# Initialize Supabase client
supabase_client = SupabaseClient()

@log_bp.route('/log', methods=['POST'])
def log_token_usage():
    """
    Endpoint to log LLM token usage
    
    Accepts a JSON payload with:
    - model: the LLM model used
    - prompt_tokens: number of input tokens
    - completion_tokens: number of output tokens
    - total_tokens: sum of input and output tokens
    - latency_ms: request latency in milliseconds
    - endpoint_name: (optional) name of the feature/endpoint using the LLM
    - timestamp: (optional) when the request occurred
    
    Returns the logged record with cost information
    """
    # Get JSON data from request
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate payload
    is_valid, error_message, cleaned_data = validate_log_payload(data)
    
    if not is_valid:
        return jsonify({"error": error_message}), 400
    
    # Get model pricing information
    model_pricing = supabase_client.get_model_pricing(cleaned_data['model'])
    
    if not model_pricing:
        return jsonify({
            "error": f"Pricing information not found for model: {cleaned_data['model']}"
        }), 404
    
    # Calculate costs
    cost_data = PricingService.calculate_cost(
        prompt_tokens=cleaned_data['prompt_tokens'],
        completion_tokens=cleaned_data['completion_tokens'],
        model_pricing=model_pricing
    )
    
    # Merge data for insertion
    log_data = {**cleaned_data, **cost_data}
    
    # Insert into database
    result = supabase_client.insert_token_log(log_data)
    
    if result:
        return jsonify({
            "message": "Token usage logged successfully",
            "log": result
        }), 201
    else:
        return jsonify({"error": "Failed to log token usage"}), 500 