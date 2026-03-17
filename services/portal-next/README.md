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

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm, yarn, or pnpm
- Brain API running (see [brain-py/README.md](../brain-py/README.md))

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
│   └── 📄 ...
├── 📄 package.json            # Dependencies & scripts
├── 📄 next.config.ts          # Next.js configuration
├── 📄 tailwind.config.ts      # Tailwind CSS config
└── 📄 tsconfig.json           # TypeScript config
```

### Key Files

- **`src/app/page.tsx`**: Main search interface with API integration
- **`src/app/layout.tsx`**: Root layout with theme provider
- **`src/app/globals.css`**: Tailwind CSS custom styles
- **`next.config.ts`**: Next.js and build configuration

---

## 🔌 API Integration

The Portal connects to the Brain API for:

- **Semantic Search**: `GET /search?query={query}&limit={limit}`
- **Health Check**: `GET /health`

### Search Flow

```
User Input ──▶ Portal ──▶ Brain API ──▶ Qdrant
                │                          │
                └───────── Results ◀───────┘
```

### TypeScript Types

```typescript
interface SearchResult {
  score: number;       // Relevance score (0-1)
  title: string;       // Document title
  url: string;         // Source URL
  content: string;      // Content preview
}

interface SearchResponse {
  query: string;
  results: SearchResult[];
  latency_ms: number;
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
- **next**: ^15.0.0 - React framework
- **react**: ^19.0.0 - UI library
- **react-dom**: ^19.0.0 - DOM rendering

### Styling
- **tailwindcss**: ^4.0.0 - Utility-first CSS
- **lucide-react**: Latest - Icon library

### Development
- **typescript**: ^5.0.0 - Type safety
- **eslint**: ^9.0.0 - Code linting
- **@types/react**: ^19.0.0 - React types

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
