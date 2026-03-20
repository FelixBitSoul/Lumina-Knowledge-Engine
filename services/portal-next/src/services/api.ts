import { useQuery } from '@tanstack/react-query';

export const searchAPI = {
  search: async (query: string, collection: string = 'all') => {
    try {
      // Build search URL with collection parameter
      let searchUrl = `http://localhost:8000/search?query=${encodeURIComponent(query)}`;
      if (collection !== 'all') {
        searchUrl += `&collection=${encodeURIComponent(collection)}`;
      }

      // Connect to the Python FastAPI search endpoint
      const response = await fetch(searchUrl);

      if (!response.ok) throw new Error('Backend service unavailable');

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Search failed:', error);
      throw new Error('Failed to connect to the Brain API. Ensure the Python service is running.');
    }
  },
};

export const useSearch = (query: string, collection: string = 'all') => {
  return useQuery({
    queryKey: ['search', query, collection],
    queryFn: () => searchAPI.search(query, collection),
    enabled: !!query,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};