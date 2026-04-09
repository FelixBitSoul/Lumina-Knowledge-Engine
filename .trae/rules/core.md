# Core Coding Principles

## 1. Code Extensibility (可抽取性)

### 1.1 Modular Design
- **Single Responsibility Principle**: Each module or function should have only one reason to change.
- **High Cohesion**: Related functionality should be grouped together.
- **Low Coupling**: Modules should be loosely coupled to minimize dependencies.

### 1.2 Reusability (可复用性)
- **Abstract Common Logic**: Extract repeated code into reusable functions or classes.
- **Parameterization**: Design functions to be flexible through parameters rather than hardcoding values.
- **DRY Principle**: Don't Repeat Yourself. Avoid duplicating code across the codebase.

## 2. General Best Practices

- **Keep It Simple**: Prefer simple solutions over complex ones.
- **Write Readable Code**: Code should be easy to understand for humans.
- **Test Early and Often**: Write tests for new functionality and run them regularly.
- **Refactor When Necessary**: Improve code quality through regular refactoring.
- **Use Version Control**: Commit changes frequently with clear commit messages.
- **Document Decisions**: Record important design decisions and their rationale.
- **Collaborate Effectively**: Communicate with team members about code changes.
- **Stay Updated**: Keep dependencies and knowledge up to date.

## 3. Code Quality Metrics

- **Cyclomatic Complexity**: Keep complexity low (maximum 10).
- **Test Coverage**: Maintain adequate test coverage for critical functionality.
- **Code Duplication**: Minimize duplicated code through abstraction.
- **Code Smells**: Identify and fix code smells regularly.
- **Technical Debt**: Address technical debt as part of regular development.

## 4. Development Workflow

- **Write Tests First**: Follow test-driven development where appropriate.
- **Code Reviews**: Conduct code reviews for all changes.
- **Continuous Integration**: Use CI/CD to enforce quality standards.
- **Automated Testing**: Automate testing to catch regressions early.
- **Performance Monitoring**: Monitor application performance in production.

## 5. Team Collaboration

- **Shared Understanding**: Ensure all team members understand the codebase and its architecture.
- **Consistent Practices**: Follow consistent coding practices across the team.
- **Knowledge Sharing**: Share knowledge through documentation and pair programming.
- **Constructive Feedback**: Provide constructive feedback during code reviews.
- **Learning Culture**: Encourage continuous learning and improvement.