import { ChatReference } from '../types';

export interface ChatResponse {
  id: string;
  content: string;
  conversation_id: string;
  timestamp: number;
  references?: ChatReference[];
}

export const chatAPI = {
  sendMessage: async (message: string, conversationId: string | null, collection: string = 'all'): Promise<ChatResponse> => {
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          collection,
        }),
      });

      if (!response.ok) throw new Error('Backend service unavailable');

      return response.json();
    } catch (error) {
      console.error('Chat failed:', error);
      throw new Error('Failed to connect to the Brain API. Ensure the Python service is running.');
    }
  },

  streamMessage: async (message: string, conversationId: string | null, collection: string = 'all', onChunk: (chunk: any) => void) => {
    try {
      const response = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          collection,
        }),
      });

      if (!response.ok) throw new Error('Backend service unavailable');

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      let completeResponse = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = new TextDecoder().decode(value);
        completeResponse += chunk;
        
        // 解析SSE格式
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data:')) {
            const data = line.slice(5).trim();
            if (data) {
              try {
                const parsed = JSON.parse(data);
                onChunk(parsed);
              } catch (e) {
                console.error('Failed to parse chunk:', e);
              }
            }
          }
        }
      }

      return completeResponse;
    } catch (error) {
      console.error('Streaming chat failed:', error);
      throw new Error('Failed to connect to the Brain API. Ensure the Python service is running.');
    }
  },
};
