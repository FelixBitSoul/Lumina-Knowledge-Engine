import { useQuery } from '@tanstack/react-query';
import { SearchFilters, SearchResponse } from '../types';

export const searchAPI = {
  search: async (
    query: string,
    collection: string = 'core-docs',
    filters?: SearchFilters,
    limit: number = 3
  ) => {
    try {
      // Build search URL with parameters
      const params = new URLSearchParams();
      params.append('query', query);
      params.append('limit', limit.toString());
      params.append('collection', collection);

      // Add filter parameters
      if (filters) {
        if (filters.title) {
          params.append('title', filters.title);
        }
        if (filters.domain) {
          params.append('domain', filters.domain);
        }
        if (filters.start_time) {
          params.append('start_time', filters.start_time);
        }
        if (filters.end_time) {
          params.append('end_time', filters.end_time);
        }
      }

      // Connect to the Python FastAPI search endpoint
      const response = await fetch(`http://localhost:8000/search?${params.toString()}`);

      if (!response.ok) throw new Error('Backend service unavailable');

      const data: SearchResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Search failed:', error);
      throw new Error('Failed to connect to the Brain API. Ensure the Python service is running.');
    }
  },
};

export const useSearch = (
  query: string,
  collection: string = 'all',
  filters?: SearchFilters,
  limit: number = 3
) => {
  return useQuery({
    queryKey: ['search', query, collection, filters, limit],
    queryFn: () => searchAPI.search(query, collection, filters, limit),
    enabled: !!query,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
