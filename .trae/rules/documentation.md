# Documentation & Commenting Standards

## 1. Commenting Guidelines

### 1.1 General Principles
- **Use English**: All comments and documentation must be in English.
- **Explain Why, Not What**: Focus on explaining the reasoning behind code decisions.
- **Keep Comments Updated**: Ensure comments remain accurate as code evolves.
- **Avoid Redundant Comments**: Don't comment on self-evident code.
- **Use Clear Language**: Write comments in clear, concise language.

### 1.2 Comment Types
- **Inline Comments**: Use inline comments sparingly for complex or non-obvious code.
- **Block Comments**: Use block comments for longer explanations or documentation.
- **Docstrings**: Use docstrings for functions, classes, and modules.
- **TODO Comments**: Use TODO comments for future work or incomplete functionality.
- **FIXME Comments**: Use FIXME comments for known issues or bugs.

### 1.3 Comment Formatting
- **Consistent Format**: Use consistent formatting for comments.
- **Proper Spacing**: Add proper spacing around comments.
- **Indentation**: Indent comments to match the code they describe.
- **Line Length**: Keep comment lines to a reasonable length (80-120 characters).

## 2. Documentation

### 2.1 Module Documentation
- **Module-Level Docstrings**: Provide high-level documentation for each module.
- **Purpose**: Explain the module's purpose and functionality.
- **Dependencies**: Document module dependencies.
- **Usage Examples**: Include usage examples where appropriate.

### 2.2 Function Documentation
- **Function Docstrings**: Document function parameters, return values, and side effects.
- **Parameters**: Document each parameter's type and purpose.
- **Return Values**: Document the function's return values and their types.
- **Exceptions**: Document any exceptions the function may raise.
- **Side Effects**: Document any side effects the function may have.

### 2.3 API Documentation
- **API Endpoints**: Document API endpoints, parameters, and responses.
- **Request/Response Formats**: Document request and response formats.
- **Authentication**: Document authentication requirements.
- **Rate Limiting**: Document rate limiting policies.
- **Error Handling**: Document error responses and status codes.

### 2.4 Project Documentation
- **README.md**: Provide a comprehensive README.md file for the project.
- **Installation Guide**: Document how to install and set up the project.
- **Usage Guide**: Document how to use the project.
- **API Documentation**: Provide comprehensive API documentation.
- **Architecture Documentation**: Document the project's architecture and design decisions.
- **Contributing Guidelines**: Document how to contribute to the project.

## 3. Language-Specific Documentation

### 3.1 Python
- **PEP 257**: Follow PEP 257 for docstring conventions.
- **Docstring Format**: Use reStructuredText or Google-style docstrings.
- **Type Hints**: Use type hints for function parameters and return values.
- **Sphinx**: Use Sphinx for generating documentation.

### 3.2 TypeScript/JavaScript
- **JSDoc**: Use JSDoc for function and class documentation.
- **TypeScript Interfaces**: Document TypeScript interfaces and types.
- **React Components**: Document React components and their props.
- **ESDoc**: Use ESDoc or TypeDoc for generating documentation.

### 3.3 Go
- **GoDoc**: Follow GoDoc conventions for documentation.
- **Package Comments**: Provide package-level comments.
- **Function Comments**: Document functions with clear comments.
- **Parameter Documentation**: Document parameters and return values.

## 4. Best Practices

- **Write Documentation Early**: Document code as you write it, not as an afterthought.
- **Keep Documentation Updated**: Update documentation when code changes.
- **Use Examples**: Include examples in documentation to clarify usage.
- **Be Consistent**: Use consistent documentation styles across the project.
- **Review Documentation**: Review documentation as part of code reviews.
- **Automate Documentation**: Use tools to generate documentation from code.
- **Document Edge Cases**: Document edge cases and limitations.
- **Use Diagrams**: Use diagrams to illustrate complex concepts.

## 5. Anti-Patterns

- **Outdated Documentation**: Documentation that doesn't match the code.
- **Excessive Comments**: Too many comments that clutter the code.
- **Redundant Comments**: Comments that repeat what the code already says.
- **Vague Comments**: Comments that don't clearly explain the code.
- **Missing Documentation**: Important code that isn't documented.
- **Inconsistent Documentation**: Documentation that follows different styles.
- **Hard-to-Read Documentation**: Documentation that is poorly formatted or hard to understand.