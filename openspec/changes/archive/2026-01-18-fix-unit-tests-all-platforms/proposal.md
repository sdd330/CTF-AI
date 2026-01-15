# Change: Fix Unit Tests for Frontend, Backend, and Native

## Why
Unit tests are currently failing or cannot run across all three platforms:
1. **Backend tests**: Missing `pytest` dependency in `requirements.txt`, preventing tests from running
2. **Native tests**: Missing `pytest` dependency, preventing tests from running
3. **Frontend tests**: Duplicate key warnings in Phaser mock setup causing build warnings
4. **Test infrastructure**: Need to ensure all test suites can run successfully and identify any actual test failures

## What Changes
- **Add pytest to backend dependencies**:
  - Add `pytest>=7.0.0` to `backend/requirements.txt`
  - Ensure pytest is available for running backend tests

- **Add pytest to native dependencies**:
  - Create or update `native/requirements.txt` with `pytest>=7.0.0`
  - Ensure pytest is available for running native tests

- **Fix frontend test warnings**:
  - Fix duplicate `RND` key in Phaser mock setup in `GameStateManager.test.ts`
  - Remove redundant getter definitions that cause duplicate key warnings

- **Run and fix test failures**:
  - Run all test suites (frontend, backend, native)
  - Identify and fix any actual test failures
  - Ensure all tests pass successfully

- **Document test setup**:
  - Update documentation if needed to reflect dependency requirements
  - Ensure test commands work as expected

## Impact
- **Affected specs**: 
  - `game-testing/spec.md` (may need updates if test requirements change)
- **Affected code**: 
  - `backend/requirements.txt` - Add pytest dependency
  - `native/requirements.txt` - Add pytest dependency (create if missing)
  - `frontend/src/game/managers/__tests__/GameStateManager.test.ts` - Fix mock setup
  - Any test files with actual failures that need fixing
- **Breaking changes**: 
  - None - this is a test infrastructure fix
