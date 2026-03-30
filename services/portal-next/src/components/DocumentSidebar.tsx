import React from 'react';
import { X, ExternalLink, Globe, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from './ui/card';
import { Button } from './ui/button';
import { SearchResultItem } from '../types';

interface DocumentSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  document: SearchResultItem;
}

const DocumentSidebar: React.FC<DocumentSidebarProps> = ({ isOpen, onClose, document }) => {
  if (!isOpen) return null;

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch {
      return dateString;
    }
  };

  return (
    <>
      {/* Overlay */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
        onClick={onClose}
      />
      
      {/* Sidebar */}
      <div className="fixed right-0 top-0 bottom-0 w-full lg:w-1/3 bg-white dark:bg-[#161B22] shadow-2xl z-50 transform transition-transform duration-300 ease-in-out lg:translate-x-0"
           style={{ transform: isOpen ? 'translateX(0)' : 'translateX(100%)' }}>
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="flex justify-between items-center p-4 border-b border-slate-200 dark:border-slate-800">
            <h2 className="text-xl font-bold">Document</h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
          
          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            <Card className="border-0 shadow-none">
              <CardHeader>
                <CardTitle className="text-2xl font-bold">{document.title}</CardTitle>
              </CardHeader>
              <CardContent className="py-6">
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-6">
                  {document.content}
                </p>
                
                {/* Metadata */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                    <Globe className="h-4 w-4" />
                    <span><strong>Domain:</strong> {document.domain}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                    <Clock className="h-4 w-4" />
                    <span><strong>Updated:</strong> {formatDate(document.updated_at)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                    <span><strong>Score:</strong> {(document.score * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between border-t border-slate-200 dark:border-slate-800">
                <span className="text-sm text-slate-500 dark:text-slate-400 truncate max-w-[200px]">
                  Source: {document.url}
                </span>
              </CardFooter>
            </Card>
          </div>
          
          {/* Footer */}
          <div className="p-4 border-t border-slate-200 dark:border-slate-800">
            <a
              href={document.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              View Original <ExternalLink className="h-4 w-4" />
            </a>
          </div>
        </div>
      </div>
    </>
  );
};

export default DocumentSidebar;