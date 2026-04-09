'use client';

import React, { useState } from 'react';
import { useUIStore } from '../store/uiStore';
import { useFileDetails, filesAPI } from '../services/api';
import { FileText, X, Plus, Trash2, Check, Pencil } from 'lucide-react';

// Processing status style mapping
const PROCESSING_STATUS_STYLES: Record<string, string> = {
  completed: 'px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium',
  processing: 'px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium',
  failed: 'px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium',
  default: 'px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium',
};

// Processing status label mapping
const PROCESSING_STATUS_LABELS: Record<string, string> = {
  completed: 'Completed',
  processing: 'Processing',
  failed: 'Failed',
  default: 'Pending',
};

interface MetadataItem {
  key: string;
  value: string;
  created_at: string;
}

interface ProcessingStatus {
  status: string;
  progress: number;
  total: number;
  current_step: string;
  error_message?: string;
  chunks_created: number;
  started_at: string;
  completed_at?: string;
}

interface FileDetails {
  id: string;
  file_name: string;
  category: string;
  collection: string;
  source_type: string;
  content_hash: string;
  minio_path: string;
  created_at: string;
  updated_at: string;
  metadata: MetadataItem[];
  processing: ProcessingStatus | null;
}

const FileDetail: React.FC = () => {
  const { activeItem, setActiveItem } = useUIStore();
  const fileId = activeItem?.id;
  const { data: fileData, isLoading, error, refetch } = useFileDetails(fileId || '');
  
  const [newMetadataKey, setNewMetadataKey] = useState('');
  const [newMetadataValue, setNewMetadataValue] = useState('');
  const [editingMetadata, setEditingMetadata] = useState<{ key: string; value: string } | null>(null);
  const [isAddingMetadata, setIsAddingMetadata] = useState(false);
  const [loading, setLoading] = useState<string | null>(null);

  if (!fileId || !activeItem || activeItem.type !== 'file') {
    return null;
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="h-8 w-8 rounded-full border-2 border-blue-600 border-t-transparent animate-spin" />
      </div>
    );
  }

  if (error || !fileData) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8">
        <FileText className="h-12 w-12 text-red-500 mb-4" />
        <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
          Failed to load file details
        </h3>
        <p className="text-gray-500 dark:text-gray-400 text-center mb-6">
          {error instanceof Error ? error.message : 'An error occurred'}
        </p>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  const file = fileData as FileDetails;

  const handleAddMetadata = async () => {
    if (!newMetadataKey.trim() || !newMetadataValue.trim()) return;

    try {
      setLoading('add');
      await filesAPI.addMetadata(file.id, newMetadataKey.trim(), newMetadataValue.trim());
      await refetch();
      setNewMetadataKey('');
      setNewMetadataValue('');
      setIsAddingMetadata(false);
    } catch (error) {
      console.error('Failed to add metadata:', error);
      alert('Failed to add metadata. Please try again.');
    } finally {
      setLoading(null);
    }
  };

  const handleDeleteMetadata = async (key: string) => {
    if (!confirm('Are you sure you want to delete this metadata?')) return;

    try {
      setLoading(`delete-${key}`);
      await filesAPI.deleteMetadata(file.id, key);
      await refetch();
    } catch (error) {
      console.error('Failed to delete metadata:', error);
      alert('Failed to delete metadata. Please try again.');
    } finally {
      setLoading(null);
    }
  };

  const handleUpdateMetadata = async (key: string, value: string) => {
    if (!value.trim()) return;

    try {
      setLoading(`update-${key}`);
      await filesAPI.addMetadata(file.id, key, value.trim());
      await refetch();
      setEditingMetadata(null);
    } catch (error) {
      console.error('Failed to update metadata:', error);
      alert('Failed to update metadata. Please try again.');
    } finally {
      setLoading(null);
    }
  };

  const renderProcessingStatus = (status: string) => {
    const styleClass = PROCESSING_STATUS_STYLES[status] || PROCESSING_STATUS_STYLES.default;
    const label = PROCESSING_STATUS_LABELS[status] || PROCESSING_STATUS_LABELS.default;
    return <span className={styleClass}>{label}</span>;
  };

  return (
    <div className="h-full flex flex-col border-l border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          {file.file_name}
        </h2>
        <button
          onClick={() => setActiveItem(null)}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
          aria-label="Close"
        >
          <X className="h-5 w-5 text-gray-500 dark:text-gray-400" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {/* File Information */}
        <div className="mb-8">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            File Information
          </h3>
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Category</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">{file.category}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Collection</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">{file.collection}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Source Type</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">{file.source_type}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Created At</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {new Date(file.created_at).toLocaleString()}
                </div>
              </div>
              <div className="md:col-span-2">
                <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Content Hash</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white break-all">
                  {file.content_hash}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Processing Status */}
        {file.processing && (
          <div className="mb-8">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Processing Status
            </h3>
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className="mr-4">
                    {renderProcessingStatus(file.processing.status)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {file.processing.current_step || 'Initializing'}
                  </div>
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {file.processing.progress}/{file.processing.total}
                </div>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                <div
                  className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                  style={{ width: `${(file.processing.progress / file.processing.total) * 100}%` }}
                />
              </div>
              {file.processing.chunks_created > 0 && (
                <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
                  Chunks Created: {file.processing.chunks_created}
                </div>
              )}
              {file.processing.error_message && (
                <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-400 rounded">
                  <div className="font-medium mb-1">Error:</div>
                  <div className="text-sm">{file.processing.error_message}</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Metadata */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Metadata
            </h3>
            {!isAddingMetadata && (
              <button
                onClick={() => setIsAddingMetadata(true)}
                className="flex items-center gap-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors"
              >
                <Plus className="h-4 w-4" />
                Add Metadata
              </button>
            )}
          </div>

          {isAddingMetadata && (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Key
                  </label>
                  <input
                    type="text"
                    value={newMetadataKey}
                    onChange={(e) => setNewMetadataKey(e.target.value)}
                    placeholder="Enter metadata key"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Value
                  </label>
                  <input
                    type="text"
                    value={newMetadataValue}
                    onChange={(e) => setNewMetadataValue(e.target.value)}
                    placeholder="Enter metadata value"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleAddMetadata}
                  disabled={loading === 'add'}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center gap-2"
                >
                  {loading === 'add' ? (
                    <div className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
                  ) : (
                    <Check className="h-4 w-4" />
                  )}
                  {loading === 'add' ? 'Adding...' : 'Add'}
                </button>
                <button
                  onClick={() => {
                    setIsAddingMetadata(false);
                    setNewMetadataKey('');
                    setNewMetadataValue('');
                  }}
                  className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-200 rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {file.metadata && file.metadata.length > 0 ? (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg overflow-hidden">
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {file.metadata.map((meta) => (
                  <div key={meta.key} className="p-4 flex items-center justify-between">
                    <div className="flex-1">
                      {editingMetadata && editingMetadata.key === meta.key ? (
                        <div className="flex gap-2">
                          <input
                            type="text"
                            value={editingMetadata.value}
                            onChange={(e) => setEditingMetadata({ ...editingMetadata, value: e.target.value })}
                            className="flex-1 px-3 py-1 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                          />
                          <div className="flex gap-1">
                            <button
                              onClick={() => handleUpdateMetadata(meta.key, editingMetadata.value)}
                              disabled={loading === `update-${meta.key}`}
                              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
                            >
                              <Check className="h-4 w-4 text-green-600" />
                            </button>
                            <button
                              onClick={() => setEditingMetadata(null)}
                              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
                            >
                              <X className="h-4 w-4 text-gray-500" />
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {meta.key}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {meta.value}
                          </div>
                        </div>
                      )}
                    </div>
                    {!editingMetadata && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => setEditingMetadata({ key: meta.key, value: meta.value })}
                          className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
                          aria-label="Edit"
                        >
                          <Pencil className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                        </button>
                        <button
                          onClick={() => handleDeleteMetadata(meta.key)}
                          disabled={loading === `delete-${meta.key}`}
                          className="p-1 hover:bg-red-100 dark:hover:bg-red-900/20 rounded transition-colors"
                          aria-label="Delete"
                        >
                          {loading === `delete-${meta.key}` ? (
                            <div className="h-4 w-4 rounded-full border-2 border-red-600 border-t-transparent animate-spin" />
                          ) : (
                            <Trash2 className="h-4 w-4 text-red-500" />
                          )}
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-8 text-center">
              <div className="text-gray-500 dark:text-gray-400 mb-4">
                No metadata added yet
              </div>
              <button
                onClick={() => setIsAddingMetadata(true)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                Add Metadata
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileDetail;