# Module & Directory Organization

## 1. Logical Grouping

### 1.1 Functionality-Based Structure
- **Organize by Functionality**: Group code by functionality rather than file type.
- **Domain-Driven Design**: Align code organization with business domains.
- **Feature-Based Modules**: Create modules around features rather than technical concerns.

### 1.2 Layered Architecture
- **Separation of Concerns**: Separate code into distinct layers:
  - **API Layer**: Handles HTTP requests and responses
  - **Service Layer**: Contains business logic
  - **Data Access Layer**: Handles data persistence
  - **Infrastructure Layer**: Provides cross-cutting concerns

### 1.3 Clear Interfaces
- **Define Explicit Interfaces**: Create clear boundaries between modules.
- **Encapsulation**: Hide implementation details within modules.
- **Dependency Injection**: Use dependency injection to manage module dependencies.

## 2. Directory Structure

### 2.1 Project Layout

#### Backend (Python/FastAPI)
```
services/lumina-brain/
├── src/
│   ├── lumina_brain/
│   │   ├── api/            # API endpoints
│   │   ├── core/            # Core functionality
│   │   │   ├── models/      # Data models
│   │   │   ├── services/    # Business logic
│   │   │   └── utils/       # Utility functions
│   │   ├── config/          # Configuration
│   │   └── tasks/           # Celery tasks
│   └── main.py              # Application entry point
├── tests/                   # Test files
├── requirements.txt         # Dependencies
└── Dockerfile               # Docker configuration
```

#### Frontend (Next.js/React)
```
services/portal-next/
├── src/
│   ├── app/                 # Next.js app directory
│   ├── components/          # React components
│   ├── services/            # API services
│   ├── hooks/               # Custom hooks
│   └── utils/               # Utility functions
├── public/                  # Static files
├── package.json             # Dependencies
└── Dockerfile               # Docker configuration
```

#### Crawler (Go)
```
services/crawler/
├── cmd/                     # Command-line tools
├── internal/                # Internal packages
│   ├── crawler/             # Crawler logic
│   ├── parser/              # Content parser
│   └── storage/             # Storage integration
├── go.mod                   # Go modules
└── Dockerfile               # Docker configuration
```

### 2.2 Directory Naming
- **Use Descriptive Names**: Choose directory names that reflect their purpose.
- **Consistent Naming**: Use consistent naming conventions across the project.
- **Avoid Deep Nesting**: Keep directory structures shallow (maximum 3-4 levels).
- **Flat Structure**: Prefer flat directory structures over deeply nested ones.

## 3. Module Organization

### 3.1 Python Modules
- **Package Structure**: Use Python packages with `__init__.py` files.
- **Relative Imports**: Use relative imports for modules within the same package.
- **Circular Dependencies**: Avoid circular dependencies between modules.
- **Module Size**: Keep modules small and focused on a single responsibility.

### 3.2 TypeScript/JavaScript Modules
- **ES Modules**: Use ES modules (import/export) for code organization.
- **Barrel Exports**: Use barrel files (`index.ts`) to export multiple modules.
- **Module Boundaries**: Define clear boundaries between modules.
- **Lazy Loading**: Use lazy loading for large modules when appropriate.

### 3.3 Go Packages
- **Package Structure**: Organize code into logical packages.
- **Package Naming**: Use short, descriptive package names.
- **Dependency Management**: Use Go modules for dependency management.
- **Interface-Based Design**: Use interfaces to define package boundaries.

## 4. Best Practices

- **Keep Related Code Together**: Group related functionality in the same directory.
- **Separate Test Files**: Keep test files separate from production code.
- **Configuration Management**: Store configuration in dedicated files or directories.
- **Documentation**: Include README files for complex modules.
- **Version Control**: Use `.gitignore` to exclude unnecessary files from version control.
- **Continuous Integration**: Configure CI/CD to validate code organization.

## 5. Anti-Patterns

- **Flat Directory Structure**: Avoid putting all files in a single directory.
- **Deeply Nested Directories**: Avoid excessively deep directory structures.
- **Mixed Concerns**: Avoid mixing different concerns in the same directory.
- **Inconsistent Naming**: Avoid inconsistent naming conventions across directories.
- **Unnecessary Complexity**: Avoid over-engineering directory structures.