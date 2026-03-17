# AI Collaboration Guide

This document defines the collaboration rules and conventions for AI assistants working on the Lumina Knowledge Engine project.

## 📋 Core Principles

### 1. Documentation-First Development

**Rule**: When making code changes that affect functionality, configuration, or architecture, you **MUST** update the corresponding documentation.

#### When to Update Documentation

Update documentation when modifying:
- **Code**: API endpoints, function signatures, data models
- **Configuration**: Config files, environment variables, deployment settings
- **Architecture**: Service structure, data flow, component relationships
- **Dependencies**: Adding/removing libraries, changing versions
- **Behavior**: Changes to how the system works or responds

#### Documentation to Update

| Change Type | Documentation Files |
|-------------|---------------------|
| API changes | `docs/api/*.md`, `docs/api/openapi/*.yaml` |
| Configuration changes | `docs/api/crawler-config.md`, service READMEs |
| Architecture changes | `docs/architecture/*.md` |
| Deployment changes | `docs/deployment/*.md` |
| New features | Relevant docs + `docs/README.md` |

### 2. Change-Documentation Mapping

Always update these document types for corresponding changes:

```yaml
Code Changes:
  - API endpoints → API docs + OpenAPI specs
  - Config options → Configuration reference
  - New services → Architecture docs + Deployment guides
  - Dependencies → Setup guides + Requirements files
  - Error handling → API docs + Troubleshooting guides
```

### 3. Documentation Quality Standards

- **Accuracy**: Documentation must match the actual code behavior
- **Completeness**: Include examples, error cases, and edge cases
- **Clarity**: Use clear language and consistent terminology
- **Currency**: Keep version numbers and requirements up to date

## 🔄 AI Assistant Workflow

### Before Making Changes

1. **Assess Impact**: Determine if the change affects user-facing behavior
2. **Identify Docs**: Find which documentation files need updates
3. **Plan Updates**: Include documentation updates in your change plan

### During Implementation

1. **Code First**: Implement the code changes
2. **Update Docs**: Immediately update affected documentation
3. **Verify Consistency**: Ensure code and docs are in sync

### Before Completion

1. **Cross-Reference**: Check that code examples in docs match actual code
2. **Link Updates**: Ensure all internal links are valid
3. **Version Alignment**: Update version references if applicable

## 📚 Documentation Structure

```
docs/
├── README.md                    # Documentation overview
├── api/                         # API documentation
│   ├── README.md
│   ├── brain-api.md            # Brain API endpoints
│   ├── crawler-config.md       # Crawler configuration
│   ├── portal-integration.md   # Frontend integration
│   └── openapi/                # OpenAPI specifications
├── architecture/               # System architecture
│   ├── README.md
│   ├── system-overview.md
│   ├── component-details.md
│   ├── data-flow.md
│   ├── api-contracts.md
│   ├── technical-decisions.md
│   └── performance-characteristics.md
└── deployment/                 # Deployment guides
    ├── README.md
    ├── local-setup.md
    ├── docker-deployment.md
    └── cloud-deployment.md
```

## 🎯 Specific Rules

### API Changes

When modifying API endpoints in `services/brain-py/main.py`:

1. Update `docs/api/brain-api.md`
2. Update `docs/api/openapi/brain-api.yaml`
3. Update example requests/responses
4. Document any new error codes

### Configuration Changes

When modifying configuration in `services/crawler-go/crawler-config.yaml` or related structs:

1. Update `docs/api/crawler-config.md`
2. Update configuration examples
3. Document new fields and validation rules
4. Update default values table

### Architecture Changes

When modifying service structure or data flow:

1. Update relevant architecture docs
2. Update system diagrams
3. Document new components or relationships
4. Update performance characteristics if applicable

### Deployment Changes

When modifying deployment configurations:

1. Update relevant deployment guides
2. Update docker-compose files
3. Update environment variable documentation
4. Update troubleshooting sections

## ✅ Checklist for AI Assistants

Before marking a task as complete:

- [ ] Code changes are implemented and tested
- [ ] Affected documentation is identified
- [ ] Documentation is updated to match code
- [ ] Examples in docs match actual behavior
- [ ] Links and references are valid
- [ ] Version numbers are updated if needed
- [ ] New features are documented with examples

## 📝 Example Scenarios

### Scenario 1: Adding New API Endpoint

```python
# services/brain-py/main.py
@app.get("/stats")
async def get_stats():
    return {"total_documents": 1000}
```

Required documentation updates:
1. Add endpoint to `docs/api/brain-api.md`
2. Add schema to `docs/api/openapi/brain-api.yaml`
3. Add example response
4. Update API overview if needed

### Scenario 2: Modifying Configuration

```yaml
# services/crawler-go/crawler-config.yaml
tasks:
  - name: "new-crawler"
    new_field: "value"  # Added new field
```

Required documentation updates:
1. Update field specification in `docs/api/crawler-config.md`
2. Add validation rules documentation
3. Update configuration examples
4. Document default values

### Scenario 3: Architecture Change

Adding a new service component:

Required documentation updates:
1. Update `docs/architecture/system-overview.md`
2. Add component details to `docs/architecture/component-details.md`
3. Update data flow diagrams in `docs/architecture/data-flow.md`
4. Update deployment guides

## 🚨 Common Mistakes to Avoid

1. **Inconsistent Examples**: Code examples in docs don't match actual code
2. **Missing Error Documentation**: New error codes not documented
3. **Outdated Configuration**: Config docs don't match current options
4. **Broken Links**: Internal documentation links point to moved/renamed files
5. **Version Drift**: Documentation references old versions

## 🔧 Tools and Automation

### Validation Commands

```bash
# Check for broken links in docs
# Use: markdown-link-check or similar tools

# Validate OpenAPI specs
# Use: swagger-codegen validate -i docs/api/openapi/brain-api.yaml

# Check markdown formatting
# Use: markdownlint docs/
```

### Documentation Generation

When possible, generate documentation from code:
- API docs from OpenAPI specs
- Type documentation from code comments
- Configuration docs from JSON Schema

## 📞 Escalation

If uncertain about documentation requirements:

1. **Ask the user**: "Should I update the API documentation for this change?"
2. **Default to documentation**: When in doubt, document the change
3. **Leave TODOs**: Add `TODO:` comments for documentation that needs review

## 🎓 Best Practices

1. **Proactive Documentation**: Document as you code, not after
2. **User Perspective**: Write docs for someone using the system for the first time
3. **Complete Examples**: Include working examples, not just syntax
4. **Error Scenarios**: Document what can go wrong and how to handle it
5. **Keep It Simple**: Avoid unnecessary complexity in explanations

---

## � Technical Standards and Guidelines

This project maintains comprehensive technical standards and style guides for all programming languages and processes.

### Core Guidelines

| Document | Purpose | Applies To |
|----------|---------|------------|
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Contribution workflow, PR process, testing requirements | All contributors |
| **[TECH_STACK.md](docs/guidelines/TECH_STACK.md)** | Technology choices, version requirements, architecture decisions | All services |
| **[PRD.md](docs/PRD.md)** | Product requirements, features, roadmap | Product team, developers |

### Language-Specific Style Guides

When writing or modifying code, follow the appropriate style guide:

| Language | Style Guide | Key Tools |
|----------|-------------|-----------|
| **Go** | [GO_STYLE_GUIDE.md](docs/guidelines/GO_STYLE_GUIDE.md) | `gofmt`, `golangci-lint` |
| **Python** | [PYTHON_STYLE_GUIDE.md](docs/guidelines/PYTHON_STYLE_GUIDE.md) | `black`, `isort`, `flake8`, `mypy` |
| **TypeScript/JavaScript** | [TYPESCRIPT_STYLE_GUIDE.md](docs/guidelines/TYPESCRIPT_STYLE_GUIDE.md) | `prettier`, `eslint`, `tsc` |

### AI Assistant Guidelines

**When modifying code:**

1. **Read the relevant style guide first** - Before writing Go/Python/TypeScript code, review the corresponding style guide
2. **Apply formatting automatically** - Use the specified tools (Black, Prettier, gofmt) to ensure consistent formatting
3. **Follow naming conventions** - Use the naming standards defined in each style guide
4. **Include proper types** - Add type annotations (Python) or ensure strict TypeScript
5. **Write documentation** - Follow the documentation standards for each language

### Service-Specific Patterns

Each service has established patterns that should be followed:

- **Crawler (Go)**: See [services/crawler-go/README.md](services/crawler-go/README.md)
- **Brain API (Python/FastAPI)**: See [services/brain-py/README.md](services/brain-py/README.md)
- **Portal (Next.js/TypeScript)**: See [services/portal-next/README.md](services/portal-next/README.md)

---

## �� Quick Reference

| If you modify... | Then update... |
|------------------|----------------|
| `services/brain-py/*.py` | `docs/api/brain-api.md`, `docs/api/openapi/*.yaml` |
| `services/crawler-go/*.go` | `docs/api/crawler-config.md` |
| `services/portal-next/*.tsx` | `docs/api/portal-integration.md` |
| `deployments/*` | `docs/deployment/*.md` |
| `README.md` | Check if `docs/README.md` needs updates |
| Any config files | Corresponding configuration documentation |

**Remember**: Good documentation is as important as good code. When in doubt, document it!
