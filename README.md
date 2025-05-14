# 🧠 TokenOptimizer

A developer tool for tracking and optimizing LLM API usage, costs, and performance.

## 🔍 Overview

TokenOptimizer helps developers monitor token usage and optimize model spend in GenAI applications. It works with apps using OpenAI, Anthropic, Mistral, or other API-accessible models.

- 📊 Track token usage, latency, and model selection
- 💰 Calculate estimated costs based on latest pricing
- 📈 View usage in a clean dashboard
- 🔄 Zero-latency integration with your existing code

## 🛠️ Project Structure

- `/backend` - Flask API for logging token usage
- `/frontend` - React dashboard (coming soon)
- `/sdk` - Python SDK for integration with LLM applications

## 🏁 Getting Started

### Setting up the database

1. Create two tables in your Supabase project:
   - `token_logs` - for storing LLM API usage data
   - `model_pricing` - for storing per-model pricing information

   Use the SQL provided in the project documentation to create these tables.

### Setting up the backend

1. Navigate to the `/backend` directory
2. Create a `.env` file with your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project-url.supabase.co
   SUPABASE_KEY=your-supabase-service-key-here
   FLASK_ENV=development
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the API:
   ```bash
   ./run.sh
   ```

### Using the SDK

```python
from tokenoptimizer import tracked_completion

response = tracked_completion(
    model="claude-3-haiku",
    messages=[{"role": "user", "content": "Summarize this PDF"}],
    endpoint_name="summarization",  # Optional task tag
    provider_client=client  # Your OpenAI, Anthropic, etc. client
)
```

## 📊 Dashboard Features

- Total token usage over time (line graph)
- Cost breakdown by model and feature
- Model distribution visualization
- Usage by endpoint/feature
- Latency tracking
- Detailed logs view

## 🚀 Development Roadmap

- ✅ Supabase database setup
- ✅ Flask API for token logging
- 🔜 Python SDK package
- 🔜 React dashboard UI
- 🔜 Authentication and multi-user support
- 🔜 Model recommendation engine

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 