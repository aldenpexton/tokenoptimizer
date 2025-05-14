from typing import Dict, Any, Optional

class PricingService:
    @staticmethod
    def calculate_cost(
        prompt_tokens: int, 
        completion_tokens: int, 
        model_pricing: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate the cost of a request based on the number of tokens and model pricing
        
        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            model_pricing: Dictionary containing 'input_price' and 'output_price' per 1K tokens
            
        Returns:
            Dictionary with input_cost, output_cost, and total_cost
        """
        # Calculate input cost (prompt_tokens / 1000 * input_price)
        input_cost = (prompt_tokens / 1000) * model_pricing['input_price']
        
        # Calculate output cost (completion_tokens / 1000 * output_price)
        output_cost = (completion_tokens / 1000) * model_pricing['output_price']
        
        # Calculate total cost
        total_cost = input_cost + output_cost
        
        return {
            'input_cost': round(input_cost, 6),
            'output_cost': round(output_cost, 6),
            'total_cost': round(total_cost, 6)
        } 