'use client';

import React, { useState } from 'react';
import { Link, AlertCircle } from 'lucide-react';
import { useSearchStore } from '../store/searchStore';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from './ui/sheet';

interface CrawlSheetProps {
  isOpen: boolean;
  onClose: () => void;
}

const CrawlSheet: React.FC<CrawlSheetProps> = ({ isOpen, onClose }) => {
  const { selectedCollection } = useSearchStore();
  const [url, setUrl] = useState('');
  const [isCrawling, setIsCrawling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // 处理爬虫提交
  const handleCrawlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedCollection) {
      setError('Please select a collection first');
      return;
    }

    if (!url) {
      setError('Please enter a URL to crawl');
      return;
    }

    try {
      setIsCrawling(true);
      setError(null);
      setSuccess(null);

      // 模拟爬虫请求
      // 实际应该调用后端的爬虫 API
      console.log('Crawling URL:', url, 'for collection:', selectedCollection);

      // 模拟爬虫过程
      await new Promise(resolve => setTimeout(resolve, 2000));

      setSuccess('Crawl initiated successfully');
      setUrl('');

      // 关闭爬虫抽屉
      setTimeout(() => {
        onClose();
      }, 1000);
    } catch (err) {
      setError('Crawl failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setIsCrawling(false);
    }
  };

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent title="Crawl Website">
        <SheetHeader>
          <SheetTitle>Crawl Website</SheetTitle>
        </SheetHeader>
        
        <div className="mt-4">
          {/* Collection Info */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Collection
            </label>
            <div className="px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-md">
              {selectedCollection || 'No collection selected'}
            </div>
          </div>

          {/* URL Input */}
          <form onSubmit={handleCrawlSubmit} className="mb-6">
            <div className="mb-4">
              <label htmlFor="url" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Website URL
              </label>
              <input
                id="url"
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter URL to crawl (e.g., https://example.com)"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                required
              />
            </div>

            {/* Crawl Button */}
            <button
              type="submit"
              disabled={isCrawling || !selectedCollection}
              className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center justify-center gap-2 transition-colors disabled:bg-gray-400 dark:disabled:bg-gray-600"
            >
              {isCrawling ? (
                <>
                  <div className="h-4 w-4 rounded-full bg-white animate-pulse" />
                  <span>Crawling...</span>
                </>
              ) : (
                <>
                  <Link className="h-4 w-4" />
                  <span>Crawl Website</span>
                </>
              )}
            </button>
          </form>

          {/* Status Messages */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-red-700 dark:text-red-300">{error}</span>
            </div>
          )}

          {success && (
            <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md flex items-center gap-2">
              <span className="text-green-700 dark:text-green-300">{success}</span>
            </div>
          )}

          {/* Crawl Info */}
          <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-md">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              About Crawling
            </h4>
            <ul className="text-sm text-gray-500 dark:text-gray-400 space-y-1">
              <li>• The crawler will follow links up to 2 levels deep</li>
              <li>• Only content from the same domain will be crawled</li>
              <li>• Crawling may take several minutes depending on the website size</li>
              <li>• You will receive a notification when crawling is complete</li>
            </ul>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
};

export default CrawlSheet;
