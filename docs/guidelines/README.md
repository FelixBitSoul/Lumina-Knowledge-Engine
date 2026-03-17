# Lumina Knowledge Engine - Technical Guidelines

This directory contains comprehensive technical standards, style guides, and development guidelines for the Lumina Knowledge Engine project.

---

## 📋 Available Guidelines

### Core Project Standards

| Document | Description | Audience |
|----------|-------------|----------|
| **[TECH_STACK.md](TECH_STACK.md)** | Technology choices, architecture decisions, version requirements | All developers |
| **[PRD.md](../PRD.md)** | Product Requirements Document - features, user stories, roadmap | Product team, developers |

### Language-Specific Style Guides

| Language | Document | Key Topics |
|----------|----------|------------|
| **Go** | [GO_STYLE_GUIDE.md](GO_STYLE_GUIDE.md) | Naming conventions, error handling, concurrency patterns, project structure (Crawler service) |
| **Python** | [PYTHON_STYLE_GUIDE.md](PYTHON_STYLE_GUIDE.md) | Type annotations, FastAPI patterns, Pydantic models, testing (Brain API service) |
| **TypeScript** | [TYPESCRIPT_STYLE_GUIDE.md](TYPESCRIPT_STYLE_GUIDE.md) | React/Next.js patterns, Tailwind usage, component design (Portal frontend) |

---

## 🚀 Quick Start

### For New Contributors

1. Start with **[CONTRIBUTING.md](../../CONTRIBUTING.md)** for contribution workflow
2. Review **[TECH_STACK.md](TECH_STACK.md)** to understand technology choices
3. Read the relevant language style guide before writing code
4. Check **[AI_COLLABORATION_GUIDE.md](../../AI_COLLABORATION_GUIDE.md)** for documentation requirements

### For Code Reviewers

- Ensure code follows the appropriate style guide
- Verify all changes are properly documented
- Check that tests follow testing standards

---

## 🛠 Tooling Configuration

Each style guide includes configuration for:

- **Formatters**: `gofmt`, `black`, `prettier`
- **Linters**: `golangci-lint`, `flake8`, `eslint`
- **Type Checkers**: `mypy`, `tsc`
- **CI/CD Integration**: GitHub Actions, pre-commit hooks

---

## 📝 Updating Guidelines

When modifying these guidelines:

1. Follow the process defined in [AI_COLLABORATION_GUIDE.md](../../AI_COLLABORATION_GUIDE.md)
2. Notify the team of significant changes
3. Update version history below

---

## 🔄 Version History

| Date | Changes |
|------|---------|
| 2024-03 | Initial creation of style guides and technical standards |

---

<p align="center">
  Consistent code, better collaboration. 🎯
</p>
