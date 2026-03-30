// Search-related types
export interface SearchFilters {
  title?: string;
  domain?: string;
  start_time?: string;
  end_time?: string;
}

export interface SearchParams {
  query: string;
  collection?: string;
  filters?: SearchFilters;
  limit?: number;
}

export interface SearchResultItem {
  score: number;
  title: string;
  url: string;
  domain: string;
  content: string;
  updated_at: string;
}

export interface SearchResponse {
  query: string;
  page_size: number;
  page: number;
  offset: number;
  collection: string;
  filters: SearchFilters | null;
  latency_ms: number;
  results: SearchResultItem[];
}
