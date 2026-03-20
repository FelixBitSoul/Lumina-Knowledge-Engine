# Contributing to Lumina Knowledge Engine

Thank you for your interest in contributing to Lumina Knowledge Engine! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)
- [Questions and Support](#questions-and-support)

---

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our commitment to:

- **Be respectful**: Treat everyone with respect. Healthy debate is encouraged, but harassment is not tolerated.
- **Be constructive**: Provide constructive feedback and be open to receiving it.
- **Be collaborative**: Work together towards the best possible solutions.
- **Focus on what's best for the community**: Prioritize the project's goals over personal preferences.

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Go**: 1.22+ ([Download](https://golang.org/dl/))
- **Python**: 3.11+ ([Download](https://python.org/downloads/))
- **Node.js**: 18+ ([Download](https://nodejs.org/))
- **Docker**: 20.10+ ([Download](https://docs.docker.com/get-docker/))
- **Git**: Latest version

### Development Environment Setup

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/lumina-knowledge-engine.git
cd lumina-knowledge-engine

# 3. Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/lumina-knowledge-engine.git

# 4. Create a feature branch
git checkout -b feature/your-feature-name

# 5. Set up development environment
make install-dev  # Or see individual service READMEs
```

---

## 🔄 Development Workflow

### 1. Branch Naming Convention

Use descriptive branch names with the following prefixes:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feature/` | New feature | `feature/semantic-search-enhancement` |
| `bugfix/` | Bug fix | `bugfix/crawler-timeout-handling` |
| `hotfix/` | Critical fix | `hotfix/security-patch` |
| `docs/` | Documentation | `docs/api-examples` |
| `refactor/` | Code refactoring | `refactor/crawler-async` |
| `test/` | Test improvements | `test/brain-api-coverage` |

### 2. Keeping Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Checkout your main branch
git checkout main

# Merge upstream changes
git merge upstream/main

# Push to your fork
git push origin main
```

### 3. Development Cycle

```
1. Create feature branch from main
2. Make changes following coding standards
3. Write/update tests
4. Update documentation
5. Run linters and formatters
6. Commit with meaningful messages
7. Push to your fork
8. Create Pull Request
```

---

## 💻 Coding Standards

### Language-Specific Guidelines

We maintain separate style guides for each language:

- **Go**: [GO_STYLE_GUIDE.md](GO_STYLE_GUIDE.md)
  - Formatting: `gofmt`, `goimports`
  - Linting: `golangci-lint`

- **Python**: [PYTHON_STYLE_GUIDE.md](PYTHON_STYLE_GUIDE.md)
  - Formatting: `black`, `isort`
  - Linting: `flake8`, `mypy`

- **TypeScript/JavaScript**: [TYPESCRIPT_STYLE_GUIDE.md](TYPESCRIPT_STYLE_GUIDE.md)
  - Formatting: `prettier`
  - Linting: `eslint`

### General Principles

1. **DRY (Don't Repeat Yourself)**: Avoid code duplication
2. **KISS (Keep It Simple, Stupid)**: Prefer simple solutions
3. **Single Responsibility**: Each function/class should do one thing
4. **Clear Naming**: Use descriptive names that explain intent
5. **Comments**: Explain "why", not "what" (code should be self-documenting)

### Pre-commit Checks

Always run these before committing:

```bash
# Go
make lint-go
make test-go

# Python
make lint-python
make test-python

# TypeScript
make lint-ts
make test-ts

# Or run all
make pre-commit
```

---

## 📝 Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes (formatting, no logic change) |
| `refactor` | Code refactoring |
| `perf` | Performance improvements |
| `test` | Test additions or corrections |
| `chore` | Build process or auxiliary tool changes |
| `ci` | CI/CD changes |

### Scopes

| Scope | Description |
|-------|-------------|
| `crawler` | Crawler service (Go) |
| `brain` | Brain API service (Python) |
| `portal` | Portal frontend (Next.js) |
| `docs` | Documentation |
| `deploy` | Deployment configurations |
| `api` | API specifications |

### Examples

```bash
# Good commit messages
git commit -m "feat(crawler): add rate limiting per domain"
git commit -m "fix(brain): handle empty search queries gracefully"
git commit -m "docs(api): update OpenAPI spec for v2 endpoints"
git commit -m "refactor(portal): extract search hook for reusability"
git commit -m "test(crawler): add integration tests for retry logic"
git commit -m "perf(brain): cache embedding model in memory"
git commit -m "chore(deploy): update docker-compose volumes"

# Bad commit messages (avoid these)
git commit -m "fix bug"                           # Too vague
git commit -m "updates"                          # No type/scope
git commit -m "feat: something"                  # No scope for multi-service repo
git commit -m "WIP"                              # Work in progress
```

### Commit Body

For complex changes, include a body explaining:
- What changed and why
- Any breaking changes
- Related issue numbers (e.g., `Closes #123`)

---

## 🔀 Pull Request Process

### Before Creating a PR

1. **Update your branch** with latest upstream changes
2. **Run all tests** and ensure they pass
3. **Run linters** and fix any issues
4. **Update documentation** if needed
5. **Verify changes** work in Docker environment

### PR Template

Use this format for PR descriptions:

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Related Issues
Closes #123
Related to #456

## Testing
Describe the tests you ran and how to reproduce them.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have tested my changes in the Docker environment
```

### PR Review Process

1. **Automated checks** must pass (CI/CD, linting, tests)
2. **Code review** by at least one maintainer
3. **Documentation review** if docs are changed
4. **Approval** and merge by maintainer

### Review Criteria

Reviewers will check for:

- ✅ Code quality and correctness
- ✅ Test coverage
- ✅ Documentation updates
- ✅ Performance implications
- ✅ Security considerations
- ✅ Backward compatibility

---

## 🧪 Testing

### Test Coverage Requirements

- **New features**: Must include tests (unit + integration)
- **Bug fixes**: Must include regression test
- **Refactoring**: Existing tests must still pass

### Minimum Coverage

| Service | Minimum Coverage |
|---------|-----------------|
| `crawler-go` | 70% |
| `brain-py` | 75% |
| `portal-next` | 60% |

### Running Tests

```bash
# Run all tests
make test

# Run specific service tests
make test-crawler
make test-brain
make test-portal

# Run with coverage
make test-coverage
```

---

## 📚 Documentation

### When to Update Documentation

Update documentation when you:

- Add or modify API endpoints
- Change configuration options
- Add new environment variables
- Modify architecture or data flow
- Change deployment procedures
- Add new features or capabilities

### Documentation Files to Update

| Change Type | Files to Update |
|-------------|-----------------|
| API changes | `docs/api/brain-api.md`, `docs/api/openapi/*.yaml` |
| Config changes | `docs/api/crawler-config.md`, service READMEs |
| Architecture | `docs/architecture/*.md` |
| Deployment | `docs/deployment/*.md` |
| New features | Relevant docs + root README |

See [AI_COLLABORATION_GUIDE.md](AI_COLLABORATION_GUIDE.md) for detailed documentation requirements.

---

## 🐳 Docker Development

### Local Docker Testing

```bash
# Build all images
docker-compose build

# Run services locally
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Run tests in Docker
docker-compose -f docker-compose.test.yaml up
```

### Testing Your Changes

Always verify your changes work in the Docker environment:

```bash
# Start services
docker-compose up -d

# Wait for health checks
curl http://localhost:8000/health
curl http://localhost:3000
curl http://localhost:6333/health

# Test your specific changes
# (add your test commands here)

# Clean up
docker-compose down
```

---

## ❓ Questions and Support

### Getting Help

- **Documentation**: Check [docs/](docs/) directory
- **Issues**: Search [existing issues](https://github.com/FelixBitSoul/lumina-knowledge-engine/issues)
- **Discussions**: Use [GitHub Discussions](https://github.com/FelixBitSoul/lumina-knowledge-engine/discussions)

### Reporting Bugs

Use the bug report template when creating issues:

```markdown
**Description**
Clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Environment**
- OS: [e.g., Windows 10, macOS 12]
- Go version: [e.g., 1.22]
- Python version: [e.g., 3.11]
- Node version: [e.g., 18.12]
- Docker version: [e.g., 20.10]

**Additional Context**
Any other relevant information.
```

### Requesting Features

Use the feature request template:

```markdown
**Feature Description**
Clear description of the proposed feature.

**Problem Statement**
What problem does this solve?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches you considered.

**Additional Context**
Any other relevant information.
```

---

## 🙏 Recognition

Contributors will be recognized in our:

- **CHANGELOG.md** for significant contributions
- **README.md** contributors section
- Release notes for major contributions

---

## 📄 License

By contributing to Lumina Knowledge Engine, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

<p align="center">
  Thank you for contributing to Lumina Knowledge Engine! 🔍
</p>
