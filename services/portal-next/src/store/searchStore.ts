import { create } from 'zustand';

interface SearchState {
  query: string;
  selectedCollection: string;
  results: any[];
  loading: boolean;
  error: string | null;
  setQuery: (query: string) => void;
  setSelectedCollection: (collection: string) => void;
  setResults: (results: any[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useSearchStore = create<SearchState>((set) => ({
  query: '',
  selectedCollection: 'all',
  results: [],
  loading: false,
  error: null,
  setQuery: (query) => set({ query }),
  setSelectedCollection: (selectedCollection) => set({ selectedCollection }),
  setResults: (results) => set({ results }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  reset: () => set({
    query: '',
    results: [],
    loading: false,
    error: null,
  }),
}));