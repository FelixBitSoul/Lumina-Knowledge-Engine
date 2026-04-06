"use client";

import React, { useEffect, useState } from 'react';
import { Cpu, MessageSquare, Search, Database, Upload as UploadIcon, Info, ChevronDown, Link } from 'lucide-react';
import CollectionList from '../components/CollectionList';
import SearchBar from '../components/SearchBar';
import SearchResults from '../components/SearchResults';
import ChatComponent from '../components/Chat/ChatComponent';
import UploadModal from '../components/UploadModal';
import FileManager from '../components/FileManager';
import Inspector from '../components/Inspector';
import UploadSheet from '../components/UploadSheet';
import CrawlSheet from '../components/CrawlSheet';
import ThemeToggle from '../components/ThemeToggle';
import { useSearchStore } from '../store/searchStore';
import { useUIStore } from '../store/uiStore';
import { useSearch, useCollections, collectionsAPI } from '../services/api';
import { useUpload } from '../hooks/useUpload';
import { SearchResultItem } from '../types';

export default function Home() {
  const { query, selectedCollection, filters, currentPage, pageSize, setQuery, setSelectedCollection, setPage, setPageSize } = useSearchStore();
  const { activeView, setActiveView, activeItem, setActiveItem, isInspectorOpen, toggleInspector } = useUIStore();
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadSuccessMessage, setUploadSuccessMessage] = useState('');
  const [isUploadSheetOpen, setIsUploadSheetOpen] = useState(false);
  const [isCrawlSheetOpen, setIsCrawlSheetOpen] = useState(false);
  const [isSplitButtonOpen, setIsSplitButtonOpen] = useState(false);

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

  // 监听来自 FileManager 的上传和爬虫事件
  useEffect(() => {
    const handleOpenUploadSheet = () => {
      setIsUploadSheetOpen(true);
    };

    const handleOpenCrawlSheet = () => {
      setIsCrawlSheetOpen(true);
    };

    window.addEventListener('open-upload-sheet', handleOpenUploadSheet);
    window.addEventListener('open-crawl-sheet', handleOpenCrawlSheet);

    return () => {
      window.removeEventListener('open-upload-sheet', handleOpenUploadSheet);
      window.removeEventListener('open-crawl-sheet', handleOpenCrawlSheet);
    };
  }, []);

  const { data, isLoading, error } = useSearch(query, selectedCollection, filters, pageSize, currentPage);
  const results: SearchResultItem[] = data?.results || [];

  const hasNextPage = results.length === pageSize;
  const hasPrevPage = currentPage > 1;

  const uploadMutation = useUpload();

  // 处理新增集合
  const handleAddCollection = async (name: string, description: string) => {
    try {
      await collectionsAPI.createCollection(name, description);
      // 刷新集合列表
      refetchCollections();
    } catch (error) {
      console.error('Failed to create collection:', error);
      alert('Failed to create collection. Please try again.');
    }
  };

  const handleSearch = (searchQuery: string) => {
    setQuery(searchQuery);
    setPage(1);
  };

  const handleUpload = async (file: File, category: string, collection: string) => {
    try {
      const result = await uploadMutation.mutateAsync({ file, category, collection });

      // Close upload modal
      setIsUploadModalOpen(false);
      setUploadSuccess(true);
      setUploadSuccessMessage('File upload initiated successfully');

      // Refresh collections after upload
      setTimeout(() => {
        refetchCollections();
      }, 2000);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handleCollectionSelect = (collection: string) => {
    setSelectedCollection(collection);
  };

  const handleCollectionDetails = (collection: string) => {
    setActiveItem({
      type: 'collection',
      id: collection,
      data: { name: collection },
    });
    toggleInspector();
  };

  const handleResultClick = (result: SearchResultItem) => {
    setActiveItem({
      type: 'chunk',
      id: `${result.url}-${result.content.substring(0, 50)}`,
      data: {
        ...result,
        source_file_id: '1', // 实际应该从 API 返回
        source_file_name: result.title,
      },
    });
    toggleInspector();
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-[#0B0F1A] text-slate-900 dark:text-slate-200">
      {/* Left Sidebar */}
      <div className="w-[260px] border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-[#161B22] flex flex-col">
        <div className="p-6 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
            <Cpu className="text-blue-600 dark:text-blue-400" size={24} />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-300">
              LUMINA
            </span>
          </div>
        </div>

        <div className="flex-1 overflow-auto p-6">
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
                onSelectCollection={handleCollectionSelect}
                onSelectCollectionDetails={handleCollectionDetails}
                onAddCollection={handleAddCollection}
              />
            </>
          ) : (
            <div className="text-center text-slate-500 dark:text-slate-400">
              <p className="text-sm mb-4">No collections available</p>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-slate-200 dark:border-slate-800 flex justify-between items-center">
          <div className="text-xs text-slate-500 dark:text-slate-400">
            Lumina Knowledge Engine
          </div>
          <ThemeToggle />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-[#161B22] flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <h1 className="text-lg font-semibold text-slate-900 dark:text-white">
              {selectedCollection || 'Knowledge Engine'}
            </h1>
            {selectedCollection && (
              <span className="text-xs text-slate-500 dark:text-slate-400">
                {collections.find(c => c.value === selectedCollection)?.label}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveView('conversation')}
              className={`px-4 py-2 rounded-md flex items-center gap-2 transition-colors ${
                activeView === 'conversation'
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                  : 'hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <MessageSquare size={16} />
              <span>Conversation</span>
            </button>
            <button
              onClick={() => setActiveView('knowledge')}
              className={`px-4 py-2 rounded-md flex items-center gap-2 transition-colors ${
                activeView === 'knowledge'
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                  : 'hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <Database size={16} />
              <span>Knowledge Base</span>
            </button>



            <button
              onClick={toggleInspector}
              className={`p-2 rounded-md transition-colors ${
                isInspectorOpen
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                  : 'hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
              aria-label="Toggle Inspector"
            >
              <Info size={16} />
            </button>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-auto">
          {activeView === 'conversation' ? (
            <div className="p-6">
              <div className="mb-8">
                <SearchBar onSearch={handleSearch} loading={isLoading} />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-white dark:bg-[#161B22] rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm p-6">
                  <h2 className="text-lg font-semibold mb-4">Search Results</h2>
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
                    onResultClick={handleResultClick}
                  />
                </div>
                <div className="bg-white dark:bg-[#161B22] rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm p-6">
                  <h2 className="text-lg font-semibold mb-4">Chat</h2>
                  <ChatComponent />
                </div>
              </div>
            </div>
          ) : (
            <FileManager />
          )}
        </div>
      </div>

      {/* Right Inspector */}
      <Inspector />

      {/* Upload Sheet */}
      <UploadSheet
        isOpen={isUploadSheetOpen}
        onClose={() => setIsUploadSheetOpen(false)}
      />

      {/* Crawl Sheet */}
      <CrawlSheet
        isOpen={isCrawlSheetOpen}
        onClose={() => setIsCrawlSheetOpen(false)}
      />
    </div>
  );
}
