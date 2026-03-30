export const uploadAPI = {
  uploadDocument: async (file: File, category: string, collection?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    if (collection) {
      formData.append('collection', collection);
    }

    const response = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
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

export type UploadResponse = {
  document_id: string;
  chunks_created: number;
  file_name: string;
  category: string;
  content_hash: string;
  collection: string;
};