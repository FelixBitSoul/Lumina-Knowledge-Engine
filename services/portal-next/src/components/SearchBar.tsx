import React, { useState } from 'react';
import { Search, Filter, X } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { useSearchStore } from '../store/searchStore';

interface SearchBarProps {
  onSearch: (query: string) => void;
  loading: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch, loading }) => {
  const [query, setQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const { filters, updateFilter, resetFilters } = useSearchStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleResetFilters = () => {
    resetFilters();
  };

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="w-full flex items-center gap-2">
        <div className="relative flex-1">
          <div className="flex items-center absolute inset-y-0 left-0 pl-3 pointer-events-none">
            <Search className="h-4 w-4 text-muted-foreground" />
          </div>
          <Input
            type="text"
            placeholder="Search documents..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="pl-9"
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit(e)}
          />
        </div>
        <Button
          type="button"
          variant="secondary"
          size="lg"
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-1"
        >
          <Filter className="h-4 w-4" />
          Filter
        </Button>
        <Button
          type="submit"
          size="lg"
          disabled={loading}
        >
          {loading ? 'Searching...' : 'Search'}
        </Button>
      </form>

      {showFilters && (
        <div className="mt-4 p-4 border rounded-lg bg-background">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">Filters</h3>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleResetFilters}
              className="text-sm"
            >
              Reset
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Title</label>
              <Input
                type="text"
                placeholder="Filter by title"
                value={filters.title || ''}
                onChange={(e) => updateFilter('title', e.target.value || undefined)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Domain</label>
              <Input
                type="text"
                placeholder="Filter by domain (e.g., example.com)"
                value={filters.domain || ''}
                onChange={(e) => updateFilter('domain', e.target.value || undefined)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Start Time</label>
              <Input
                type="datetime-local"
                value={filters.start_time ? new Date(filters.start_time).toISOString().slice(0, 16) : ''}
                onChange={(e) => {
                  if (e.target.value) {
                    const date = new Date(e.target.value);
                    updateFilter('start_time', date.toISOString());
                  } else {
                    updateFilter('start_time', undefined);
                  }
                }}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">End Time</label>
              <Input
                type="datetime-local"
                value={filters.end_time ? new Date(filters.end_time).toISOString().slice(0, 16) : ''}
                onChange={(e) => {
                  if (e.target.value) {
                    const date = new Date(e.target.value);
                    updateFilter('end_time', date.toISOString());
                  } else {
                    updateFilter('end_time', undefined);
                  }
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchBar;