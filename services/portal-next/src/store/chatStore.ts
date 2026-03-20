import { create } from 'zustand';
import { chatAPI } from '../services/chatAPI';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  status: 'sending' | 'sent' | 'error' | 'streaming' | 'completed';
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  currentMessageId: string | null;
  conversationId: string | null;
  
  sendMessage: (content: string, collection: string) => Promise<void>;
  clearMessages: () => void;
  setError: (error: string | null) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  error: null,
  currentMessageId: null,
  conversationId: null,
  
  sendMessage: async (content: string, collection: string) => {
    const userId = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const assistantId = `assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const timestamp = Date.now();
    const { conversationId, messages } = get();
    
    // Add user message
    const newUserMessage = {
      id: userId,
      role: 'user' as const,
      content,
      timestamp,
      status: 'sent' as const
    };
    
    // Add assistant message placeholder
    const newAssistantMessage = {
      id: assistantId,
      role: 'assistant' as const,
      content: '',
      timestamp: Date.now(),
      status: 'streaming' as const
    };
    
    set({ 
      messages: [...messages, newUserMessage, newAssistantMessage],
      isLoading: true,
      error: null,
      currentMessageId: assistantId
    });
    
    try {
      // Use streaming API
      await chatAPI.streamMessage(
        content,
        conversationId,
        collection,
        (chunk) => {
          const { messages: currentMessages } = get();
          const updatedMessages = currentMessages.map(msg => {
            if (msg.id === assistantId) {
              return {
                ...msg,
                content: msg.content + chunk.content,
                status: chunk.is_finished ? 'completed' as const : 'streaming' as const
              };
            }
            return msg;
          });
          
          set({ 
            messages: updatedMessages,
            conversationId: chunk.conversation_id
          });
        }
      );
      
      set({ 
        isLoading: false,
        currentMessageId: null
      });
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      
      const { messages: currentMessages } = get();
      const updatedMessages = currentMessages.map(msg => {
        if (msg.id === assistantId) {
          return { ...msg, status: 'error' as const };
        }
        return msg;
      });
      
      set({ 
        error: errorMessage,
        isLoading: false,
        messages: updatedMessages,
        currentMessageId: null
      });
    }
  },
  
  clearMessages: () => {
    set({ messages: [], conversationId: null, error: null });
  },
  
  setError: (error: string | null) => {
    set({ error });
  },
}));
