import { UploadResponse, TaskStatus } from '../types';

export const uploadAPI = {
  uploadDocument: async (file: File, category: string, collection?: string): Promise<UploadResponse> => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    if (collection) {
      formData.append('collection', collection);
    }

    const response = await fetch(`${apiUrl}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  },

  getTaskStatus: async (taskId: string): Promise<TaskStatus> => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/upload/tasks/${taskId}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get task status');
    }

    return response.json();
  },

  getPreviewUrl: async (fileId: string, filename: string, expiry: number = 600): Promise<{ preview_url: string; expires_in: number; expires_at: string }> => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/documents/${fileId}/preview-url?filename=${encodeURIComponent(filename)}&expiry=${expiry}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get preview URL');
    }

    return response.json();
  },
};

export const validateFile = (file: File): { valid: boolean; error?: string } => {
  const allowedExtensions = ['.pdf', '.md', '.markdown', '.txt', '.text'];
  const maxSize = 50 * 1024 * 1024; // 50MB

  const extension = '.' + file.name.split('.').pop()?.toLowerCase();
  if (!extension || !allowedExtensions.includes(extension)) {
    return {
      valid: false,
      error: 'Only PDF, Markdown, and Text files are allowed',
    };
  }

  if (file.size > maxSize) {
    return {
      valid: false,
      error: 'File size must be less than 50MB',
    };
  }

  return { valid: true };
};