# TokenOptimizer Backend

This is the Flask API backend for TokenOptimizer, responsible for logging and analyzing LLM API usage.

## Setup

1. Create a `.env` file in the `/backend` directory with the following contents:
```
# Supabase connection
SUPABASE_URL=https://your-project-url.supabase.co
SUPABASE_KEY=your-supabase-service-key-here

# Flask settings
FLASK_ENV=development
FLASK_APP=app.py
HOST=0.0.0.0
PORT=5000
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API:
```bash
python app.py
```

## API Endpoints

### POST /api/log

Logs token usage from LLM API calls.

**Request body:**
```json
{
  "model": "gpt-4",
  "prompt_tokens": 150,
  "completion_tokens": 50,
  "total_tokens": 200,
  "latency_ms": 1200,
  "endpoint_name": "summarization",
  "timestamp": "2023-05-01T12:34:56Z"
}
```

**Response:**
```json
{
  "message": "Token usage logged successfully",
  "log": {
    "id": "uuid",
    "model": "gpt-4",
    "prompt_tokens": 150,
    "completion_tokens": 50,
    "total_tokens": 200,
    "latency_ms": 1200,
    "endpoint_name": "summarization",
    "timestamp": "2023-05-01T12:34:56Z",
    "input_cost": 0.0045,
    "output_cost": 0.003,
    "total_cost": 0.0075,
    "api_provider": "OpenAI"
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## Project Structure

- `app.py`: Main application entry point
- `config/`: Configuration and environment variables
- `routes/`: API route definitions
- `services/`: Business logic (pricing calculations, etc.)
- `db/`: Database operations
- `utils/`: Helper functions and utilities 