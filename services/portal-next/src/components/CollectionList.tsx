import React, { useState } from 'react';
import { Badge } from './ui/badge';
import { useCollectionDetails } from '../services/api';
import { Plus, X, Check } from 'lucide-react';

interface Collection {
  value: string;
  label: string;
  count?: number;
}

interface CollectionListProps {
  collections: Collection[];
  selectedCollection: string;
  onSelectCollection: (collection: string) => void;
  onSelectCollectionDetails: (collection: string) => void;
  onAddCollection: (name: string, description: string) => void;
}

const CollectionList: React.FC<CollectionListProps> = ({
  collections,
  selectedCollection,
  onSelectCollection,
  onSelectCollectionDetails,
  onAddCollection,
}) => {
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState('');
  const [newCollectionDescription, setNewCollectionDescription] = useState('');
  const handleCollectionClick = (collection: string) => {
    onSelectCollection(collection);
    onSelectCollectionDetails(collection);
  };

  const handleAddCollection = () => {
    if (newCollectionName.trim()) {
      onAddCollection(newCollectionName.trim(), newCollectionDescription.trim());
      setIsAddDialogOpen(false);
      setNewCollectionName('');
      setNewCollectionDescription('');
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Collections</h3>
        <button
          onClick={() => setIsAddDialogOpen(true)}
          className="p-1 rounded-full hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          aria-label="Add collection"
        >
          <Plus className="h-4 w-4 text-slate-600 dark:text-slate-400" />
        </button>
      </div>
      {collections.map((collection) => (
        <div
          key={collection.value}
          onClick={() => handleCollectionClick(collection.value)}
          className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
            selectedCollection === collection.value
              ? 'bg-blue-100 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800'
              : 'hover:bg-slate-100 dark:hover:bg-slate-800'
          }`}
        >
          <span className="font-medium">{collection.label}</span>
          {collection.count !== undefined && (
            <Badge variant="secondary" className="ml-2">
              {collection.count}
            </Badge>
          )}
        </div>
      ))}

      {/* Add Collection Dialog */}
      {isAddDialogOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h4 className="text-lg font-semibold mb-4">Add New Collection</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Name *
                </label>
                <input
                  type="text"
                  value={newCollectionName}
                  onChange={(e) => setNewCollectionName(e.target.value)}
                  placeholder="Enter collection name"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  value={newCollectionDescription}
                  onChange={(e) => setNewCollectionDescription(e.target.value)}
                  placeholder="Enter collection description (optional)"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => {
                    setIsAddDialogOpen(false);
                    setNewCollectionName('');
                    setNewCollectionDescription('');
                  }}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddCollection}
                  disabled={!newCollectionName.trim()}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors disabled:bg-gray-400 dark:disabled:bg-gray-600"
                >
                  Add Collection
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CollectionList;
