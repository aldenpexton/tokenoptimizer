# Token Optimizer API Documentation

## Base URL
All API endpoints are prefixed with `/api`

## Authentication
All requests must include a valid API key in the Authorization header:
```
Authorization: Bearer <api_key>
```

## Common Query Parameters

The following parameters are available for most metric endpoints:

- `granularity` (string): Time grouping granularity. One of:
  - `hour` - Group by hour
  - `day` - Group by day (default)
  - `week` - Group by week
  - `month` - Group by month
  - `year` - Group by year
- `start_date` (ISO date string): Start of date range (defaults based on granularity)
- `end_date` (ISO date string): End of date range (defaults to current time)
- `model` (array): Filter by specific models
- `endpoint` (array): Filter by specific endpoints
- `provider` (array): Filter by specific providers

## Endpoints

### Health Check
```
GET /api/health
```
Returns server status information.

#### Response
```json
{
    "status": "healthy",
    "timestamp": "2024-03-21T15:30:00Z",
    "version": "1.0.0"
}
```

### Filters
```
GET /api/filters
```
Returns available filter options for the dashboard.

#### Response
```json
{
    "models": ["gpt-4", "claude-3", ...],
    "endpoints": ["chat-assistant", "text-to-sql", ...],
    "providers": ["OpenAI", "Anthropic", "Mistral", "Meta"],
    "granularities": ["hour", "day", "week", "month", "year"],
    "example_usage": {
        "filter_by_model": "?model=gpt-4&model=gpt-3.5-turbo",
        "filter_by_endpoint": "?endpoint=chat&endpoint=completions",
        "filter_by_provider": "?provider=OpenAI&provider=Anthropic",
        "filter_by_granularity": "?granularity=month",
        "filter_by_date": "?end_date=2024-03-20T00:00:00Z",
        "combine_filters": "?granularity=month&model=gpt-4&endpoint=chat&provider=OpenAI"
    }
}
```

### Metrics Summary
```
GET /api/metrics/summary
```
Returns aggregated usage metrics.

#### Query Parameters
All common query parameters apply.

#### Response
```json
{
    "total_spend": 150.25,
    "total_requests": 1000,
    "avg_cost_per_request": 0.15,
    "provider_breakdown": {
        "OpenAI": {
            "total_spend": 100.25,
            "total_requests": 700,
            "total_tokens": 400000
        },
        "Anthropic": {
            "total_spend": 50.00,
            "total_requests": 300,
            "total_tokens": 200000
        }
    },
    "filters": {
        "granularity": "day",
        "start_date": "2024-03-20T00:00:00Z",
        "end_date": "2024-03-21T00:00:00Z",
        "models": ["gpt-4"],
        "endpoints": ["chat"],
        "providers": ["OpenAI"]
    }
}
```

### Model-Specific Metrics
```
GET /api/metrics/by-model
```
Returns metrics grouped by model.

#### Query Parameters
All common query parameters apply.

#### Response
```json
{
    "models": [
        {
            "name": "gpt-4",
            "total_tokens": 500000,
            "total_cost": 75.50,
            "average_latency": 2.1
        },
        // ... other models
    ],
    "filters": {
        "granularity": "day",
        "start_date": "2024-03-20T00:00:00Z",
        "end_date": "2024-03-21T00:00:00Z",
        "models": ["gpt-4"],
        "endpoints": ["chat"],
        "providers": ["OpenAI"]
    }
}
```

### Endpoint-Specific Metrics
```
GET /api/metrics/by-endpoint
```
Returns metrics grouped by endpoint.

#### Query Parameters
All common query parameters apply.

#### Response
```json
{
    "endpoints": [
        {
            "name": "chat-assistant",
            "total_tokens": 300000,
            "total_cost": 45.75,
            "average_latency": 2.3
        },
        // ... other endpoints
    ],
    "filters": {
        "granularity": "day",
        "start_date": "2024-03-20T00:00:00Z",
        "end_date": "2024-03-21T00:00:00Z",
        "models": ["gpt-4"],
        "endpoints": ["chat"],
        "providers": ["OpenAI"]
    }
}
```

### Usage Trends
```
GET /api/metrics/trend
```
Returns time-series data for usage trends.

#### Query Parameters
All common query parameters apply.

#### Response
```json
{
    "trends": [
        {
            "timestamp": "2024-03-01T00:00:00Z",
            "total_tokens": 50000,
            "total_cost": 7.50,
            "request_count": 100
        },
        // ... other time periods
    ],
    "filters": {
        "granularity": "day",
        "start_date": "2024-03-20T00:00:00Z",
        "end_date": "2024-03-21T00:00:00Z",
        "models": ["gpt-4"],
        "endpoints": ["chat"],
        "providers": ["OpenAI"]
    }
}
```

### Recommendations
```
GET /api/recommendations
```
Returns cost optimization suggestions.

#### Query Parameters
All common query parameters apply.

#### Response
```json
{
    "recommendations": [
        {
            "model": "gpt-4",
            "alternative": "claude-3",
            "potential_savings": 25.50,
            "confidence": 0.85,
            "reasoning": "Similar performance metrics with lower cost"
        },
        // ... other recommendations
    ],
    "filters": {
        "granularity": "day",
        "start_date": "2024-03-20T00:00:00Z",
        "end_date": "2024-03-21T00:00:00Z",
        "models": ["gpt-4"],
        "endpoints": ["chat"],
        "providers": ["OpenAI"]
    }
}
```

### Token Logs
```
GET /api/logs
```
Returns detailed token usage logs.

#### Query Parameters
All common query parameters apply, plus:
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 50, max: 100)
- `format` (string): Response format, one of:
  - `json` (default) - Returns JSON response
  - `csv` - Returns CSV file download
- `sort_by` (string): Field to sort by (default: "timestamp")
- `sort_desc` (boolean): Sort in descending order (default: true)

#### Response (JSON)
```json
{
    "logs": [
        {
            "timestamp": "2024-03-01T12:34:56Z",
            "model": "gpt-4",
            "endpoint": "chat-assistant",
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
            "input_cost": 0.10,
            "output_cost": 0.05,
            "total_cost": 0.15,
            "latency_ms": 2100,
            "api_provider": "OpenAI"
        },
        // ... other logs
    ],
    "pagination": {
        "current_page": 1,
        "total_pages": 10,
        "total_items": 500,
        "per_page": 50
    },
    "filters": {
        "granularity": "day",
        "start_date": "2024-03-20T00:00:00Z",
        "end_date": "2024-03-21T00:00:00Z",
        "models": ["gpt-4"],
        "endpoints": ["chat"],
        "providers": ["OpenAI"]
    }
}
```

#### Response (CSV)
When `format=csv` is specified, the endpoint returns a CSV file with the following:

- Content-Type: text/csv
- Content-Disposition: attachment; filename="token_logs_YYYY-MM-DD.csv"
- CSV Headers: timestamp, model, endpoint, prompt_tokens, completion_tokens, total_tokens, input_cost, output_cost, total_cost, latency_ms, api_provider
- One row per log entry
- Dates in ISO format
- Numbers in decimal format with up to 6 decimal places for costs
- All text fields are quoted if they contain commas

Example CSV content:
```csv
timestamp,model,endpoint,prompt_tokens,completion_tokens,total_tokens,input_cost,output_cost,total_cost,latency_ms,api_provider
"2024-03-01T12:34:56Z","gpt-4","chat-assistant",100,50,150,0.100000,0.050000,0.150000,2100,"OpenAI"
```

## Error Responses
All endpoints return standard error responses:

```json
{
    "error": {
        "code": "INVALID_DATE_RANGE",
        "message": "Start date must be before end date",
        "details": {
            "start_date": "2024-04-01",
            "end_date": "2024-03-01"
        }
    }
}
```

Common error codes:
- `INVALID_PARAMETERS`: Invalid request parameters
- `INVALID_DATE_RANGE`: Invalid date range specified
- `INVALID_GRANULARITY`: Invalid time granularity
- `INVALID_SORT`: Invalid sort parameters
- `INVALID_PAGE`: Invalid pagination parameters
- `UNAUTHORIZED`: Invalid or missing API key
- `NOT_FOUND`: Requested resource not found
- `INTERNAL_ERROR`: Server error 