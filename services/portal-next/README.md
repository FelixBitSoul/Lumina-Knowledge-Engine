# 🌐 Lumina Portal

The **Portal** is the web frontend for the Lumina Knowledge Engine - a modern, responsive interface for semantic document search and knowledge discovery.

Built with [Next.js 15](https://nextjs.org), [Tailwind CSS v4](https://tailwindcss.com), and [React 19](https://react.dev).

---

## ✨ Features

- **🔍 Semantic Search Interface**: Clean, intuitive search with real-time results
- **🎨 Modern UI/UX**: Built with Tailwind CSS and Lucide icons
- **🌓 Theme Support**: Automatic dark/light mode detection
- **⚡ High Performance**: Next.js 15 with App Router for optimal performance
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **🔌 API Integration**: Direct integration with Brain API
- **♿ Accessibility**: ARIA-compliant components and keyboard navigation
- **🌐 WebSocket Integration**: Real-time document processing notifications
- **📋 Processing Modal**: Interactive progress tracking for document uploads
- **🚀 Async Uploads**: Non-blocking file uploads with background processing
- **📁 File Management**: File listing, pagination, and deletion functionality
- **📄 Collection Management**: Create and manage vector collections

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm, yarn, or pnpm
- Brain API running (see [lumina-brain/README.md](../lumina-brain/README.md))

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local and set NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ | `http://localhost:8000` | Brain API base URL |
| `NODE_ENV` | ❌ | `development` | Environment mode |

### Example `.env.local`

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For Docker deployment, the URL should point to the Brain API service:
```bash
NEXT_PUBLIC_API_URL=http://brain-api:8000
```

---

## 📁 Project Structure

```
portal-next/
├── 📁 src/
│   ├── 📁 app/                 # Next.js 15 App Router
│   │   ├── 📄 page.tsx        # Main search interface
│   │   ├── 📄 layout.tsx      # Root layout with providers
│   │   └── 📄 globals.css     # Tailwind CSS styles
│   ├── 📁 components/         # UI components
│   │   ├── UploadModal.tsx    # File upload modal
│   │   ├── ProcessingModal.tsx # Document processing progress modal
│   │   ├── SearchBar.tsx      # Search input component
│   │   ├── SearchResults.tsx  # Search results display
│   │   ├── CollectionList.tsx # Collection selection
│   │   ├── FileManager.tsx    # File management component
│   │   ├── DocumentSidebar.tsx # Document sidebar
│   │   ├── ThemeProvider.tsx  # Theme provider component
│   │   ├── QueryClientProviderWrapper.tsx # React Query provider
│   │   ├── Chat/              # Chat components
│   │   │   ├── ChatComponent.tsx # Main chat interface
│   │   │   ├── ChatInput.tsx  # Chat input component
│   │   │   └── MessageBubble.tsx # Message bubble component
│   │   └── ui/                # Shadcn UI components
│   │       ├── badge.tsx      # Badge component
│   │       ├── button.tsx     # Button component
│   │       ├── card.tsx       # Card component
│   │       ├── input.tsx      # Input component
│   │       └── select.tsx     # Select component
│   ├── 📁 hooks/               # Custom hooks
│   │   └── useUpload.ts        # Upload and WebSocket hooks
│   ├── 📁 services/            # API services
│   │   ├── api.ts             # Search and collections API
│   │   ├── uploadAPI.ts        # Upload API service
│   │   └── chatAPI.ts          # Chat API service
│   ├── 📁 types/               # TypeScript types
│   │   └── index.ts            # Type definitions
│   ├── 📁 store/               # State management
│   │   ├── searchStore.ts       # Search state store
│   │   └── chatStore.ts         # Chat state store
│   └── 📁 lib/                 # Utility functions
│       └── utils.ts            # Common utility functions
├── 📄 package.json            # Dependencies & scripts
├── 📄 next.config.ts          # Next.js configuration
├── 📄 tailwind.config.ts      # Tailwind CSS config
├── 📄 tsconfig.json           # TypeScript config
├── 📄 postcss.config.mjs      # PostCSS configuration
├── 📄 eslint.config.mjs       # ESLint configuration
├── 📄 components.json         # Shadcn UI configuration
├── 📁 public/                 # Static assets
│   ├── next.svg               # Next.js logo
│   ├── file.svg               # File icon
│   ├── globe.svg              # Globe icon
│   ├── vercel.svg             # Vercel logo
│   └── window.svg             # Window icon
└── 📄 .gitignore              # Git ignore file
```

### Key Files

- **`src/app/page.tsx`**: Main search interface with API integration
- **`src/app/layout.tsx`**: Root layout with theme provider
- **`src/app/globals.css`**: Tailwind CSS custom styles
- **`src/components/UploadModal.tsx`**: File upload modal with progress tracking
- **`src/components/ProcessingModal.tsx`**: Real-time document processing progress modal
- **`src/components/SearchBar.tsx`**: Search input component with debounce
- **`src/components/SearchResults.tsx`**: Search results display with pagination
- **`src/components/CollectionList.tsx`**: Collection selection component
- **`src/components/FileManager.tsx`**: File management component with pagination
- **`src/components/Chat/ChatComponent.tsx`**: Main chat interface
- **`src/hooks/useUpload.ts`**: Custom hook for upload and WebSocket handling
- **`src/services/api.ts`**: Search and collections API integration
- **`src/services/uploadAPI.ts`**: Upload API service integration
- **`src/services/chatAPI.ts`**: Chat API service integration
- **`src/store/searchStore.ts`**: Search state management
- **`src/store/chatStore.ts`**: Chat state management
- **`src/types/index.ts`**: TypeScript type definitions
- **`src/lib/utils.ts`**: Common utility functions
- **`next.config.ts`**: Next.js and build configuration

---

## 🔌 API Integration

The Portal connects to the Brain API for:

- **Semantic Search**: `GET /search?query={query}&page_size={size}&page={num}&collection={collection}&title={title}&domain={domain}&start_time={start_time}&end_time={end_time}`
- **Get Collections**: `GET /collections`
- **Create Collection**: `POST /collections` with name and description
- **Health Check**: `GET /health`
- **File Upload**: `POST /upload` with file multipart/form-data (file, category, collection)
- **Task Status**: `GET /upload/tasks/{task_id}`
- **List Files**: `GET /documents?collection={collection}&limit={limit}&start_after={marker}`
- **Document Preview**: `GET /documents/{file_id}/preview-url?filename={filename}&expiry={expiry}`
- **Document Delete**: `DELETE /documents/{file_id}?collection={collection}&filename={filename}`
- **WebSocket Notifications**: `WebSocket /ws/{file_id}`
- **Chat API**: `POST /chat` with message and context

### Search Flow

```
User Input ──▶ Portal ──▶ Brain API ──▶ Qdrant
                │                          │
                └───────── Results ◀───────┘
```

### TypeScript Types

```typescript
// Search-related types
export interface SearchFilters {
  title?: string;      // Filter by title
  domain?: string;     // Filter by domain
  start_time?: string; // Filter by start time (ISO format)
  end_time?: string;   // Filter by end time (ISO format)
}

export interface SearchParams {
  query: string;
  collection?: string;
  filters?: SearchFilters;
  limit?: number;
}

export interface SearchResultItem {
  score: number;       // Relevance score (0-1)
  title: string;       // Document title
  url: string;         // Source URL
  domain: string;      // Document domain
  content: string;     // Content preview
  updated_at: string;  // Last update time (ISO format)
}

export interface SearchResponse {
  query: string;
  page_size: number;
  page: number;
  offset: number;
  collection: string;
  filters: SearchFilters | null;
  latency_ms: number;
  results: SearchResultItem[];
}

// Upload-related types
export interface UploadResponse {
  task_id: string;
  file_id: string;
  file_name: string;
  category: string;
  collection: string;
  status: string;
  websocket_url: string;
  message: string;
}

export interface TaskStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  total?: number;
  current_step?: string;
  result?: {
    file_id: string;
    filename: string;
    chunks_created: number;
    status: string;
  };
  error?: string;
  message?: string;
}

export interface WebSocketMessage {
  file_id: string;
  status: 'connected' | 'processing' | 'completed' | 'failed';
  progress?: number;
  total?: number;
  step?: string;
  error?: string;
  filename?: string;
  chunks_created?: number;
  collection?: string;
  timestamp?: string;
}
```

---

## 🛠 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Create production build |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint for code quality |
| `npm run format` | Format code with Prettier |

---

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

---

## 📦 Dependencies

### Core
- **next**: 15.0.2 - React framework
- **react**: 19.0.0 - UI library
- **react-dom**: 19.0.0 - DOM rendering
- **@tanstack/react-query**: ^5.28.9 - Data fetching
- **zustand**: ^4.5.2 - State management
- **shadcn**: ^4.1.0 - UI components
- **class-variance-authority**: ^0.7.1 - Type-safe component variants
- **clsx**: ^2.1.1 - Class name utility
- **next-themes**: ^0.4.6 - Theme management
- **radix-ui**: ^1.4.3 - UI primitives
- **tw-animate-css**: ^1.4.0 - Animation utilities

### Styling
- **tailwindcss**: ^4 - Utility-first CSS
- **lucide-react**: 0.577.0 - Icon library
- **tailwind-merge**: ^3.5.0 - Class merging

### Development
- **typescript**: ^5 - Type safety
- **eslint**: ^9 - Code linting
- **@types/react**: ^19.0.0 - React types
- **@types/react-dom**: ^19.0.0 - React DOM types
- **@tailwindcss/postcss**: ^4 - Tailwind CSS PostCSS plugin
- **babel-plugin-react-compiler**: 1.0.0 - React compiler
- **eslint-config-next**: 15.0.2 - ESLint Next.js config

See `package.json` for complete dependency list.

---

## 🐳 Docker Support

### Build Docker Image

```bash
# Build image
docker build -t lumina/portal:latest .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://brain-api:8000 \
  lumina/portal:latest
```

The Dockerfile supports multi-stage builds for optimal image size.

---

## 🔗 Related Documentation

- **Portal Integration Guide**: [docs/api/portal-integration.md](../../docs/api/portal-integration.md)
- **Brain API Docs**: [docs/api/brain-api.md](../../docs/api/brain-api.md)
- **Deployment Guide**: [docs/deployment/docker-deployment.md](../../docs/deployment/docker-deployment.md)

---

## 🤝 Contributing

1. Follow the [AI Collaboration Guide](../../AI_COLLABORATION_GUIDE.md)
2. Ensure code passes linting: `npm run lint`
3. Update documentation for any changes
4. Test on multiple browsers

---

## 📄 License

This project is part of the Lumina Knowledge Engine and is licensed under the MIT License.

---

<p align="center">
  Part of <a href="../../README.md">Lumina Knowledge Engine</a> 🔍
</p>
