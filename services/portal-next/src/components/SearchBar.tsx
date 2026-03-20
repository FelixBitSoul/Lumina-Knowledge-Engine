import React, { useState } from 'react';
import { Search } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';

interface SearchBarProps {
  onSearch: (query: string) => void;
  loading: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch, loading }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full flex items-center gap-2">
      <div className="relative flex-1">
        <div className="flex items-center absolute inset-y-0 left-0 pl-3 pointer-events-none">
          <Search className="h-4 w-4 text-muted-foreground" />
        </div>
        <Input
          type="text"
          placeholder="Ask a technical question..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-9"
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit(e)}
        />
      </div>
      <Button
        type="submit"
        size="lg"
        disabled={loading}
      >
        {loading ? 'Searching...' : 'Execute'}
      </Button>
    </form>
  );
};

export default SearchBar;