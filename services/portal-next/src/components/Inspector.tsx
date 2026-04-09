'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X, FileText, Database, Code, ExternalLink, ChevronLeft } from 'lucide-react';
import { useUIStore } from '../store/uiStore';
import { uploadAPI } from '../services/uploadAPI';
import { useCollectionDetails, useChunkDetails } from '../services/api';
import FileDetail from './FileDetail';

// Status style mapping for pipeline steps
const STATUS_STYLES: Record<string, string> = {
  completed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  processing: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  default: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
};

const Inspector: React.FC = () => {
  const { activeItem, isInspectorOpen, setIsInspectorOpen, setActiveItem } = useUIStore();
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  
  // 使用 useCollectionDetails 钩子获取集合详情
  const { data: collectionDetails, isLoading: isCollectionLoading } = useCollectionDetails(
    activeItem?.type === 'collection' ? activeItem.id : ''
  );
  
  // 使用 useChunkDetails 钩子获取切片详情
  const { data: chunkDetails, isLoading: isChunkLoading } = useChunkDetails(
    activeItem?.type === 'chunk' ? activeItem.id : '',
    activeItem?.data?.collection || ''
  );

  useEffect(() => {
    if (activeItem?.type === 'file' && activeItem.id) {
      // 获取文件预览链接
      uploadAPI.getPreviewUrl(activeItem.id, activeItem.data.name)
        .then(response => setPreviewUrl(response.preview_url))
        .catch(error => console.error('Failed to get preview URL:', error));
    }
  }, [activeItem]);

  const handleClose = () => {
    setIsInspectorOpen(false);
    setActiveItem(null);
  };

  const handleGoToSource = () => {
    if (activeItem?.type === 'chunk' && activeItem.data.source_file_id) {
      setActiveItem({
        type: 'file',
        id: activeItem.data.source_file_id,
        data: { name: activeItem.data.source_file_name },
      });
    }
  };

  const renderCollectionInspector = () => {
    if (!activeItem || activeItem.type !== 'collection') return null;

    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Collection: {activeItem.id}
          </h3>
          <Database className="h-6 w-6 text-blue-500" />
        </div>

        {collectionDetails ? (
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Files</div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {collectionDetails.files_count}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Vectors</div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {collectionDetails.total_vectors}
                  </div>
                </div>
                <div className="col-span-2">
                  <div className="text-sm text-gray-500 dark:text-gray-400">Chunks</div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {collectionDetails.total_chunks}
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Collection Details
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Name:</span>
                  <span className="text-gray-900 dark:text-white">{activeItem.id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Vector Size:</span>
                  <span className="text-gray-900 dark:text-white">{collectionDetails.vector_size}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Distance Function:</span>
                  <span className="text-gray-900 dark:text-white">{collectionDetails.distance_function}</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="animate-pulse space-y-2">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderFileInspector = () => {
    if (!activeItem || activeItem.type !== 'file') return null;

    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            File: {activeItem.data.name}
          </h3>
          <FileText className="h-6 w-6 text-blue-500" />
        </div>

        <div className="space-y-4">
          <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              File Details
            </h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">File ID:</span>
                <span className="text-gray-900 dark:text-white font-mono truncate max-w-[200px]">
                  {activeItem.id}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">SHA-256:</span>
                <span className="text-gray-900 dark:text-white font-mono truncate max-w-[200px]">
                  {activeItem.id.substring(0, 8)}...{activeItem.id.substring(activeItem.id.length - 8)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Size:</span>
                <span className="text-gray-900 dark:text-white">
                  {activeItem.data.size ? (
                    activeItem.data.size > 1024 * 1024 ? 
                      `${(activeItem.data.size / (1024 * 1024)).toFixed(2)} MB` :
                      `${(activeItem.data.size / 1024).toFixed(2)} KB`
                  ) : 'Unknown'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Uploaded:</span>
                <span className="text-gray-900 dark:text-white">
                  {activeItem.data.uploadedAt ? 
                    new Date(activeItem.data.uploadedAt).toLocaleString() : 
                    'Unknown'}
                </span>
              </div>
            </div>
          </div>

          {previewUrl && (
            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Preview
              </h4>
              <a
                href={previewUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline"
              >
                <ExternalLink className="h-4 w-4" />
                View File Preview
              </a>
            </div>
          )}

          <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Processing Status
            </h4>
            {activeItem.data.pipeline && (
              <div className="space-y-2 text-sm">
                {Object.entries(activeItem.data.pipeline).map(([step, status]) => (
                  <div key={step} className="flex justify-between items-center">
                    <span className="text-gray-500 dark:text-gray-400">
                      {step.charAt(0).toUpperCase() + step.slice(1)}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${STATUS_STYLES[status as string] || STATUS_STYLES.default}`}>
                      {status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderChunkInspector = () => {
    if (!activeItem || activeItem.type !== 'chunk') return null;

    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Chunk Details
          </h3>
          <Code className="h-6 w-6 text-blue-500" />
        </div>

        {chunkDetails ? (
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Chunk Info
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Score:</span>
                  <span className="text-gray-900 dark:text-white font-mono">
                    {chunkDetails.score ? chunkDetails.score.toFixed(4) : 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Source File:</span>
                  <span className="text-gray-900 dark:text-white truncate max-w-[200px]">
                    {chunkDetails.source_file.file_name || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Category:</span>
                  <span className="text-gray-900 dark:text-white">
                    {chunkDetails.source_file.category || 'Unknown'}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Content
                </h4>
                {chunkDetails.source_file.file_id && (
                  <button
                    onClick={() => setActiveItem({
                      type: 'file',
                      id: chunkDetails.source_file.file_id,
                      data: { name: chunkDetails.source_file.file_name }
                    })}
                    className="text-xs text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                  >
                    <ChevronLeft className="h-3 w-3" />
                    Go to Source
                  </button>
                )}
              </div>
              <div className="text-sm text-gray-900 dark:text-white p-3 bg-white dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-700 max-h-40 overflow-auto">
                {chunkDetails.content || 'No content available'}
              </div>
            </div>

            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Raw Payload
              </h4>
              <div className="text-xs font-mono text-gray-900 dark:text-white p-3 bg-white dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-700 max-h-40 overflow-auto">
                <pre>
                  {JSON.stringify(chunkDetails.payload, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="animate-pulse space-y-2">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderContent = () => {
    if (!activeItem) {
      return (
        <div className="flex flex-col items-center justify-center h-full p-6">
          <p className="text-gray-500 dark:text-gray-400 text-center">
            Select an item to view details
          </p>
        </div>
      );
    }

    switch (activeItem.type) {
      case 'collection':
        return renderCollectionInspector();
      case 'file':
        return <FileDetail />;
      case 'chunk':
        return renderChunkInspector();
      default:
        return null;
    }
  };

  if (!isInspectorOpen) return null;

  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 20, stiffness: 100 }}
      className="fixed top-0 right-0 w-[380px] h-full bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-800 z-50 flex flex-col"
    >
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Inspector
        </h2>
        <button
          onClick={handleClose}
          className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <X className="h-5 w-5 text-gray-500 dark:text-gray-400" />
        </button>
      </div>
      <div className="flex-1 overflow-auto">
        {renderContent()}
      </div>
    </motion.div>
  );
};

export default Inspector;
