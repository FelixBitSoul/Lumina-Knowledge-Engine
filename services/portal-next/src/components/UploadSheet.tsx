'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { useSearchStore } from '../store/searchStore';
import { useUpload } from '../hooks/useUpload';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from './ui/sheet';

interface UploadSheetProps {
  isOpen: boolean;
  onClose: () => void;
}

const UploadSheet: React.FC<UploadSheetProps> = ({ isOpen, onClose }) => {
  const { selectedCollection } = useSearchStore();
  const [category, setCategory] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  
  const uploadMutation = useUpload();

  // 常用标签建议
  const commonCategories = ['Documentation', 'Research', 'Blog', 'Tutorial', 'Guide', 'Report', 'Presentation', 'Paper'];

  // 处理分类输入变化，提供建议
  const handleCategoryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setCategory(value);
    
    if (value) {
      const filteredSuggestions = commonCategories.filter(cat => 
        cat.toLowerCase().includes(value.toLowerCase())
      );
      setSuggestions(filteredSuggestions);
    } else {
      setSuggestions([]);
    }
  };

  // 选择建议
  const handleSelectSuggestion = (suggestion: string) => {
    setCategory(suggestion);
    setSuggestions([]);
  };

  // 处理文件上传
  const handleFileUpload = useCallback(async (file: File) => {
    try {
      if (!selectedCollection) {
        alert('Please select a collection first');
        return;
      }

      const result = await uploadMutation.mutateAsync({
        file,
        category: category || 'Document',
        collection: selectedCollection,
      });

      // 关闭上传抽屉
      onClose();
    } catch (error) {
      console.error('Upload failed:', error);
    }
  }, [uploadMutation, selectedCollection, category, onClose]);

  // 配置 dropzone
  const { getRootProps, getInputProps } = useDropzone({
    accept: { 'application/pdf': ['.pdf'], 'text/plain': ['.txt'], 'text/markdown': ['.md', '.markdown'] },
    onDrop: (acceptedFiles) => {
      acceptedFiles.forEach(file => {
        handleFileUpload(file);
      });
      setIsDragging(false);
    },
    onDragEnter: () => setIsDragging(true),
    onDragLeave: () => setIsDragging(false),
    onDropRejected: () => setIsDragging(false),
  });

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent title="Upload Files">
        <SheetHeader>
          <SheetTitle>Upload Files</SheetTitle>
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

          {/* Category Input */}
          <div className="mb-6">
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Category
            </label>
            <div className="relative">
              <input
                id="category"
                type="text"
                value={category}
                onChange={handleCategoryChange}
                placeholder="Enter category (e.g., Documentation, Research)"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
              />
              {suggestions.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-10">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSelectSuggestion(suggestion)}
                      className="w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* File Dropzone */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragging ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-300 dark:border-gray-700'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
              Drag and drop files here
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              or click to browse
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
              Supported formats: PDF, Markdown, Text
            </p>
          </div>

          {/* Upload Status */}
          {uploadMutation.isPending && (
            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md flex items-center gap-2">
              <div className="h-4 w-4 rounded-full bg-blue-500 animate-pulse" />
              <span className="text-blue-700 dark:text-blue-300">Uploading...</span>
            </div>
          )}

          {uploadMutation.error && (
            <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-red-700 dark:text-red-300">
                {uploadMutation.error.message || 'Upload failed'}
              </span>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
};

export default UploadSheet;
