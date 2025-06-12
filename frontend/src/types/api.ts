// Common types
export interface FilterParams {
  models?: string[];
  endpoints?: string[];
  providers?: string[];
  start_date?: string;
  end_date?: string;
  page?: number;
  per_page?: number;
}

export interface MetricsSummary {
  total_spend: number;
  total_requests: number;
  avg_cost_per_request: number;
  provider_breakdown: {
    [provider: string]: {
      total_spend: number;
      total_requests: number;
      total_tokens: number;
    };
  };
  model_breakdown: {
    [model: string]: {
      total_spend: number;
      total_requests: number;
      total_tokens: number;
    };
  };
  endpoint_breakdown: {
    [endpoint: string]: {
      total_spend: number;
      total_requests: number;
      total_tokens: number;
    };
  };
  period: string;
}

export interface TrendMetric {
  period: string;
  period_label: string;
  total_spend: number;
  total_requests: number;
  total_tokens: number;
  models_used: string[];
  endpoints_used: string[];
  providers_used: string[];
}

export interface TrendResponse {
  metrics: TrendMetric[];
  period: string;
}

export interface LogsResponse {
  logs: Array<{
    id: string;
    timestamp: string;
    model: string;
    endpoint_name: string;
    total_tokens: number;
    total_cost: number;
    api_provider: string;
  }>;
  pagination: {
    page: number;
    per_page: number;
    total_pages: number;
    total_records: number;
  };
}

export interface Recommendation {
  current_model: string;
  recommended_model: string;
  similarity_score: number;
  potential_savings: number;
  usage_count: number;
  reason?: string;
}

export interface RecommendationsResponse {
  recommendations: Recommendation[];
  total_potential_savings: number;
  filters: {
    granularity: string;
    start_date: string;
    end_date: string;
    models: string[];
    endpoints: string[];
  };
} 