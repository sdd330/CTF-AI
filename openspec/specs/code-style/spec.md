# Code Style Specification

## Purpose
Code style rules and conventions for the CTF-AI project.

## Requirements

### Requirement: File Size Limit
All source files SHALL follow size limits based on language and framework constraints.

**Backend Python files** (`.py`):
- SHALL NOT exceed 200 lines, including test files

**Frontend TypeScript/Vue files** (`.ts`, `.tsx`, `.vue`):
- SHOULD target 200 lines or fewer
- MAY exceed 200 lines when framework requirements make it impractical (e.g., Phaser scenes, Vue SFCs)

#### Scenario: Backend Python file within limit
- **WHEN** a Python source file has 200 lines or fewer
- **THEN** the file complies with the size limit

#### Scenario: Backend Python file exceeds limit
- **WHEN** a Python source file exceeds 200 lines
- **THEN** the file MUST be refactored into smaller, focused modules

#### Scenario: Frontend TypeScript file exceeds limit
- **WHEN** a TypeScript file exceeds 200 lines due to framework requirements
- **THEN** the file SHOULD be refactored when possible, but exceptions are acceptable if splitting would harm framework integration

#### Scenario: Test file within limit
- **WHEN** a test file has 200 lines or fewer
- **THEN** the file complies with the size limit

#### Scenario: Test file exceeds limit
- **WHEN** a test file exceeds 200 lines
- **THEN** the file MUST be split into multiple test files by logical grouping

### Requirement: Module Single Responsibility
Each module SHALL have a single, clearly defined responsibility.

#### Scenario: Module with focused purpose
- **WHEN** a module is created or modified
- **THEN** it MUST serve exactly one purpose

#### Scenario: Module needs splitting
- **WHEN** a module's description requires "AND" to explain its purpose
- **THEN** the module MUST be split into separate modules

### Requirement: Python Style
Python code SHALL follow PEP 8 conventions.

#### Scenario: Python naming conventions
- **WHEN** writing Python code
- **THEN** use `snake_case` for functions/variables, `PascalCase` for classes

#### Scenario: Python exception handling
- **WHEN** catching exceptions
- **THEN** always specify exception types (no bare `except:`)

### Requirement: TypeScript Style
TypeScript code SHALL follow standard TypeScript conventions with strict mode enabled.

#### Scenario: TypeScript type annotations
- **WHEN** writing TypeScript code
- **THEN** prefer explicit type annotations for function parameters and return types

#### Scenario: TypeScript naming conventions
- **WHEN** writing TypeScript code
- **THEN** use `camelCase` for functions/variables, `PascalCase` for classes/interfaces/types

#### Scenario: ES6 Module Imports
- **WHEN** importing modules in TypeScript code
- **THEN** MUST use ES6 `import` statements
- **THEN** MUST NOT use CommonJS `require()` statements

### Requirement: Code Comments
Code SHALL be self-documenting with minimal comments.

#### Scenario: Unnecessary comments
- **WHEN** writing code
- **THEN** MUST NOT add obvious comments that simply repeat what the code does
- **THEN** MUST NOT add verbose explanations for standard operations

#### Scenario: Special logic comments
- **WHEN** implementing non-obvious logic, workarounds, or complex algorithms
- **THEN** MAY add brief comments explaining the "why" not the "what"
- **THEN** comments MUST be concise and focus on the reasoning, not the implementation

#### Scenario: Code clarity
- **WHEN** code needs explanation
- **THEN** prefer refactoring to make code self-explanatory over adding comments
- **THEN** use clear variable and function names instead of comments

### Requirement: ESLint Rule Disabling
Code SHALL NOT use inline ESLint rule disabling comments (e.g., `eslint-disable`, `eslint-disable-next-line`).

#### Scenario: ESLint rule violation detected
- **WHEN** ESLint reports a rule violation
- **THEN** the code MUST be refactored to comply with the rule
- **THEN** MUST NOT add `eslint-disable` comments to suppress the violation

#### Scenario: Framework-specific requirements
- **WHEN** a rule violation is caused by framework requirements (e.g., TypeScript global declarations requiring `var`)
- **THEN** the ESLint configuration MUST be updated to allow the pattern for specific file types (e.g., using `overrides` in `.eslintrc.json`)
- **THEN** MUST NOT use inline `eslint-disable` comments

#### Scenario: Environment variable checks
- **WHEN** checking environment variables in Vite projects
- **THEN** MUST use `import.meta.env.DEV` or `import.meta.env.MODE` instead of `process.env.NODE_ENV`
- **THEN** MUST NOT use `eslint-disable` to suppress type checking issues with `process.env`

#### Scenario: Alternative solutions
- **WHEN** a rule seems too strict for a specific use case
- **THEN** MUST first consider refactoring the code to comply with the rule
- **THEN** MUST consider updating ESLint configuration at the project level if the pattern is legitimate
- **THEN** MUST document the rationale in ESLint configuration comments if an exception is needed

## Refactoring Patterns

### Large File Splitting Strategy

For files exceeding 200 lines:
1. Extract by Feature
2. Extract by Layer
3. Extract Helpers
4. Extract Constants
5. Extract Types

### Test File Splitting Strategy

For test files exceeding 200 lines:
1. Split by Test Category
2. Split by Feature
3. Extract Test Fixtures
4. Extract Test Data
