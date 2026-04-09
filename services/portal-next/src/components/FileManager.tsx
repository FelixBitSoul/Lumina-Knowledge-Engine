'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { CheckCircle, FileText, Link, Upload, AlertCircle, ChevronDown, MoreVertical, Trash2 } from 'lucide-react';
import { useUIStore } from '../store/uiStore';
import { useSearchStore } from '../store/searchStore';
import { useUpload } from '../hooks/useUpload';
import { useWebSocket } from '../hooks/useUpload';
import { useFiles, filesAPI } from '../services/api';
import { WebSocketMessage } from '../types';

interface FileItem {
  id: string;
  file_name: string;
  category: string;
  collection: string;
  source_type: string;
  content_hash: string;
  minio_path: string;
  created_at: string;
  updated_at: string;
  processing?: {
    status: string;
    progress: number;
    total: number;
    current_step: string;
    error_message?: string;
    chunks_created: number;
    started_at: string;
    completed_at?: string;
  };
  metadata?: Array<{
    key: string;
    value: string;
    created_at: string;
  }>;
}

const FileManager: React.FC = () => {
  const { selectedCollection } = useSearchStore();
  const { setActiveItem } = useUIStore();
  const [isDragging, setIsDragging] = useState(false);
  const [urlInput, setUrlInput] = useState('');
  const [isSplitButtonOpen, setIsSplitButtonOpen] = useState(false);
  const [isDeleteMenuOpen, setIsDeleteMenuOpen] = useState<string | null>(null);
  const [deleteLoading, setDeleteLoading] = useState<string | null>(null);
  const [filesList, setFilesList] = useState<FileItem[]>([]);
  const [offset, setOffset] = useState(0);
  const [isLoadingMore, setIsLoadingMore] = useState(false);

  const uploadMutation = useUpload();
  const { data: filesData, isLoading: filesLoading, error: filesError, refetch: refetchFiles } = useFiles(selectedCollection || '', 20, offset);

  // 处理文件数据，转换后端返回的格式并合并到文件列表
  React.useEffect(() => {
    if (filesData) {
      setFilesList(filesData.files || []);
    }
  }, [filesData]);

  // 处理文件上传后刷新文件列表
  React.useEffect(() => {
    if (uploadMutation.isSuccess) {
      refetchFiles();
    }
  }, [uploadMutation.isSuccess, refetchFiles]);

  // 加载更多文件
  const loadMoreFiles = async () => {
    if (isLoadingMore || !selectedCollection) return;

    setIsLoadingMore(true);
    try {
      const newOffset = offset + 20;
      const result = await filesAPI.getFiles(selectedCollection, 20, newOffset);
      if (result.files && result.files.length > 0) {
        setFilesList(prev => [...prev, ...result.files]);
        setOffset(newOffset);
      }
    } catch (error) {
      console.error('Failed to load more files:', error);
    } finally {
      setIsLoadingMore(false);
    }
  };

  const handleFileUpload = useCallback(async (file: File) => {
    try {
      const result = await uploadMutation.mutateAsync({
        file,
        category: 'document',
        collection: selectedCollection || '',
      });

      // 处理 WebSocket 连接
      const handleWebSocketMessage = (message: WebSocketMessage) => {
        setFilesList(prevFiles => {
          const updatedFiles = prevFiles.map(f =>
            f.id === message.file_id
              ? {
                  ...f,
                  processing: {
                    status: message.step === 'completed' ? 'completed' : 'processing',
                    progress: message.progress || 0,
                    total: message.total || 100,
                    current_step: message.step,
                    error_message: message.error,
                    chunks_created: 0,
                    started_at: f.processing?.started_at || new Date().toISOString(),
                  },
                }
              : f
          );

          // 如果是新文件，添加到列表
          if (!prevFiles.some(f => f.id === message.file_id)) {
            updatedFiles.push({
              id: message.file_id,
              file_name: message.filename || 'Unknown File',
              category: 'document',
              collection: selectedCollection || '',
              source_type: 'document',
              content_hash: '',
              minio_path: '',
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              processing: {
                status: 'processing',
                progress: message.progress || 0,
                total: message.total || 100,
                current_step: message.step,
                error_message: message.error,
                chunks_created: 0,
                started_at: new Date().toISOString(),
              },
            });
          }

          return updatedFiles;
        });
      };

      const { connect } = useWebSocket(result.websocket_url, handleWebSocketMessage);
      const ws = connect();

      return () => {
        ws.close();
      };
    } catch (error) {
      console.error('Upload failed:', error);
    }
  }, [uploadMutation, selectedCollection]);

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

  const handleUrlSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // 处理 URL 爬虫逻辑
    console.log('Crawling URL:', urlInput);
    setUrlInput('');
  };

  const handleFileClick = (file: FileItem) => {
    setActiveItem({
      type: 'file',
      id: file.id,
      data: file,
    });
  };

  // 处理文件删除
  const handleDeleteFile = async (fileId: string, collection: string, filename: string) => {
    try {
      setDeleteLoading(fileId);
      await filesAPI.deleteFile(fileId, collection, filename);
      // 刷新文件列表
      refetchFiles();
      // 弹出 Toast 提示
      alert('File deleted successfully');
    } catch (error) {
      console.error('Failed to delete file:', error);
      alert('Failed to delete file. Please try again.');
    } finally {
      setDeleteLoading(null);
      setIsDeleteMenuOpen(null);
    }
  };

  const renderPipelineStatus = (status: string, error?: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'processing':
        return <div className="h-4 w-4 rounded-full bg-blue-500 animate-pulse" />;
      case 'failed':
        return (
          <div className="relative">
            <AlertCircle className="h-4 w-4 text-red-500" />
            {error && (
              <div className="absolute -top-10 left-0 bg-red-100 text-red-800 text-xs p-2 rounded whitespace-nowrap z-10">
                {error}
              </div>
            )}
          </div>
        );
      default:
        return <div className="h-4 w-4 rounded-full bg-gray-300" />;
    }
  };

  if (!selectedCollection) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8">
        <FileText className="h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
          No Collection Selected
        </h3>
        <p className="text-gray-500 dark:text-gray-400 text-center mb-6">
          Please select a collection from the sidebar to view and manage files
        </p>
      </div>
    );
  }

  if (filesList.length === 0 && !filesLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-8">
          No Files in {selectedCollection}
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl">
          {/* File Dropzone */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${isDragging ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-300 dark:border-gray-700'}`}
          >
            <input {...getInputProps()} />
            <FileText className="h-12 w-12 text-blue-500 mb-4" />
            <h4 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
              Upload Files
            </h4>
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              Drag and drop files here or click to browse
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Supported formats: PDF, Markdown, Text
            </p>
          </div>

          {/* URL Crawler */}
          <div className="border-2 border-dashed rounded-lg p-8 text-center border-gray-300 dark:border-gray-700">
            <Link className="h-12 w-12 text-green-500 mb-4" />
            <h4 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
              Crawl Website
            </h4>
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              Enter a URL to crawl and add to this collection
            </p>
            <form onSubmit={handleUrlSubmit} className="flex gap-2">
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="Enter URL to crawl"
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                required
              />
              <button
                type="submit"
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center gap-2 transition-colors"
              >
                <Link className="h-4 w-4" />
                Crawl
              </button>
            </form>
          </div>
        </div>

        <div className="mt-8 w-full max-w-4xl text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Files uploaded or crawled will appear in the list below. Each file will be processed through our pipeline:
          </p>
          <div className="flex justify-center gap-6 mt-4">
            <div className="text-center">
              <div className="h-4 w-4 rounded-full bg-gray-300 mx-auto mb-1" />
              <span className="text-xs text-gray-500 dark:text-gray-400">Parsed</span>
            </div>
            <div className="text-center">
              <div className="h-4 w-4 rounded-full bg-gray-300 mx-auto mb-1" />
              <span className="text-xs text-gray-500 dark:text-gray-400">Chunked</span>
            </div>
            <div className="text-center">
              <div className="h-4 w-4 rounded-full bg-gray-300 mx-auto mb-1" />
              <span className="text-xs text-gray-500 dark:text-gray-400">Embedded</span>
            </div>
            <div className="text-center">
              <div className="h-4 w-4 rounded-full bg-gray-300 mx-auto mb-1" />
              <span className="text-xs text-gray-500 dark:text-gray-400">Indexed</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto">
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Files in {selectedCollection}
          </h2>
          <div className="relative">
            <button
              onClick={() => setIsSplitButtonOpen(!isSplitButtonOpen)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2 transition-colors"
            >
              <Upload className="h-4 w-4" />
              <span>Upload Files</span>
              <ChevronDown className="h-4 w-4" />
            </button>

            {isSplitButtonOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-10">
                <button
                  onClick={() => {
                    // 触发上传抽屉
                    const event = new CustomEvent('open-upload-sheet');
                    window.dispatchEvent(event);
                    setIsSplitButtonOpen(false);
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                >
                  <Upload className="h-4 w-4" />
                  <span>Upload Files</span>
                </button>
                <button
                  onClick={() => {
                    // 触发爬虫抽屉
                    const event = new CustomEvent('open-crawl-sheet');
                    window.dispatchEvent(event);
                    setIsSplitButtonOpen(false);
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                >
                  <Link className="h-4 w-4" />
                  <span>Crawl Website</span>
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  File Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
              {filesList.map((file) => (
                <tr
                  key={file.id}
                  className="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
                  onClick={() => handleFileClick(file)}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <FileText className="h-5 w-5 text-blue-500 mr-2" />
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {file.file_name}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {file.category}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {file.source_type}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {new Date(file.created_at).toLocaleString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-4">
                      <div className="flex flex-col items-center">
                        <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                          Status
                        </div>
                        {renderPipelineStatus(file.processing?.status || 'pending', file.processing?.error_message)}
                      </div>
                      <div className="flex flex-col items-center">
                        <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                          Progress
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {file.processing?.progress || 0}/{file.processing?.total || 100}
                        </div>
                      </div>
                      <div className="flex flex-col items-center">
                        <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                          Chunks
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {file.processing?.chunks_created || 0}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="relative">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setIsDeleteMenuOpen(isDeleteMenuOpen === file.id ? null : file.id);
                        }}
                        className="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                        aria-label="More actions"
                      >
                        <MoreVertical className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                      </button>
                      {isDeleteMenuOpen === file.id && (
                        <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-10">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              if (confirm('Are you sure you want to delete this file?')) {
                                handleDeleteFile(file.id, file.collection, file.file_name);
                              }
                            }}
                            disabled={deleteLoading === file.id}
                            className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 text-red-600 dark:text-red-400"
                          >
                            {deleteLoading === file.id ? (
                              <div className="h-4 w-4 rounded-full border-2 border-red-600 dark:border-red-400 border-t-transparent animate-spin" />
                            ) : (
                              <Trash2 className="h-4 w-4" />
                            )}
                            <span>{deleteLoading === file.id ? 'Deleting...' : 'Delete File'}</span>
                          </button>
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Load More Button */}
        <div className="mt-6 flex justify-center">
          <button
            onClick={loadMoreFiles}
            disabled={isLoadingMore}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2 transition-colors"
          >
            {isLoadingMore ? (
              <div className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
            <span>{isLoadingMore ? 'Loading...' : 'Load More'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default FileManager;
