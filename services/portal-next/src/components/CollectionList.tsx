import React from 'react';
import { Badge } from './ui/badge';

interface Collection {
  value: string;
  label: string;
  count?: number;
}

interface CollectionListProps {
  collections: Collection[];
  selectedCollection: string;
  onSelectCollection: (collection: string) => void;
}

const CollectionList: React.FC<CollectionListProps> = ({
  collections,
  selectedCollection,
  onSelectCollection,
}) => {
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold mb-4">Collections</h3>
      {collections.map((collection) => (
        <div
          key={collection.value}
          onClick={() => onSelectCollection(collection.value)}
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
    </div>
  );
};

export default CollectionList;