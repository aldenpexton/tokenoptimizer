```
┌─────────────────────────────┐                                           
│                             │                                           
│  Developer's Application    │                                           
│  ┌─────────────────────┐    │                                           
│  │                     │    │                                           
│  │  LLM API Call       │────┼──►  OpenAI, Anthropic, etc.              
│  │                     │    │                                           
│  └──────────┬──────────┘    │                                           
│             │               │                                           
│             ▼               │                                           
│  ┌─────────────────────┐    │                                           
│  │                     │    │                                           
│  │  track_usage()      │    │                                           
│  │                     │    │                                           
│  └──────────┬──────────┘    │                                           
│             │               │                                           
└─────────────┼───────────────┘                                           
              │                                                           
              ▼                                                           
┌─────────────────────────────┐                                           
│                             │                                           
│  TokenOptimizer Backend     │                                           
│  ┌─────────────────────┐    │                                           
│  │                     │    │                                           
│  │ /api/log endpoint   │    │                                           
│  │                     │    │                                           
│  └──────────┬──────────┘    │                                           
│             │               │                                           
│             ▼               │                                           
│  ┌─────────────────────┐    │                                           
│  │                     │    │                                           
│  │ Supabase Database   │    │                                           
│  │                     │    │                                           
│  └─────────────────────┘    │                                           
│                             │                                           
└─────────────────────────────┘                                           
              │                                                           
              ▼                                                           
┌─────────────────────────────┐                                           
│                             │                                           
│  TokenOptimizer Dashboard   │                                           
│  ┌─────────────────────┐    │                                           
│  │                     │    │                                           
│  │ Usage Analytics     │    │                                           
│  │                     │    │                                           
│  └─────────────────────┘    │                                           
│                             │                                           
└─────────────────────────────┘                                           
```

# TokenOptimizer: High-Level Flow

## Simple End-to-End Process

1. **Developer's Application**
   - Makes normal LLM API calls to providers (OpenAI, Anthropic, etc.)
   - After receiving a response, calls `track_usage()` to log token data
   - Continues normal application flow without disruption

2. **TokenOptimizer Backend**
   - Receives token usage data via `/api/log` endpoint
   - Calculates costs based on current model pricing
   - Stores data in Supabase database for analysis

3. **TokenOptimizer Dashboard**
   - Visualizes token usage and costs
   - Provides insights for optimization
   - Helps track and manage LLM API expenses

This non-intrusive approach allows developers to add token tracking to their applications with minimal changes to existing code, while still gaining valuable usage insights. 