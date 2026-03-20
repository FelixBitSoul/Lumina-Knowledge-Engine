"use client";

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

interface QueryClientProviderWrapperProps {
  children: React.ReactNode;
}

export default function QueryClientProviderWrapper({ children }: QueryClientProviderWrapperProps) {
  // Create a client
  const queryClient = new QueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}