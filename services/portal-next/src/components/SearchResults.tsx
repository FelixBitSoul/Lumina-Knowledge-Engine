import React, { useState } from 'react';
import { ExternalLink, Clock, Globe } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader } from './ui/card';
import { Badge } from './ui/badge';
import DocumentSidebar from './DocumentSidebar';
import { SearchResultItem } from '../types';

interface SearchResultsProps {
  results: SearchResultItem[];
  error: string | null;
  loading: boolean;
  query: string;
}

const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  error,
  loading,
  query,
}) => {
  const [selectedDocument, setSelectedDocument] = useState<SearchResultItem | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleDocumentClick = (result: SearchResultItem) => {
    setSelectedDocument(result);
    setIsSidebarOpen(true);
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-16">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-lg font-medium">Searching...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 mb-6">
        <p className="text-red-600 dark:text-red-400">{error}</p>
      </div>
    );
  }

  if (!query) {
    return (
      <div className="text-center py-20 opacity-50">
        <p className="text-xl">Enter a query to search</p>
        <p className="text-sm mt-2">Ask a technical question to get started</p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-20 opacity-50">
        <p className="text-xl">No results found</p>
        <p className="text-sm mt-2">Try a different query or collection</p>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-6">
        {results.map((result, index) => (
          <Card key={index} className="overflow-hidden hover:shadow-md transition-shadow cursor-pointer" onClick={() => handleDocumentClick(result)}>
            <CardHeader className="pb-2">
              <div className="flex justify-between items-start">
                <h3 className="text-xl font-semibold text-slate-900 dark:text-white">
                  {result.title}
                </h3>
                <div className="flex flex-col items-end gap-2">
                  <Badge variant="secondary" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    Score: {(result.score * 100).toFixed(1)}%
                  </Badge>
                  <Badge variant="outline" className="border-purple-500 text-purple-700 dark:border-purple-400 dark:text-purple-400">
                    {result.domain}
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pb-4">
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed italic line-clamp-3">
              "{result.content.length > 200 ? result.content.substring(0, 200) + '...' : result.content}"
            </p>
            </CardContent>
            <CardFooter className="pt-0 border-t border-slate-100 dark:border-slate-800">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between w-full gap-2">
                <div className="flex items-center gap-4">
                  <span className="text-xs font-mono text-slate-400 truncate max-w-[250px] md:max-w-md flex items-center gap-1">
                    <Globe className="h-3 w-3" />
                    {result.url}
                  </span>
                  <span className="text-xs text-slate-400 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatDate(result.updated_at)}
                  </span>
                </div>
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-sm font-medium text-blue-600 dark:text-blue-400 hover:underline"
                >
                  View <ExternalLink className="h-3 w-3" />
                </a>
              </div>
            </CardFooter>
          </Card>
        ))}
      </div>

      {selectedDocument && (
        <DocumentSidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
          document={selectedDocument}
        />
      )}
    </>
  );
};

export default SearchResults;
