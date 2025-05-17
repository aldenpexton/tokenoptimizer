import axios from 'axios';

// API base URL - use environment variable if available or fallback to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL ? 
  `${import.meta.env.VITE_API_URL}/api` : 
  'http://localhost:5001/api';

// Define types for API responses
export interface SummaryData {
  total_tokens: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_cost: number;
  avg_latency_ms: number;
  top_model: {
    name: string;
    usage_percent: number;
  };
  time_period: {
    start_date: string;
    end_date: string;
    days: number;
  };
}

export interface TimeSeriesPoint {
  display_key: string;
  display_date: string;
  value: number;
  prompt_tokens: number;
  completion_tokens: number;
  cost: number;
  alternative_cost: number;
  savings: number;
}

export interface TimeSeriesData {
  data: TimeSeriesPoint[];
  time_period?: {
    start_date: string;
    end_date: string;
    interval: string;
  };
}

export interface ModelData {
  model: string;
  value: number;
  percent: number;
  cost: number;
}

export interface ModelDistributionData {
  data: ModelData[];
  other: {
    value: number;
    percent: number;
    cost: number;
  };
  time_period: {
    start_date: string;
    end_date: string;
  };
}

export interface FeatureData {
  feature: string;
  total_tokens: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_cost: number;
  request_count: number;
  avg_latency_ms: number;
  percent: number;
}

export interface FeatureUsageData {
  data: FeatureData[];
  time_period: {
    start_date: string;
    end_date: string;
  };
}

export interface LogEntry {
  id: string;
  timestamp: string;
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  total_cost: number;
  feature: string;
  latency_ms: number;
}

export interface LogsData {
  data: LogEntry[];
  pagination: {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
  };
  filters: {
    start_date: string;
    end_date: string;
    model: string | null;
    feature: string | null;
  };
}

// API functions
export const fetchSummary = async (
  startDate?: string, 
  endDate?: string,
  model?: string,
  task?: string,
  interval?: 'day' | 'week' | 'month'
): Promise<SummaryData> => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  
  // Always send model/task parameters - backend handles '*' as "all"
  params.append('model', model || '*');
  params.append('task', task || '*');
  
  if (interval) params.append('interval', interval);
  
  console.log('Fetching summary with params:', Object.fromEntries(params.entries()));
  
  const response = await axios.get(`${API_BASE_URL}/analytics/summary`, { params });
  return response.data;
};

export const fetchTimeSeries = async (
  startDate?: string, 
  endDate?: string,
  interval: 'day' | 'week' | 'month' = 'day',
  metric: 'tokens' | 'cost' = 'tokens',
  model?: string,
  task?: string
): Promise<TimeSeriesData> => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  params.append('interval', interval);
  params.append('metric', metric);
  
  // Always send model parameter - backend will handle '*' as all models
  params.append('model', model || '*');
  
  // Always send task parameter - backend will handle '*' as all tasks
  params.append('task', task || '*');
  
  console.log('Fetching time series with params:', Object.fromEntries(params.entries()));
  
  const response = await axios.get(`${API_BASE_URL}/analytics/timeseries`, { params });
  
  // Log the response shape for debugging
  console.log(`Time series response: ${response.data.data?.length || 0} data points`);
  
  return response.data;
};

export const fetchModelDistribution = async (
  startDate?: string, 
  endDate?: string,
  metric: 'tokens' | 'cost' = 'tokens',
  limit: number = 10,
  model?: string,
  task?: string,
  interval?: 'day' | 'week' | 'month'
): Promise<ModelDistributionData> => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  params.append('metric', metric);
  params.append('limit', limit.toString());
  
  // Always send model/task parameters - backend handles '*' as "all"
  params.append('model', model || '*');
  params.append('task', task || '*');
  
  if (interval) params.append('interval', interval);
  
  const response = await axios.get(`${API_BASE_URL}/analytics/models`, { params });
  return response.data;
};

export const fetchFeatureUsage = async (
  startDate?: string, 
  endDate?: string,
  metric: 'tokens' | 'cost' = 'tokens',
  limit: number = 10,
  model?: string,
  task?: string,
  interval?: 'day' | 'week' | 'month'
): Promise<FeatureUsageData> => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  params.append('metric', metric);
  params.append('limit', limit.toString());
  
  // Always send model/task parameters - backend handles '*' as "all"
  params.append('model', model || '*');
  params.append('task', task || '*');
  
  if (interval) params.append('interval', interval);
  
  const response = await axios.get(`${API_BASE_URL}/analytics/features`, { params });
  return response.data;
};

export const fetchLogs = async (
  startDate?: string, 
  endDate?: string,
  model?: string,
  feature?: string,
  page: number = 1,
  pageSize: number = 20,
  sortBy: string = 'created_at',
  sortDir: 'asc' | 'desc' = 'desc'
): Promise<LogsData> => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  if (model) params.append('model', model);
  if (feature) params.append('feature', feature);
  params.append('page', page.toString());
  params.append('page_size', pageSize.toString());
  params.append('sort_by', sortBy);
  params.append('sort_dir', sortDir);
  
  const response = await axios.get(`${API_BASE_URL}/analytics/logs`, { params });
  return response.data;
}; 