import { useQuery } from '@tanstack/react-query';
import config from '../config';
import { FilterParams, MetricsSummary, LogsResponse, TrendResponse } from '../types/api';

// API client functions
export const fetchJson = async <T>(endpoint: string, params?: FilterParams): Promise<T> => {
  const searchParams = new URLSearchParams();
  if (params) {
    // Handle array parameters (models, endpoints)
    if (params.models?.length) {
      params.models.forEach(model => searchParams.append('model', model));
    }
    if (params.endpoints?.length) {
      params.endpoints.forEach(endpoint => searchParams.append('endpoint', endpoint));
    }
    if (params.providers?.length) {
      params.providers.forEach(provider => searchParams.append('provider', provider));
    }
    // Handle date range parameters
    if (params.start_date) {
      searchParams.append('start_date', params.start_date);
    }
    if (params.end_date) {
      searchParams.append('end_date', params.end_date);
    }
    // Handle pagination parameters
    if (params.page) {
      searchParams.append('page', params.page.toString());
    }
    if (params.per_page) {
      searchParams.append('per_page', params.per_page.toString());
    }
  }

  const url = `${config.apiUrl}${endpoint}${searchParams.toString() ? `?${searchParams}` : ''}`;
  console.log('Fetching:', url);
  
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }
  
  const data = await response.json();
  console.log('Response:', data);
  return data;
};

// Query hooks
export const useMetricsSummary = (filters?: FilterParams) => {
  return useQuery<MetricsSummary>({
    queryKey: ['metrics', 'summary', filters],
    queryFn: () => fetchJson('/api/metrics/summary', filters),
  });
};

export const useMetricsTrend = (filters?: FilterParams) => {
  return useQuery<TrendResponse>({
    queryKey: ['metrics', 'trend', filters],
    queryFn: () => fetchJson('/api/metrics/trend', filters),
  });
};

export const useLogs = (params: FilterParams & { page?: number; per_page?: number }) => {
  return useQuery<LogsResponse>({
    queryKey: ['logs', params],
    queryFn: () => fetchJson('/api/logs', params),
    staleTime: 30000, // Consider data fresh for 30 seconds
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
    retry: 1 // Only retry failed requests once
  });
}; 