# TokenOptimizer

Token usage tracking and analytics for Large Language Models.

## Overview

TokenOptimizer provides a complete solution to track, analyze, and optimize your LLM API usage:

- **SDK**: Simple integration to track token usage from any application
- **Dashboard**: Visualize token usage, costs, and model distribution
- **Analytics**: Gain insights into usage patterns and optimize your prompts

## Project Structure

This repository contains two main components:

- `/backend`: Python Flask API for data processing and analytics
- `/frontend`: React dashboard with Tailwind CSS for visualization
- `/sdk`: Python package for tracking token usage in applications

## Getting Started

### Local Development

1. Clone this repository
2. Set up the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```
3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Using the SDK

```python
from tokenoptimizer import TokenOptimizer

# Initialize with your API key
tracker = TokenOptimizer(api_key="your-api-key")

# Track LLM API usage
tracker.log(
    model="gpt-4",
    prompt_tokens=250,
    completion_tokens=100,
    latency_ms=450,
    endpoint="document-chat"
)
```

## Current Status

This project is under active development. Key features:

- [x] Token tracking SDK
- [x] Analytics backend
- [x] Dashboard visualization
- [ ] User authentication
- [ ] API key management
- [ ] Advanced analytics

## License

[MIT License](LICENSE) 