"use client";

import React from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  status: 'sending' | 'sent' | 'error' | 'streaming' | 'completed';
}

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] ${isUser ? 'mr-2' : 'ml-2'}`}>
        <div 
          className={`rounded-2xl p-4 ${isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-slate-100 dark:bg-[#21262D] text-slate-900 dark:text-slate-200'}`}
        >
          {message.content}
          {message.status === 'streaming' && (
            <span className="inline-block animate-pulse">...</span>
          )}
        </div>
        <div className={`text-xs text-slate-400 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {new Date(message.timestamp).toLocaleTimeString()}
          {message.status === 'sending' && <span className="ml-2">Sending...</span>}
          {message.status === 'error' && <span className="ml-2 text-red-500">Error</span>}
        </div>
      </div>
    </div>
  );
}