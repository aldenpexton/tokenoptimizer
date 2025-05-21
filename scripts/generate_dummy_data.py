#!/usr/bin/env python3
"""
TokenOptimizer Dummy Data Generator

This script generates realistic dummy data for the TokenOptimizer dashboard
development and testing. It creates token usage logs, model pricing data,
and model alternatives.

Usage:
    python generate_dummy_data.py [--days=30] [--entries-per-day=25]

Options:
    --days              Number of days of historical data to generate (default: 30)
    --entries-per-day   Average number of entries per day (default: 25)
"""

import json
import os
import random
import uuid
from datetime import datetime, timedelta
import argparse

# Define models with realistic pricing
MODELS = [
    {"name": "gpt-3.5-turbo", "input_price": 0.0005, "output_price": 0.0015, "provider": "OpenAI"},
    {"name": "gpt-4", "input_price": 0.03, "output_price": 0.06, "provider": "OpenAI"},
    {"name": "gpt-4-turbo", "input_price": 0.01, "output_price": 0.03, "provider": "OpenAI"},
    {"name": "claude-3-opus", "input_price": 0.015, "output_price": 0.075, "provider": "Anthropic"},
    {"name": "claude-3-sonnet", "input_price": 0.003, "output_price": 0.015, "provider": "Anthropic"},
    {"name": "claude-3-haiku", "input_price": 0.00025, "output_price": 0.00125, "provider": "Anthropic"},
    {"name": "llama-3-70b", "input_price": 0.001, "output_price": 0.002, "provider": "Meta"},
    {"name": "mistral-medium", "input_price": 0.002, "output_price": 0.006, "provider": "Mistral"}
]

# Define realistic features/endpoints
FEATURES = [
    {"name": "text-to-sql", "avg_prompt_tokens": 800, "avg_completion_tokens": 400},
    {"name": "chat-assistant", "avg_prompt_tokens": 600, "avg_completion_tokens": 250},
    {"name": "summarization", "avg_prompt_tokens": 1200, "avg_completion_tokens": 350},
    {"name": "extraction", "avg_prompt_tokens": 900, "avg_completion_tokens": 300},
    {"name": "translation", "avg_prompt_tokens": 700, "avg_completion_tokens": 250},
    {"name": "code-generation", "avg_prompt_tokens": 500, "avg_completion_tokens": 800},
    {"name": "classification", "avg_prompt_tokens": 400, "avg_completion_tokens": 100}
]

def generate_token_logs(days=30, entries_per_day=25):
    """Generate realistic token usage logs"""
    logs = []
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    current_date = start_date
    while current_date <= end_date:
        # Create some variation in daily entries
        daily_entries = random.randint(
            int(entries_per_day * 0.8), 
            int(entries_per_day * 1.2)
        )
        
        for _ in range(daily_entries):
            # Randomly select model and feature with some weighting
            # to create more realistic patterns (some models used more than others)
            model_weights = [0.3, 0.1, 0.15, 0.05, 0.2, 0.1, 0.05, 0.05]
            feature_weights = [0.25, 0.3, 0.15, 0.1, 0.1, 0.05, 0.05]
            
            model = random.choices(MODELS, weights=model_weights, k=1)[0]
            feature = random.choices(FEATURES, weights=feature_weights, k=1)[0]
            
            # Add some variation to the average token counts
            variation_factor = random.uniform(0.7, 1.3)
            prompt_tokens = int(feature["avg_prompt_tokens"] * variation_factor)
            
            variation_factor = random.uniform(0.7, 1.3)
            completion_tokens = int(feature["avg_completion_tokens"] * variation_factor)
            
            total_tokens = prompt_tokens + completion_tokens
            
            # Calculate costs
            input_cost = (prompt_tokens / 1000) * model["input_price"]
            output_cost = (completion_tokens / 1000) * model["output_price"]
            total_cost = input_cost + output_cost
            
            # Generate realistic latency (higher for larger models)
            base_latency = 500 if "gpt-4" in model["name"] or "opus" in model["name"] else 300
            latency = base_latency + random.randint(0, 1500) + (total_tokens / 20)
            
            # Success rate (occasionally fail)
            success = random.random() > 0.02  # 98% success rate
            
            # Create log entry with random time within the current day
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            timestamp = current_date.replace(hour=hour, minute=minute, second=second)
            
            log = {
                "id": str(uuid.uuid4()),
                "timestamp": timestamp.isoformat(),
                "model": model["name"],
                "endpoint_name": feature["name"],
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "latency_ms": latency,
                "input_cost": round(input_cost, 6),
                "output_cost": round(output_cost, 6),
                "total_cost": round(total_cost, 6),
                "api_provider": model["provider"],
                "success": success
            }
            
            logs.append(log)
        
        # Move to next day
        current_date = current_date + timedelta(days=1)
        current_date = current_date.replace(hour=0, minute=0, second=0)
    
    return logs

def generate_model_alternatives():
    """Generate model alternatives with similarity scores"""
    alternatives = []
    
    # Define alternative mappings with similarity scores
    mappings = [
        {"source": "gpt-4", "alternative": "gpt-4-turbo", "score": 0.95, "note": "Almost identical quality with significantly better price"},
        {"source": "gpt-4", "alternative": "claude-3-sonnet", "score": 0.85, "note": "Excellent alternative for most use cases with significant savings"},
        {"source": "gpt-4", "alternative": "gpt-3.5-turbo", "score": 0.75, "note": "Good for most general tasks with substantial cost savings"},
        {"source": "claude-3-opus", "alternative": "claude-3-sonnet", "score": 0.9, "note": "Very similar quality with much better pricing"},
        {"source": "claude-3-opus", "alternative": "gpt-4-turbo", "score": 0.85, "note": "Great alternative with competitive pricing"},
        {"source": "claude-3-opus", "alternative": "claude-3-haiku", "score": 0.7, "note": "Good for simpler tasks with maximum cost savings"},
        {"source": "claude-3-sonnet", "alternative": "claude-3-haiku", "score": 0.8, "note": "Good quality tradeoff for increased performance and lower cost"},
        {"source": "claude-3-sonnet", "alternative": "gpt-3.5-turbo", "score": 0.8, "note": "Similar performance profile with comparable pricing"},
        {"source": "gpt-3.5-turbo", "alternative": "claude-3-haiku", "score": 0.85, "note": "Often better quality at a similar price point"},
        {"source": "gpt-3.5-turbo", "alternative": "mistral-medium", "score": 0.8, "note": "Solid alternative with competitive pricing"}
    ]
    
    for mapping in mappings:
        source_model = next((m for m in MODELS if m["name"] == mapping["source"]), None)
        alt_model = next((m for m in MODELS if m["name"] == mapping["alternative"]), None)
        
        if source_model and alt_model:
            # Calculate potential savings percentage
            source_cost = (1000 * source_model["input_price"]) + (1000 * source_model["output_price"])
            alt_cost = (1000 * alt_model["input_price"]) + (1000 * alt_model["output_price"])
            savings_percent = round(((source_cost - alt_cost) / source_cost) * 100, 1)
            
            alternative = {
                "id": str(uuid.uuid4()),
                "source_model": mapping["source"],
                "alternative_model": mapping["alternative"],
                "similarity_score": mapping["score"],
                "savings_percent": savings_percent,
                "is_recommended": True,
                "notes": mapping["note"]
            }
            alternatives.append(alternative)
    
    return alternatives

def generate_usage_benchmarks():
    """Generate benchmark data for model quality comparison"""
    benchmarks = []
    
    tasks = [
        "general-chat", "summarization", "extraction", "code-generation", 
        "reasoning", "creative-writing", "translation"
    ]
    
    for model in MODELS:
        for task in tasks:
            # Generate realistic quality scores - higher for more advanced models
            base_score = 0.7
            if "gpt-4" in model["name"] or "opus" in model["name"]:
                base_score = 0.9
            elif "sonnet" in model["name"] or "gpt-4-turbo" in model["name"]:
                base_score = 0.85
            elif "haiku" in model["name"] or "gpt-3.5" in model["name"]:
                base_score = 0.8
            
            # Add some task-specific variation
            variation = random.uniform(-0.1, 0.1)
            quality_score = min(0.99, max(0.5, base_score + variation))
            
            # Calculate realistic tokens per second
            tokens_per_second = random.uniform(5, 30)
            if "gpt-4" in model["name"] or "opus" in model["name"]:
                tokens_per_second = random.uniform(5, 15)
            elif "gpt-3.5" in model["name"] or "haiku" in model["name"]:
                tokens_per_second = random.uniform(15, 30)
            
            benchmark = {
                "model": model["name"],
                "task": task,
                "quality_score": round(quality_score, 2),
                "tokens_per_second": round(tokens_per_second, 1),
                "avg_latency_ms": round(1000 / tokens_per_second * 20),  # Rough estimate for 20 tokens
                "cost_per_1k_tokens": round(model["input_price"] + model["output_price"], 6)
            }
            benchmarks.append(benchmark)
    
    return benchmarks

def main():
    parser = argparse.ArgumentParser(description='Generate dummy data for TokenOptimizer')
    parser.add_argument('--days', type=int, default=30, help='Number of days of historical data')
    parser.add_argument('--entries-per-day', type=int, default=25, help='Average entries per day')
    args = parser.parse_args()
    
    # Create directory for output files
    output_dir = "../dummy_data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate token logs
    token_logs = generate_token_logs(days=args.days, entries_per_day=args.entries_per_day)
    with open(f"{output_dir}/token_logs.json", "w") as f:
        json.dump(token_logs, f, indent=2)
    
    # Generate model pricing
    with open(f"{output_dir}/model_pricing.json", "w") as f:
        json.dump(MODELS, f, indent=2)
    
    # Generate model alternatives
    alternatives = generate_model_alternatives()
    with open(f"{output_dir}/model_alternatives.json", "w") as f:
        json.dump(alternatives, f, indent=2)
    
    # Generate benchmark data
    benchmarks = generate_usage_benchmarks()
    with open(f"{output_dir}/model_benchmarks.json", "w") as f:
        json.dump(benchmarks, f, indent=2)
    
    print(f"Generated {len(token_logs)} token logs")
    print(f"Generated {len(MODELS)} model pricing entries")
    print(f"Generated {len(alternatives)} model alternatives")
    print(f"Generated {len(benchmarks)} benchmark entries")
    print(f"Files saved to {output_dir}/")

if __name__ == "__main__":
    main() 