# TypeScript Style Guide

This style guide defines coding standards and best practices for TypeScript/JavaScript code in the Lumina Knowledge Engine project, specifically for the Portal frontend (`services/portal-next`).

---

## 📋 Table of Contents

- [Code Formatting](#code-formatting)
- [TypeScript Configuration](#typescript-configuration)
- [Naming Conventions](#naming-conventions)
- [Project Structure](#project-structure)
- [React & Next.js Patterns](#react--nextjs-patterns)
- [Type System](#type-system)
- [Testing](#testing)
- [Anti-patterns to Avoid](#anti-patterns-to-avoid)

---

## 🎨 Code Formatting

### Mandatory Formatting

All TypeScript/JavaScript code **must** be formatted with **Prettier**:

```bash
# Install prettier
npm install --save-dev prettier

# Format all files
npx prettier --write .

# Check formatting
npx prettier --check .

# Format specific files
npx prettier --write "src/**/*.{ts,tsx}"
```

### ESLint

Use ESLint for code quality:

```bash
# Run ESLint
npx eslint . --ext .ts,.tsx

# Fix auto-fixable issues
npx eslint . --ext .ts,.tsx --fix
```

### Prettier Configuration (`.prettierrc`)

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "avoid",
  "endOfLine": "lf"
}
```

### ESLint Configuration (`.eslintrc.json`)

```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended"
  ],
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint"],
  "rules": {
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/explicit-function-return-type": "off",
    "@typescript-eslint/no-explicit-any": "warn",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

---

## ⚙️ TypeScript Configuration

### tsconfig.json Standards

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "ES2022"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### Import Organization

Order imports as follows:

1. React/Next.js imports
2. Third-party libraries
3. Absolute imports (using `@/` alias)
4. Relative imports
5. Type imports

```typescript
// 1. React/Next.js
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

// 2. Third-party libraries
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Search } from 'lucide-react';

// 3. Absolute imports
import { Button } from '@/components/ui/button';
import { SearchService } from '@/lib/services/search';

// 4. Relative imports
import { SearchResult } from './SearchResult';

// 5. Type imports
import type { SearchResponse } from '@/types/search';
```

---

## 🏷 Naming Conventions

### General Rules

| Type | Convention | Example |
|------|------------|---------|
| **Variables** | camelCase | `searchQuery`, `isLoading` |
| **Functions** | camelCase | `handleSearch()`, `fetchResults()` |
| **Components** | PascalCase | `SearchBar`, `ResultCard` |
| **Types/Interfaces** | PascalCase | `SearchResult`, `UserProfile` |
| **Enums** | PascalCase + PascalCase | `Status.Active`, `Type.Document` |
| **Constants** | UPPER_SNAKE_CASE | `API_URL`, `DEFAULT_LIMIT` |
| **Private** | _leadingUnderscore | `_internalHelper` |
| **Files (components)** | PascalCase | `SearchBar.tsx` |
| **Files (utils)** | camelCase | `searchUtils.ts` |
| **Files (types)** | camelCase | `searchTypes.ts` |

### Variable Names

```typescript
// Good - descriptive
const searchQuery = 'python tutorial';
const isLoading = true;
const resultsCount = 42;

// Bad - unclear
const q = 'python';      // What's 'q'?
const flag = true;        // What flag?
const num = 42;           // What number?
```

### Function Names

```typescript
// Good - action verbs
function handleSearch(query: string): void { }
async function fetchResults(url: string): Promise<SearchResult[]> { }
function normalizeQuery(input: string): string { }

// Bad - unclear names
function process(data: unknown): unknown { }    // Too vague
function doStuff(): void { }                   // Meaningless
function handler(a: string, b: number): void { }  // Unclear parameters
```

### Component Names

```typescript
// Good - descriptive nouns
function SearchBar() { }
function ResultCard({ result }: ResultCardProps) { }
function LoadingSpinner() { }

// Bad - unclear
function Component() { }           // Too generic
function Thing() { }               // Meaningless
function Display({ data }) { }     // What does it display?
```

### Interface/Type Names

```typescript
// Good - descriptive
interface SearchResult {
  title: string;
  url: string;
  content: string;
}

type SearchStatus = 'idle' | 'loading' | 'success' | 'error';

type SearchHandler = (query: string) => Promise<SearchResult[]>;

// Bad - unclear
interface Data { }           // What data?
type Props = { };            // Too generic
type Result = unknown;       // Unclear
```

### Enum Names

```typescript
// Good - clear names
enum LoadingState {
  Idle = 'idle',
  Loading = 'loading',
  Success = 'success',
  Error = 'error',
}

enum HttpStatus {
  OK = 200,
  NotFound = 404,
  ServerError = 500,
}

// Bad - unclear
enum State { }               // Too generic
enum Status {                // Ambiguous values
  One = 1,
  Two = 2,
}
```

---

## 📁 Project Structure

### Next.js 15 App Router Structure

```
services/portal-next/
├── 📁 src/
│   ├── 📁 app/                    # Next.js App Router
│   │   ├── 📄 layout.tsx        # Root layout
│   │   ├── 📄 page.tsx          # Home page
│   │   ├── 📄 globals.css        # Global styles
│   │   ├── 📄 loading.tsx       # Loading UI
│   │   ├── 📄 error.tsx          # Error UI
│   │   └── 📁 api/               # API routes (if any)
│   │
│   ├── 📁 components/           # React components
│   │   ├── 📁 ui/               # Base UI components
│   │   │   ├── 📄 button.tsx
│   │   │   ├── 📄 input.tsx
│   │   │   └── 📄 card.tsx
│   │   ├── 📁 search/           # Search-related components
│   │   │   ├── 📄 SearchBar.tsx
│   │   │   ├── 📄 SearchResults.tsx
│   │   │   └── 📄 ResultCard.tsx
│   │   └── 📄 ThemeToggle.tsx   # Other components
│   │
│   ├── 📁 hooks/                # Custom React hooks
│   │   ├── 📄 useSearch.ts
│   │   └── 📄 useDebounce.ts
│   │
│   ├── 📁 lib/                  # Utility functions
│   │   ├── 📁 services/          # API services
│   │   │   └── 📄 search.ts
│   │   ├── 📁 utils/            # Helper functions
│   │   │   └── 📄 cn.ts         # Tailwind class merge
│   │   └── 📁 types/            # Type definitions
│   │       └── 📄 search.ts
│   │
│   └── 📁 styles/               # Additional styles
│
├── 📁 public/                   # Static assets
├── 📄 next.config.ts            # Next.js configuration
├── 📄 tailwind.config.ts        # Tailwind configuration
├── 📄 tsconfig.json             # TypeScript configuration
├── 📄 package.json              # Dependencies
└── 📄 README.md                 # Service documentation
```

### Component File Organization

```typescript
// 1. Imports
import { useState } from 'react';
import { Search } from 'lucide-react';

// 2. Types/Interfaces
interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
}

// 3. Component
export function SearchBar({ onSearch, placeholder = 'Search...' }: SearchBarProps) {
  const [query, setQuery] = useState('');
  
  // ... component logic
  
  return (
    // ... JSX
  );
}

// 4. Default export (if applicable)
export default SearchBar;
```

---

## ⚛️ React & Next.js Patterns

### Functional Components

Always use functional components with hooks:

```typescript
// Good - functional component with hooks
interface UserCardProps {
  name: string;
  email: string;
  avatar?: string;
}

export function UserCard({ name, email, avatar }: UserCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  return (
    <div className="user-card">
      {avatar && <img src={avatar} alt={name} />}
      <h3>{name}</h3>
      <p>{email}</p>
    </div>
  );
}

// Bad - class components (unless necessary)
class UserCard extends React.Component<UserCardProps> {
  // Don't use unless necessary
}
```

### Custom Hooks

```typescript
// hooks/useSearch.ts
import { useState, useEffect, useCallback } from 'react';

interface UseSearchOptions {
  debounceMs?: number;
}

interface UseSearchReturn {
  query: string;
  setQuery: (query: string) => void;
  results: SearchResult[];
  isLoading: boolean;
  error: Error | null;
}

export function useSearch(options: UseSearchOptions = {}): UseSearchReturn {
  const { debounceMs = 300 } = options;
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  // Search logic with debounce
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (!query.trim()) {
        setResults([]);
        return;
      }
      
      setIsLoading(true);
      setError(null);
      
      try {
        const searchResults = await performSearch(query);
        setResults(searchResults);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Search failed'));
      } finally {
        setIsLoading(false);
      }
    }, debounceMs);
    
    return () => clearTimeout(timer);
  }, [query, debounceMs]);
  
  return {
    query,
    setQuery,
    results,
    isLoading,
    error,
  };
}
```

### Props Destructuring

```typescript
// Good - destructure in parameter
function SearchBar({ 
  onSearch, 
  placeholder = 'Search...',
  disabled = false 
}: SearchBarProps) {
  // Use onSearch, placeholder, disabled directly
}

// Acceptable - destructure in function body
function SearchBar(props: SearchBarProps) {
  const { onSearch, placeholder = 'Search...' } = props;
  // ...
}

// Bad - using props. everywhere
function SearchBar(props: SearchBarProps) {
  return (
    <input 
      placeholder={props.placeholder}  // Too verbose
      onChange={props.onSearch}        // Inconsistent
    />
  );
}
```

### Event Handlers

```typescript
// Good - named handlers
function SearchBar({ onSearch }: SearchBarProps) {
  const [query, setQuery] = useState('');
  
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(event.target.value);
  };
  
  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onSearch(query);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input 
        value={query}
        onChange={handleInputChange}
      />
    </form>
  );
}

// Bad - inline anonymous functions
function SearchBarBad({ onSearch }: SearchBarProps) {
  return (
    <input 
      onChange={(e) => /* logic here */}  // Hard to read
      onBlur={() => /* more logic */}       // Duplicated if reused
    />
  );
}
```

### Conditional Rendering

```typescript
// Good - early returns
function SearchResults({ results, isLoading, error }: SearchResultsProps) {
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  if (error) {
    return <ErrorMessage error={error} />;
  }
  
  if (results.length === 0) {
    return <EmptyState />;
  }
  
  return (
    <ul>
      {results.map(result => (
        <ResultCard key={result.id} result={result} />
      ))}
    </ul>
  );
}

// Acceptable - ternary for simple cases
function StatusBadge({ status }: { status: Status }) {
  return (
    <span className={status === 'active' ? 'text-green-600' : 'text-gray-600'}>
      {status}
    </span>
  );
}

// Bad - nested ternaries
function StatusBadgeBad({ status, type, isAdmin }: StatusBadgeProps) {
  return (
    <span>
      {status === 'active' 
        ? isAdmin 
          ? type === 'premium' 
            ? 'Active Premium Admin'
            : 'Active Admin'
          : 'Active User'
        : 'Inactive'}
    </span>
  );
}
```

### Tailwind CSS Usage

```typescript
// Good - use cn() utility for conditional classes
import { cn } from '@/lib/utils/cn';

function Button({ 
  variant = 'primary', 
  size = 'md', 
  className,
  children 
}: ButtonProps) {
  return (
    <button
      className={cn(
        // Base styles
        'inline-flex items-center justify-center font-medium',
        'transition-colors focus:outline-none focus:ring-2',
        
        // Variant styles
        variant === 'primary' && 'bg-blue-600 text-white hover:bg-blue-700',
        variant === 'secondary' && 'bg-gray-200 text-gray-800 hover:bg-gray-300',
        
        // Size styles
        size === 'sm' && 'px-3 py-1.5 text-sm',
        size === 'md' && 'px-4 py-2 text-base',
        size === 'lg' && 'px-6 py-3 text-lg',
        
        // Custom classes passed from parent
        className
      )}
    >
      {children}
    </button>
  );
}

// lib/utils/cn.ts
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

---

## 📐 Type System

### Strict Typing

Enable strict mode in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true
  }
}
```

### Avoid `any`

```typescript
// Bad - using any
function processData(data: any): any {
  return data.value;
}

// Good - proper typing
interface Data {
  value: number;
  label: string;
}

function processData(data: Data): number {
  return data.value;
}

// Acceptable - unknown with type guard
function processUnknown(data: unknown): number {
  if (typeof data === 'object' && data !== null && 'value' in data) {
    const dataObj = data as { value: number };
    return dataObj.value;
  }
  throw new Error('Invalid data format');
}
```

### Type Inference

```typescript
// Good - let TypeScript infer when obvious
const count = 42;                          // inferred as number
const message = 'Hello';                  // inferred as string
const items = ['a', 'b', 'c'];            // inferred as string[]

// Good - explicit types when not obvious
const fetchData = async (): Promise<User[]> => {
  // explicit return type
};

const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
  // event type is important
};

// Bad - redundant type annotations
const count: number = 42;                  // Unnecessary
const message: string = 'Hello';           // Unnecessary
```

### Interface vs Type

```typescript
// Use interface for object shapes that may be extended
interface User {
  id: string;
  name: string;
}

interface AdminUser extends User {
  permissions: string[];
}

// Use type for unions, tuples, or mapped types
type Status = 'idle' | 'loading' | 'success' | 'error';
type Point = [number, number];
type StringKeys<T> = { [K in keyof T]: string };

// Use type for function types
type Handler = (event: Event) => void;
type AsyncOperation<T> = () => Promise<T>;
```

### Generic Constraints

```typescript
// Good - constrained generics
interface Identifiable {
  id: string;
}

function findById<T extends Identifiable>(
  items: T[],
  id: string
): T | undefined {
  return items.find(item => item.id === id);
}

// Usage
interface User extends Identifiable {
  name: string;
}

const users: User[] = [{ id: '1', name: 'Alice' }];
const user = findById(users, '1');  // Returns User | undefined
```

---

## 🧪 Testing

### Test File Naming

```
Component.test.tsx          # Component tests
useHook.test.ts             # Hook tests
utils.test.ts               # Utility tests
```

### Testing Library Patterns

```typescript
// tests/SearchBar.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SearchBar } from '@/components/search/SearchBar';

describe('SearchBar', () => {
  const mockOnSearch = jest.fn();
  
  beforeEach(() => {
    mockOnSearch.mockClear();
  });
  
  it('renders with default placeholder', () => {
    render(<SearchBar onSearch={mockOnSearch} />);
    
    expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument();
  });
  
  it('calls onSearch when form is submitted', async () => {
    const user = userEvent.setup();
    render(<SearchBar onSearch={mockOnSearch} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'python tutorial');
    
    const button = screen.getByRole('button', { name: /search/i });
    await user.click(button);
    
    expect(mockOnSearch).toHaveBeenCalledWith('python tutorial');
  });
  
  it('displays loading state', () => {
    render(<SearchBar onSearch={mockOnSearch} isLoading />);
    
    expect(screen.getByRole('button')).toBeDisabled();
    expect(screen.getByText(/searching/i)).toBeInTheDocument();
  });
  
  it('handles keyboard shortcuts', async () => {
    const user = userEvent.setup();
    render(<SearchBar onSearch={mockOnSearch} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'test{Enter}');
    
    expect(mockOnSearch).toHaveBeenCalledWith('test');
  });
});

// Hook testing
// tests/useSearch.test.ts
import { renderHook, act, waitFor } from '@testing-library/react';
import { useSearch } from '@/hooks/useSearch';

describe('useSearch', () => {
  it('returns initial state', () => {
    const { result } = renderHook(() => useSearch());
    
    expect(result.current.query).toBe('');
    expect(result.current.results).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });
  
  it('updates query on setQuery', () => {
    const { result } = renderHook(() => useSearch());
    
    act(() => {
      result.current.setQuery('test query');
    });
    
    expect(result.current.query).toBe('test query');
  });
  
  it('debounces search calls', async () => {
    const mockSearch = jest.fn().mockResolvedValue([]);
    const { result } = renderHook(() => useSearch({ debounceMs: 300 }));
    
    act(() => {
      result.current.setQuery('test');
    });
    
    // Immediately after, search should not be called
    expect(mockSearch).not.toHaveBeenCalled();
    
    // Wait for debounce
    await waitFor(() => {
      expect(mockSearch).toHaveBeenCalledWith('test');
    }, { timeout: 400 });
  });
});
```

---

## 🚫 Anti-patterns to Avoid

### 1. Using `any` Type

```typescript
// Bad
function process(data: any): any {
  return data.value;
}

// Good
interface Data {
  value: number;
}

function process(data: Data): number {
  return data.value;
}
```

### 2. Non-null Assertions

```typescript
// Bad - unsafe non-null assertion
element!.click();
value!.toString();

// Good - proper null checking
if (element) {
  element.click();
}

// Or optional chaining
element?.click();
value?.toString();
```

### 3. Missing Dependency Arrays

```typescript
// Bad - missing dependencies
useEffect(() => {
  fetchData(query);
}, []);  // Missing 'query' dependency!

// Good - include all dependencies
useEffect(() => {
  fetchData(query);
}, [query]);

// Or disable ESLint rule with explanation
useEffect(() => {
  // Initial load only
  fetchData();
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, []);
```

### 4. Prop Drilling

```typescript
// Bad - deep prop drilling
function App() {
  const [user, setUser] = useState<User | null>(null);
  
  return <Layout user={user} setUser={setUser} />;
}

function Layout({ user, setUser }) {
  return <Header user={user} setUser={setUser} />;
}

function Header({ user, setUser }) {
  return <UserMenu user={user} setUser={setUser} />;
}

// Good - use Context for global state
const UserContext = createContext<UserContextType | null>(null);

function App() {
  const [user, setUser] = useState<User | null>(null);
  
  return (
    <UserContext.Provider value={{ user, setUser }}>
      <Layout />
    </UserContext.Provider>
  );
}

function UserMenu() {
  const { user, setUser } = useContext(UserContext)!;
  // Use user and setUser directly
}
```

### 5. Inline Styles

```typescript
// Bad - inline styles
function Component() {
  return <div style={{ backgroundColor: 'blue', padding: '10px' }} />;
}

// Good - use Tailwind classes
function Component() {
  return <div className="bg-blue-600 p-2.5" />;
}

// Good - use CSS modules for complex styles
import styles from './Component.module.css';

function Component() {
  return <div className={styles.container} />;
}
```

### 6. Index as Key

```typescript
// Bad - using index as key
function List({ items }: { items: string[] }) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={index}>{item}</li>  // Bad if items can reorder!
      ))}
    </ul>
  );
}

// Good - use unique identifier
interface Item {
  id: string;
  name: string;
}

function List({ items }: { items: Item[] }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}
```

---

## 📚 Additional Resources

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Testing Library](https://testing-library.com/docs/)

---

<p align="center">
  Write clean, typed, component-driven code. ⚛️
</p>
