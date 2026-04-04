import { useMutation, useQuery, UseMutationResult, UseQueryResult } from '@tanstack/react-query';
import { useCallback } from 'react';
import { uploadAPI } from '../services/uploadAPI';
import { UploadResponse, TaskStatus, WebSocketMessage } from '../types';

export const useUpload = (): UseMutationResult<
  UploadResponse,
  Error,
  { file: File; category: string; collection: string }
> => {
  return useMutation({
    mutationFn: ({ file, category, collection }) =>
      uploadAPI.uploadDocument(file, category, collection),
    onSuccess: (data) => {
      console.log('Upload initiated:', data);
    },
    onError: (error) => {
      console.error('Upload failed:', error);
    },
  });
};

export const useTaskStatus = (taskId: string): UseQueryResult<TaskStatus, Error> => {
  return useQuery({
    queryKey: ['taskStatus', taskId],
    queryFn: () => uploadAPI.getTaskStatus(taskId),
    enabled: !!taskId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false; // Stop polling when task is complete
      }
      return 2000; // Poll every 2 seconds
    },
  });
};

export const useWebSocket = (websocketUrl: string, onMessage: (message: WebSocketMessage) => void) => {
  const connect = useCallback(() => {
    console.log('[WebSocket] Connecting to:', websocketUrl);
    const ws = new WebSocket(websocketUrl);

    ws.onopen = () => {
      console.log('[WebSocket] Connected successfully');
    };

    ws.onmessage = (event) => {
      console.log('[WebSocket] Raw message received:', event.data);
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        console.log('[WebSocket] Parsed message:', message);
        onMessage(message);
      } catch (error) {
        console.error('[WebSocket] Error parsing message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[WebSocket] Error:', error);
    };

    ws.onclose = (event) => {
      console.log('[WebSocket] Disconnected. Code:', event.code, 'Reason:', event.reason);
    };

    return ws;
  }, [websocketUrl, onMessage]);

  return { connect };
};
