# TokenOptimizer Dashboard (Simplified MVP)

## Project Goal
Build a single-page dashboard clearly visualizing API token usage, highlighting cost breakdowns and optimization opportunities. The project should maintain simplicity and clarity, allowing for easy understanding and minimal complexity.

## Database Tables & Schemas

### 1. `token_logs`
- **id** (UUID, PK)
- **timestamp** (timestamp with time zone)
- **model** (text)
- **endpoint_name** (text)
- **prompt_tokens** (integer)
- **completion_tokens** (integer)
- **total_tokens** (integer)
- **latency_ms** (integer)
- **input_cost** (numeric)
- **output_cost** (numeric)
- **total_cost** (numeric)
- **api_provider** (text)
- **created_at** (timestamp)
- **updated_at** (timestamp)

### 2. `model_pricing`
- **model** (text, PK)
- **input_price** (numeric)
- **output_price** (numeric)
- **api_provider** (text)
- **is_active** (boolean)
- **last_updated** (timestamp)
- **created_at** (timestamp)

### 3. `model_alternatives`
- **id** (UUID, PK)
- **source_model** (text, FK to `model_pricing.model`)
- **alternative_model** (text, FK to `model_pricing.model`)
- **similarity_score** (numeric)
- **is_recommended** (boolean)
- **created_at** (timestamp)
- **updated_at** (timestamp)

## Dashboard Components

### Summary Metrics (Cards)
- Total Spend (current period vs previous period)
- Average Cost per Request

### Visualizations (using Recharts)
- **Spend by Model**: Bar Chart
- **Spend by Endpoint**: Bar Chart
- **Spend Trend**: Line Chart

### Optimization Recommendations
- Clearly display recommended alternative models from `model_alternatives` (only where `is_recommended=true`)
- Show similarity scores
- Highlight cost savings potential based on current pricing (`model_pricing`)

### Logs View
- Detailed table view of all token usage logs
- Columns:
  - Timestamp
  - Model
  - Endpoint
  - Prompt Tokens
  - Completion Tokens
  - Total Tokens
  - Input Cost
  - Output Cost
  - Total Cost
  - Latency
  - API Provider
  - Alternative Models (with similarity scores and potential savings)
- Features:
  - Sortable columns
  - Pagination (50 records per page)
  - Uses same global filters as dashboard
  - Export to CSV option
  - Clickable model names to show full alternative model details

## Filters & Interactivity

### Global Filters
1. **Time Period Selection**
   - Year View: Data grouped by months
   - Month View: Data grouped by weeks
   - Week View: Data grouped by days
   - Day View: Data grouped by hours
   - Default to last 30 days

2. **Model Filter**
   - Multi-select filter for models
   - Shows all available models from token_logs
   - Affects all visualizations and metrics

3. **Endpoint Filter**
   - Multi-select filter for endpoints
   - Shows all available endpoints from token_logs
   - Affects all visualizations and metrics

### Filter Behavior
- All filters are applied globally to all dashboard components
- Time period selection determines data granularity
- Filters can be combined (e.g., specific models for a particular month)
- Clear visual indication of active filters
- Reset option to return to default view

## Technical Guidelines

### Frontend
- Use React with TypeScript
- Clearly separate concerns: components, hooks, utilities
- Keep individual files below ~200 lines
- Refactor clearly and incrementally; maintain readability
- Ensure thorough commenting for each component, function, and data retrieval
- Avoid complex nested logic; prefer simple, flat component structure

### Backend & Data Retrieval
- Utilize Supabase client for straightforward queries and aggregations
- Create single endpoint aggregations (avoid unnecessary complexity)
- Implement simple caching for quick responsiveness and maintainability
- Clearly comment each backend function to describe its purpose and expected output
- Support time-based grouping (hour, day, week, month, year)
- Efficient handling of multi-select filters

### General Rules for Cursor Agent
- Avoid unnecessary abstraction and complexity
- Incrementally test each step and validate data correctness frequently
- Avoid large refactorings; prefer smaller, manageable, and understandable code adjustments
- Always clearly document why specific decisions or implementations are chosen

## Success Criteria
- Dashboard reliably loads quickly (<2 seconds)
- Accurate representation of data at all times
- Filters update visuals clearly without error
- Recommendations provide clear, actionable insights
- Time-based grouping works correctly at all levels

