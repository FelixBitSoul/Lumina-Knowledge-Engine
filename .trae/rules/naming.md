# Naming Conventions

## 1. General Naming

- **Descriptive Names**: Use meaningful names that describe the purpose or behavior.
- **Consistency**: Follow language-specific naming conventions consistently.
- **Avoid Abbreviations**: Use full words unless abbreviations are widely understood.
- **Length**: Names should be long enough to be clear but not overly verbose.
- **Context**: Names should provide sufficient context for their use.

## 2. Language-Specific Naming

### 2.1 Python
- **Files**: Use snake_case (e.g., `document_service.py`).
- **Functions**: Use snake_case (e.g., `generate_document_id()`).
- **Variables**: Use snake_case (e.g., `file_content`).
- **Classes**: Use CamelCase (e.g., `DocumentService`).
- **Constants**: Use UPPER_SNAKE_CASE (e.g., `MAX_FILE_SIZE`).
- **Protected Methods**: Use single underscore prefix (e.g., `_process_file()`).
- **Private Methods**: Use double underscore prefix (e.g., `__validate_input()`).
- **Special Methods**: Use double underscore prefix and suffix (e.g., `__init__()`).

### 2.2 TypeScript/JavaScript
- **Files**: Use PascalCase for components (e.g., `FileManager.tsx`), camelCase for utilities (e.g., `api.ts`).
- **Functions**: Use camelCase (e.g., `processFile()`).
- **Variables**: Use camelCase (e.g., `fileContent`).
- **Classes**: Use PascalCase (e.g., `FileService`).
- **Constants**: Use UPPER_SNAKE_CASE (e.g., `MAX_FILE_SIZE`).
- **Interfaces**: Use PascalCase with `I` prefix (e.g., `IFileData`).
- **Types**: Use PascalCase (e.g., `FileStatus`).

### 2.3 Go
- **Files**: Use snake_case (e.g., `document_service.go`).
- **Functions**: Use CamelCase (e.g., `GenerateDocumentID()`).
- **Variables**: Use camelCase (e.g., `fileContent`).
- **Structs**: Use CamelCase (e.g., `DocumentService`).
- **Constants**: Use UPPER_SNAKE_CASE (e.g., `MaxFileSize`).
- **Packages**: Use lowercase letters (e.g., `document`).

## 3. Naming Patterns

### 3.1 Boolean Variables
- Use prefixes like `is`, `has`, `can`, `should` (e.g., `is_valid`, `has_permission`).

### 3.2 Collections
- Use plural names (e.g., `files`, `users`, `items`).

### 3.3 Functions
- Use verb-noun patterns (e.g., `get_user`, `process_file`, `validate_input`).
- Use clear, action-oriented names.

### 3.4 Classes
- Use noun or noun-phrase names (e.g., `DocumentService`, `FileManager`).
- Use descriptive names that reflect the class's purpose.

### 3.5 Constants
- Use descriptive, all-uppercase names with underscores (e.g., `MAX_FILE_SIZE`, `DEFAULT_TIMEOUT`).

## 4. Anti-Patterns

- **Single-letter Names**: Avoid single-letter names except for loop variables or mathematical constants.
- **Hungarian Notation**: Avoid type-based prefixes (e.g., `strName`, `intCount`).
- **Abbreviations**: Avoid unclear abbreviations (e.g., `doc_svc` instead of `document_service`).
- **Inconsistent Capitalization**: Maintain consistent capitalization within the same codebase.
- **Misleading Names**: Ensure names accurately reflect the purpose or behavior of the code.