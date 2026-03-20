"use client";

import React, { useEffect, useState } from 'react';
import { useTheme } from 'next-themes';
import { Sun, Moon, Cpu, MessageSquare, Search } from 'lucide-react';
import CollectionList from '../components/CollectionList';
import SearchBar from '../components/SearchBar';
import SearchResults from '../components/SearchResults';
import ChatComponent from '../components/Chat/ChatComponent';
import { useSearchStore } from '../store/searchStore';
import { useSearch } from '../services/api';

// Available collections
const collections = [
  { value: 'all', label: 'All Collections' },
  { value: 'core-docs', label: 'Core Docs' },
  { value: 'web-frontends', label: 'Web Frontends' },
  { value: 'backend-apis', label: 'Backend APIs' }
];

// Search result interface
interface SearchResult {
  title: string;
  url: string;
  content: string;
  score: number;
  collection?: string;
}

export default function Home() {
  const { theme, setTheme } = useTheme();
  const { query, selectedCollection, setQuery, setSelectedCollection } = useSearchStore();
  const [activeTab, setActiveTab] = useState<'search' | 'chat'>('search');

  // Use React Query for search
  const { data, isLoading, error } = useSearch(query, selectedCollection);
  const results = data?.results || [];

  // Ensure component is mounted to prevent hydration mismatch
  useEffect(() => {
    // Component mounted
  }, []);

  /**
   * Orchestrates the semantic search by calling the Python Vector Service.
   */
  const handleSearch = (searchQuery: string) => {
    setQuery(searchQuery);
  };

  return (
    <main className="min-h-screen transition-colors duration-500 bg-slate-50 dark:bg-[#0B0F1A] text-slate-900 dark:text-slate-200 py-8 px-4 md:px-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
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

        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-black mb-4 tracking-tight text-slate-900 dark:text-white">
            Knowledge Engine
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-lg max-w-xl mx-auto">
            Semantic search powered by Go crawlers and Python vector embeddings.
          </p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Left Sidebar - Collection List */}
          <div className="lg:col-span-1">
            <div className="sticky top-8 bg-white dark:bg-[#161B22] p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <CollectionList
                collections={collections}
                selectedCollection={selectedCollection}
                onSelectCollection={setSelectedCollection}
              />
            </div>
          </div>

          {/* Right Content - Search Bar and Results */}
          <div className="lg:col-span-3">
            {/* Tab Navigation */}
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

              {/* Tab Content */}
              <div className="p-6">
                {activeTab === 'search' ? (
                  <>
                    {/* Search Bar */}
                    <div className="mb-8">
                      <SearchBar onSearch={handleSearch} loading={isLoading} />
                    </div>

                    {/* Search Results */}
                    <SearchResults
                      results={results}
                      error={error?.message || null}
                      loading={isLoading}
                      query={query}
                    />
                  </>
                ) : (
                  /* Chat Component */
                  <ChatComponent />
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
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
    </main>
  );
}
