import { useQuery } from '@tanstack/react-query';
import { SearchFilters, SearchResponse } from '../types';

export const searchAPI = {
  search: async (
    query: string,
    collection: string,
    filters?: SearchFilters,
    page_size: number = 3,
    page: number = 1
  ) => {
    try {
      const params = new URLSearchParams();
      params.append('query', query);
      params.append('page_size', page_size.toString());
      params.append('page', page.toString());

      if (collection) {
        params.append('collection', collection);
      }

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

export const collectionsAPI = {
  getCollections: async (): Promise<{ collections: string[]; count: number }> => {
    try {
      const response = await fetch('http://localhost:8000/collections');
      if (!response.ok) throw new Error('Failed to fetch collections');
      return response.json();
    } catch (error) {
      console.error('Failed to fetch collections:', error);
      throw error;
    }
  },
};

export const useSearch = (
  query: string,
  collection: string,
  filters?: SearchFilters,
  page_size: number = 3,
  page: number = 1
) => {
  return useQuery({
    queryKey: ['search', query, collection, filters, page_size, page],
    queryFn: () => {
      if (!collection) {
        throw new Error('Please select a collection before searching');
      }
      return searchAPI.search(query, collection, filters, page_size, page);
    },
    enabled: !!query && !!collection,
    staleTime: 5 * 60 * 1000,
  });
};

export const useCollections = () => {
  return useQuery({
    queryKey: ['collections'],
    queryFn: collectionsAPI.getCollections,
    staleTime: 5 * 60 * 1000,
  });
};
