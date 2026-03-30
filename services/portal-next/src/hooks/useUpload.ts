import { useMutation, UseMutationResult } from '@tanstack/react-query';
import { uploadAPI, UploadResponse } from '../services/uploadAPI';

export const useUpload = (): UseMutationResult<
  UploadResponse,
  Error,
  { file: File; category: string; collection: string }
> => {
  return useMutation({
    mutationFn: ({ file, category, collection }) =>
      uploadAPI.uploadDocument(file, category, collection),
    onSuccess: (data) => {
      console.log('Upload successful:', data);
    },
    onError: (error) => {
      console.error('Upload failed:', error);
    },
  });
};