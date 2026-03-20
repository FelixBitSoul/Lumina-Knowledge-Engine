"use client";

import { useState, useEffect } from "react";
import { useTheme } from "next-themes";
import { Sun, Moon, Search, ExternalLink, Cpu } from "lucide-react";

/**
 * Interface representing the structure of a search result 
 * returned from the Python FastAPI backend.
 */
interface SearchResult {
  title: string;
  url: string;
  content: string;
  score: number;
  collection?: string;
}

// Available collections
const collections = [
  { value: "all", label: "All Collections" },
  { value: "core-docs", label: "Core Docs" },
  { value: "web-frontends", label: "Web Frontends" },
  { value: "backend-apis", label: "Backend APIs" }
];

export default function Home() {
  const { theme, setTheme } = useTheme();
  const [query, setQuery] = useState("");
  const [selectedCollection, setSelectedCollection] = useState("all");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  // Ensure component is mounted to prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  /**
   * Orchestrates the semantic search by calling the Python Vector Service.
   */
  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);

    try {
      // Build search URL with collection parameter
      let searchUrl = `http://localhost:8000/search?query=${encodeURIComponent(query)}`;
      if (selectedCollection !== "all") {
        searchUrl += `&collection=${encodeURIComponent(selectedCollection)}`;
      }

      // Connect to the Python FastAPI search endpoint
      const response = await fetch(searchUrl);

      if (!response.ok) throw new Error("Backend service unavailable");

      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error("Search failed:", error);
      setError("Failed to connect to the Brain API. Ensure the Python service is running.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  // Prevent rendering until mounted to avoid flickering
  if (!mounted) return null;

  return (
    <main className="min-h-screen transition-colors duration-500 bg-slate-50 dark:bg-[#0B0F1A] text-slate-900 dark:text-slate-200 py-12 px-6">
      <div className="max-w-4xl mx-auto">
        
        {/* Top Navigation / Actions */}
        <div className="flex justify-between items-center mb-12">
          <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
            <Cpu className="text-blue-600 dark:text-blue-400" size={28} />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-300">
              LUMINA
            </span>
          </div>
          
          <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="p-3 rounded-2xl bg-white dark:bg-[#161B22] border border-slate-200 dark:border-slate-800 hover:shadow-lg transition-all active:scale-90"
            aria-label="Toggle Theme"
          >
            {theme === "dark" ? (
              <Sun className="text-yellow-400" size={20} />
            ) : (
              <Moon className="text-blue-600" size={20} />
            )}
          </button>
        </div>

        {/* Hero Section */}
        <header className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-black mb-6 tracking-tight text-slate-900 dark:text-white">
            Knowledge Engine
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-lg max-w-xl mx-auto">
            Semantic search powered by Go crawlers and Python vector embeddings.
          </p>
        </header>

        {/* Search Interface with Collection Selector */}
        <div className="relative group mb-16">
          <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
          <div className="relative flex gap-0 bg-white dark:bg-[#161B22] p-0 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl">
            <select
              value={selectedCollection}
              onChange={(e) => setSelectedCollection(e.target.value)}
              className="bg-white dark:bg-[#161B22] border-r border-slate-200 dark:border-slate-800 rounded-l-3xl px-6 py-4 text-slate-900 dark:text-white text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {collections.map((collection) => (
                <option key={collection.value} value={collection.value}>
                  {collection.label}
                </option>
              ))}
            </select>
            <div className="flex items-center text-slate-400 px-4">
              <Search size={22} />
            </div>
            <input
              type="text"
              className="flex-1 bg-transparent p-4 text-lg text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none"
              placeholder="Ask a technical question..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-10 py-4 rounded-r-3xl font-bold transition-all shadow-lg active:scale-95 disabled:opacity-50"
            >
              {loading ? "Searching..." : "Execute"}
            </button>
          </div>
        </div>

        {/* Results Stream */}
        <section className="space-y-8">
          {error && (
            <div className="rounded-2xl border border-red-500/40 bg-red-500/10 text-red-200 px-4 py-3 text-sm font-mono">
              {error}
            </div>
          )}
          {results.map((res, index) => (
            <div 
              key={index} 
              className="group bg-white dark:bg-[#161B22] p-8 rounded-3xl border border-slate-200 dark:border-slate-800 hover:border-blue-500/50 transition-all shadow-sm hover:shadow-2xl"
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-2xl font-bold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  {res.title}
                </h3>
                <div className="flex flex-col items-end gap-2">
                  <div className="flex items-center gap-2 bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 px-4 py-1.5 rounded-full border border-blue-100 dark:border-blue-500/20 text-xs font-mono font-bold">
                    SCORE: {(res.score * 100).toFixed(1)}%
                  </div>
                  {res.collection && (
                    <div className="flex items-center gap-2 bg-green-50 dark:bg-green-500/10 text-green-600 dark:text-green-400 px-4 py-1.5 rounded-full border border-green-100 dark:border-green-500/20 text-xs font-mono font-bold">
                      COLLECTION: {res.collection}
                    </div>
                  )}
                </div>
              </div>
              
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-6 text-lg italic">
                "{res.content}..."
              </p>
              
              <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
                <span className="text-xs font-mono text-slate-400 truncate max-w-[250px] md:max-w-md">
                  SOURCE: {res.url}
                </span>
                <a 
                  href={res.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-sm font-bold text-blue-600 dark:text-blue-400 hover:opacity-80 transition-opacity"
                >
                  View Documentation <ExternalLink size={14} />
                </a>
              </div>
            </div>
          ))}

          {/* Empty / Initial State */}
          {!loading && query && results.length === 0 && (
            <div className="text-center py-20 opacity-50">
              <p className="text-xl">No neural matches found for your query.</p>
              <p className="text-sm mt-2 font-mono">Check if the crawler has ingested relevant data.</p>
            </div>
          )}
        </section>

        {/* Footer Meta */}
        <footer className="mt-24 text-center border-t border-slate-200 dark:border-slate-800 pt-8 pb-12">
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