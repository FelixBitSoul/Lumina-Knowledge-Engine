"use client";

import React, { useEffect, useRef } from 'react';
import { useChatStore } from '../../store/chatStore';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import { useSearchStore } from '../../store/searchStore';

export default function ChatComponent() {
  const { messages, isLoading, error, sendMessage } = useChatStore();
  const { selectedCollection } = useSearchStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (content: string) => {
    if (content.trim()) {
      sendMessage(content, selectedCollection);
    }
  };

  return (
    <div className="h-[700px] flex flex-col bg-white dark:bg-[#161B22] rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
      {/* Chat Header */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">AI Assistant</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">Powered by OpenAI</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-400">
            <p className="text-lg mb-2">Start a conversation</p>
            <p className="text-sm">Ask me anything about your knowledge base</p>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}
        {isLoading && (
          <MessageBubble
            message={{
              id: 'loading',
              role: 'assistant',
              content: '',
              timestamp: Date.now(),
              status: 'streaming'
            }}
          />
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border-t border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Input */}
      <ChatInput onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}