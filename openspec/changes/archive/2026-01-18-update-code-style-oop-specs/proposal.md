# Change: Update Code Style and OOP Specs to Match Implementation

## Why
The current code style and OOP specifications need to be updated to accurately reflect the actual codebase implementation. Analysis shows:
- Frontend files frequently exceed 200 lines (Game.ts: 935, GameStateManager.ts: 1030)
- Backend Python files generally comply with 200-line limit
- OOP patterns need clarification based on actual implementation (Player modular architecture, World service composition)

## What Changes
- Update `specs/code-style/spec.md` to reflect actual file size patterns:
  - Clarify that 200-line limit applies primarily to backend Python files
  - Frontend TypeScript files may exceed 200 lines due to framework requirements (Phaser scenes, Vue components)
  - Add guidance on when exceptions are acceptable
  
- Update `specs/python-oop/spec.md` to reflect actual OOP patterns:
  - Document Player class modular architecture (composition with managers)
  - Document World class service composition pattern
  - Clarify lazy initialization pattern for managers
  - Document dependency injection patterns actually used

## Impact
- Affected specs: `code-style/spec.md`, `python-oop/spec.md`
- Affected code: None (documentation update to match reality)
- Breaking changes: None (specs updated to reflect existing code)
