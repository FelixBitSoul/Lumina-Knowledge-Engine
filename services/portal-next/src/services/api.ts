import { useQuery } from '@tanstack/react-query';
import { SearchFilters, SearchResponse, CollectionDetails, ChunkDetails } from '../types';

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
        if (filters.category) {
          params.append('category', filters.category);
        }
        if (filters.file_name) {
          params.append('file_name', filters.file_name);
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
  getCollectionDetails: async (collection: string): Promise<CollectionDetails> => {
    try {
      const response = await fetch(`http://localhost:8000/collections/${collection}`);
      if (!response.ok) throw new Error('Failed to fetch collection details');
      return response.json();
    } catch (error) {
      console.error('Failed to fetch collection details:', error);
      throw error;
    }
  },
  createCollection: async (name: string, description: string): Promise<{ collection: string }> => {
    try {
      const response = await fetch('http://localhost:8000/collections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, description }),
      });
      if (!response.ok) throw new Error('Failed to create collection');
      return response.json();
    } catch (error) {
      console.error('Failed to create collection:', error);
      throw error;
    }
  },
};

export const chunksAPI = {
  getChunkDetails: async (chunkId: string, collection: string): Promise<ChunkDetails> => {
    try {
      const params = new URLSearchParams();
      params.append('collection', collection);
      const response = await fetch(`http://localhost:8000/documents/chunks/${chunkId}?${params.toString()}`);
      if (!response.ok) throw new Error('Failed to fetch chunk details');
      return response.json();
    } catch (error) {
      console.error('Failed to fetch chunk details:', error);
      throw error;
    }
  },
};

export const filesAPI = {
  getFiles: async (collection: string, limit: number = 20, start_after: string | null = null): Promise<{ files: any[], next_marker: string | null }> => {
    try {
      const params = new URLSearchParams();
      params.append('collection', collection);
      params.append('limit', limit.toString());
      if (start_after) {
        params.append('start_after', start_after);
      }
      const response = await fetch(`http://localhost:8000/documents?${params.toString()}`);
      if (!response.ok) throw new Error('Failed to fetch files');
      const data = await response.json();
      return {
        files: data.files,
        next_marker: data.next_marker
      };
    } catch (error) {
      console.error('Failed to fetch files:', error);
      throw error;
    }
  },
  deleteFile: async (fileId: string, collection: string, filename: string): Promise<{ success: boolean }> => {
    try {
      const params = new URLSearchParams();
      params.append('collection', collection);
      params.append('filename', filename);
      const response = await fetch(`http://localhost:8000/documents/${fileId}?${params.toString()}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete file');
      return response.json();
    } catch (error) {
      console.error('Failed to delete file:', error);
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

export const useCollectionDetails = (collection: string) => {
  return useQuery({
    queryKey: ['collectionDetails', collection],
    queryFn: () => collectionsAPI.getCollectionDetails(collection),
    enabled: !!collection,
    staleTime: 5 * 60 * 1000,
  });
};

export const useChunkDetails = (chunkId: string, collection: string) => {
  return useQuery({
    queryKey: ['chunkDetails', chunkId, collection],
    queryFn: () => chunksAPI.getChunkDetails(chunkId, collection),
    enabled: !!chunkId && !!collection,
    staleTime: 5 * 60 * 1000,
  });
};

export const useFiles = (collection: string, limit: number = 20, start_after: string | null = null) => {
  return useQuery({
    queryKey: ['files', collection, limit, start_after],
    queryFn: () => filesAPI.getFiles(collection, limit, start_after),
    enabled: !!collection,
    staleTime: 5 * 60 * 1000,
  });
};
