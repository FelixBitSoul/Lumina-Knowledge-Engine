"use client";

import React, { useEffect, useState } from 'react';
import { useTheme } from 'next-themes';
import { Sun, Moon, Cpu, MessageSquare, Search, Upload as UploadIcon } from 'lucide-react';
import CollectionList from '../components/CollectionList';
import SearchBar from '../components/SearchBar';
import SearchResults from '../components/SearchResults';
import ChatComponent from '../components/Chat/ChatComponent';
import UploadModal from '../components/UploadModal';
import ProcessingModal from '../components/ProcessingModal';
import { useSearchStore } from '../store/searchStore';
import { useSearch, useCollections } from '../services/api';
import { useUpload } from '../hooks/useUpload';
import { SearchResultItem } from '../types';

export default function Home() {
  const { theme, setTheme } = useTheme();
  const { query, selectedCollection, filters, currentPage, pageSize, setQuery, setSelectedCollection, setPage, setPageSize } = useSearchStore();
  const [activeTab, setActiveTab] = useState<'search' | 'chat'>('search');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isProcessingModalOpen, setIsProcessingModalOpen] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadSuccessMessage, setUploadSuccessMessage] = useState('');
  const [processingInfo, setProcessingInfo] = useState<{ websocketUrl: string; fileName: string }>({ websocketUrl: '', fileName: '' });

  const { data: collectionsData, isLoading: collectionsLoading, refetch: refetchCollections } = useCollections();

  const collections = collectionsData?.collections?.map((name: string) => ({
    value: name,
    label: name.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
  })) || [];

  useEffect(() => {
    if (collections.length > 0 && !selectedCollection) {
      setSelectedCollection(collections[0].value);
    }
  }, [collections, selectedCollection, setSelectedCollection]);

  const { data, isLoading, error } = useSearch(query, selectedCollection, filters, pageSize, currentPage);
  const results: SearchResultItem[] = data?.results || [];

  const hasNextPage = results.length === pageSize;
  const hasPrevPage = currentPage > 1;

  const uploadMutation = useUpload();

  const handleSearch = (searchQuery: string) => {
    setQuery(searchQuery);
    setPage(1);
  };

  const handleUpload = async (file: File, category: string, collection: string) => {
    try {
      const result = await uploadMutation.mutateAsync({ file, category, collection });

      // Show processing modal with WebSocket connection
      setProcessingInfo({
        websocketUrl: result.websocket_url,
        fileName: file.name
      });
      setIsProcessingModalOpen(true);

      // Close upload modal
      setIsUploadModalOpen(false);

      // Refresh collections after upload (when processing is complete)
      // We'll handle this in the ProcessingModal onClose
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  return (
    <main className="min-h-screen transition-colors duration-500 bg-slate-50 dark:bg-[#0B0F1A] text-slate-900 dark:text-slate-200 py-8 px-4 md:px-6">
      <div className="max-w-7xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
            <Cpu className="text-blue-600 dark:text-blue-400" size={28} />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-300">
              LUMINA
            </span>
          </div>

          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="p-2 rounded-full bg-white dark:bg-[#161B22] border border-slate-200 dark:border-slate-800 hover:shadow-lg transition-all active:scale-90"
            aria-label="Toggle Theme"
          >
            {theme === 'dark' ? (
              <Sun className="text-yellow-400" size={20} />
            ) : (
              <Moon className="text-blue-600" size={20} />
            )}
          </button>
        </header>

        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-black mb-4 tracking-tight text-slate-900 dark:text-white">
            Knowledge Engine
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-lg max-w-xl mx-auto">
            Semantic search powered by Go crawlers and Python vector embeddings.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <div className="sticky top-8 bg-white dark:bg-[#161B22] p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
              {collectionsLoading ? (
                <div className="space-y-3">
                  <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded w-3/4 animate-pulse"></div>
                  <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
                  <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></div>
                </div>
              ) : collections.length > 0 ? (
                <>
                  <CollectionList
                    collections={collections}
                    selectedCollection={selectedCollection}
                    onSelectCollection={setSelectedCollection}
                  />
                  <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-800">
                    <button
                      onClick={() => setIsUploadModalOpen(true)}
                      className="w-full flex items-center justify-center gap-2 py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                    >
                      <UploadIcon className="h-4 w-4" />
                      <span>Upload Document</span>
                    </button>
                  </div>
                </>
              ) : (
                <div className="text-center text-slate-500 dark:text-slate-400">
                  <p className="text-sm">No collections available</p>
                  <button
                    onClick={() => setIsUploadModalOpen(true)}
                    className="mt-4 w-full flex items-center justify-center gap-2 py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                  >
                    <UploadIcon className="h-4 w-4" />
                    <span>Upload Document</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="lg:col-span-3">
            <div className="bg-white dark:bg-[#161B22] rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm mb-8 overflow-hidden">
              <div className="flex border-b border-slate-200 dark:border-slate-800">
                <button
                  onClick={() => setActiveTab('search')}
                  className={`flex-1 py-4 px-6 flex items-center justify-center gap-2 ${activeTab === 'search' ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'}`}
                >
                  <Search size={18} />
                  <span className="font-medium">Search</span>
                </button>
                <button
                  onClick={() => setActiveTab('chat')}
                  className={`flex-1 py-4 px-6 flex items-center justify-center gap-2 ${activeTab === 'chat' ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'}`}
                >
                  <MessageSquare size={18} />
                  <span className="font-medium">Chat</span>
                </button>
              </div>

              <div className="p-6">
                {activeTab === 'search' ? (
                  <>
                    <div className="mb-8">
                      <SearchBar onSearch={handleSearch} loading={isLoading} />
                    </div>

                    <SearchResults
                      results={results}
                      error={error?.message || null}
                      loading={isLoading}
                      query={query}
                      currentPage={currentPage}
                      pageSize={pageSize}
                      hasNextPage={hasNextPage}
                      hasPrevPage={hasPrevPage}
                      onPageChange={setPage}
                      onPageSizeChange={setPageSize}
                    />
                  </>
                ) : (
                  <ChatComponent />
                )}
              </div>
            </div>
          </div>
        </div>

        <footer className="mt-16 text-center border-t border-slate-200 dark:border-slate-800 pt-8 pb-12">
          <div className="flex justify-center gap-6 text-xs font-mono text-slate-400 uppercase tracking-widest">
            <span>Stack: Go 1.22</span>
            <span>•</span>
            <span>Python 3.11</span>
            <span>•</span>
            <span>Qdrant DB</span>
            <span>•</span>
            <span>Next.js 15</span>
          </div>
        </footer>
      </div>

      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => {
          setIsUploadModalOpen(false);
          setUploadSuccess(false);
        }}
        onUpload={handleUpload}
        collections={collections}
        isUploading={uploadMutation.isPending}
        error={uploadMutation.error?.message || null}
        success={uploadSuccess}
        successMessage={uploadSuccessMessage}
      />

      <ProcessingModal
        isOpen={isProcessingModalOpen}
        onClose={() => {
          setIsProcessingModalOpen(false);
          // Refresh collections after processing is complete
          refetchCollections();
        }}
        websocketUrl={processingInfo.websocketUrl}
        fileName={processingInfo.fileName}
      />
    </main>
  );
}
