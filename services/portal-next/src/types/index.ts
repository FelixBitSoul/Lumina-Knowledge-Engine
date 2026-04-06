// Search-related types
export interface SearchFilters {
  title?: string;
  domain?: string;
  category?: string;
  file_name?: string;
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

// Upload-related types
export interface UploadResponse {
  task_id: string;
  file_id: string;
  file_name: string;
  category: string;
  collection: string;
  status: string;
  websocket_url: string;
  message: string;
}

export interface TaskStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  total?: number;
  current_step?: string;
  result?: {
    file_id: string;
    filename: string;
    chunks_created: number;
    status: string;
  };
  error?: string;
  message?: string;
}

export interface WebSocketMessage {
  file_id: string;
  status: 'connected' | 'processing' | 'completed' | 'failed';
  progress?: number;
  total?: number;
  step?: string;
  error?: string;
  filename?: string;
  chunks_created?: number;
  collection?: string;
  timestamp?: string;
}

// Collection-related types
export interface CollectionDetails {
  collection: string;
  files_count: number;
  total_vectors: number;
  total_chunks: number;
  vector_size: number;
  distance_function: string;
}

// Chunk-related types
export interface ChunkDetails {
  chunk_id: string;
  content: string;
  score: number;
  payload: Record<string, any>;
  source_file: {
    file_id: string;
    file_name: string;
    category: string;
  };
}

// Chat-related types
export interface ChatReference {
  title: string;
  url: string;
  score: number;
  file_name: string;
  category: string;
}
