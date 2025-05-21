# TokenOptimizer Dashboard

A comprehensive dashboard for AI developers to visualize, analyze, and optimize their LLM API usage across different models and features.

## Features

- **Cost Visualization**: Track and visualize your token spend across different models and features
- **Optimization Suggestions**: Get recommendations for comparable models that may be cheaper or better suited
- **Performance Metrics**: Monitor latency, success rates, and other key performance indicators
- **Usage Patterns**: Identify peak usage times and opportunities for optimization

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Python 3.9+
- Git

### Development Setup

1. **Clone the repository and create a feature branch**

```bash
git clone https://github.com/yourusername/tokenoptimizer.git
cd tokenoptimizer
git checkout -b feature/dashboard-foundation
```

2. **Install dependencies**

Backend:
```bash
cd backend
pip install -r requirements.txt
pip install langchain langchain-openai
```

Frontend:
```bash
cd frontend
npm install
```

3. **Generate dummy data for development**

```bash
# Create scripts directory if it doesn't exist
mkdir -p scripts

# Make the script executable
chmod +x scripts/generate_dummy_data.py

# Generate 30 days of dummy data
python scripts/generate_dummy_data.py --days 30 --entries-per-day 25
```

4. **Start the development servers**

Backend:
```bash
cd backend
python app.py
```

Frontend:
```bash
cd frontend
npm run dev
```

5. **Access the dashboard**

Open your browser and navigate to:
```
http://localhost:5173
```

## Project Structure

- `backend/` - Flask API and data services
  - `services/dashboard_service.py` - Unified dashboard data processing
  - `routes/analytics_routes.py` - API endpoints for dashboard data
  - `db/` - Database clients and schema

- `frontend/` - React-based dashboard UI
  - `src/components/dashboard/` - Dashboard components
  - `src/hooks/useDashboard.js` - Data fetching hook
  - `src/pages/Dashboard.tsx` - Main dashboard page

- `scripts/` - Utility scripts
  - `generate_dummy_data.py` - Creates test data for development

- `dummy_data/` - Generated test data
  - `token_logs.json` - Simulated token usage data
  - `model_pricing.json` - Model pricing information
  - `model_alternatives.json` - Alternative model recommendations
  - `model_benchmarks.json` - Performance benchmarks

## Development Process

1. Review the `REQUIREMENTS.md` document for a complete list of requirements
2. Follow the `DEVELOPMENT_PLAN.md` for the implementation timeline
3. Check off completed items in the requirements document as you go
4. Run the test data generator to create realistic data for development
5. Submit PRs against the `develop` branch for review

## Key Implementation Details

### Backend

- Create a unified `DashboardService` that handles all data processing in one place
- Implement a `/api/dashboard` endpoint that returns all dashboard data in a single call
- Use LangChain for intelligent model recommendations
- Implement proper caching to improve performance

### Frontend

- Use a central data fetching hook (`useDashboard`) to manage state
- Create reusable visualization components
- Implement consistent filtering for all dashboard components
- Focus on performance and responsiveness

## Resources

- [Design Mockups](link-to-mockups)
- [API Documentation](link-to-api-docs)
- [REQUIREMENTS.md](./REQUIREMENTS.md) - Detailed requirements document
- [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md) - Implementation timeline

## Contributing

1. Create a feature branch from `develop`
2. Implement your changes
3. Submit a pull request
4. Ensure all tests pass
5. Update documentation

## License

MIT 