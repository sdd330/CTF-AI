## MODIFIED Requirements

### Requirement: File Size Limit
All source files SHALL follow size limits based on language and framework constraints.

**Backend Python files** (`.py`):
- SHALL NOT exceed 200 lines, including test files
- **Rationale**: Smaller files improve AI readability, code review efficiency, and encourage single-responsibility design

**Frontend TypeScript/Vue files** (`.ts`, `.tsx`, `.vue`):
- SHOULD target 200 lines or fewer when possible
- MAY exceed 200 lines when framework requirements make it impractical (e.g., Phaser scene classes, complex Vue components with template/script/style)
- **Rationale**: Framework-specific patterns (Phaser scenes, Vue SFC structure) may require larger files, but should still be split when feasible

#### Scenario: Backend Python file within limit
- **WHEN** a Python source file has 200 lines or fewer
- **THEN** the file complies with the size limit

#### Scenario: Backend Python file exceeds limit
- **WHEN** a Python source file exceeds 200 lines
- **THEN** the file MUST be refactored into smaller, focused modules

#### Scenario: Frontend TypeScript file exceeds limit
- **WHEN** a TypeScript file exceeds 200 lines due to framework requirements (Phaser scene, complex component)
- **THEN** the file SHOULD be refactored when possible, but exceptions are acceptable if splitting would harm framework integration
- **THEN** the file MUST still follow single responsibility principle within its larger size

#### Scenario: Test file within limit
- **WHEN** a test file has 200 lines or fewer
- **THEN** the file complies with the size limit

#### Scenario: Test file exceeds limit
- **WHEN** a test file exceeds 200 lines
- **THEN** the file MUST be split into multiple test files by logical grouping
