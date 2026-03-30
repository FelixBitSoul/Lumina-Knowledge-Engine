import { create } from 'zustand';
import { SearchFilters } from '../types';

interface SearchState {
  query: string;
  selectedCollection: string;
  filters: SearchFilters;
  results: any[];
  loading: boolean;
  error: string | null;
  currentPage: number;
  pageSize: number;
  setQuery: (query: string) => void;
  setSelectedCollection: (collection: string) => void;
  setFilters: (filters: SearchFilters) => void;
  updateFilter: (key: keyof SearchFilters, value: string | undefined) => void;
  setResults: (results: any[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  reset: () => void;
  resetFilters: () => void;
}

export const useSearchStore = create<SearchState>((set) => ({
  query: '',
  selectedCollection: '',
  filters: {
    title: undefined,
    domain: undefined,
    start_time: undefined,
    end_time: undefined,
  },
  results: [],
  loading: false,
  error: null,
  currentPage: 1,
  pageSize: 3,
  setQuery: (query) => set({ query }),
  setSelectedCollection: (selectedCollection) => set({ selectedCollection }),
  setFilters: (filters) => set({ filters }),
  updateFilter: (key, value) => set((state) => ({
    filters: {
      ...state.filters,
      [key]: value,
    },
  })),
  setResults: (results) => set({ results }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setPage: (page) => set({ currentPage: page }),
  setPageSize: (size) => set({ pageSize: size }),
  reset: () => set({
    query: '',
    results: [],
    loading: false,
    error: null,
    currentPage: 1,
    pageSize: 3,
    filters: {
      title: undefined,
      domain: undefined,
      start_time: undefined,
      end_time: undefined,
    },
  }),
  resetFilters: () => set({
    filters: {
      title: undefined,
      domain: undefined,
      start_time: undefined,
      end_time: undefined,
    },
  }),
}));
