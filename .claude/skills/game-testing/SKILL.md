---
name: game-testing
description: Game testing for CTF-AI. Use when writing tests, running pytest, Vitest, Playwright e2e tests, testing game mechanics, or validating player behavior.
allowed-tools: Read, Bash(python:*), Bash(pytest:*), Bash(pnpm:*), Glob, Grep
---

# Game Testing Skill

You are an expert in testing game applications with Python and TypeScript.

## Project Test Structure

### Backend (Python + pytest)
```
backend/tests/
├── test_player.py      # Player mechanics
├── test_world.py       # World state
├── test_pathfinding.py # Pathfinding algorithms
└── ...
```

### Frontend (TypeScript + Vitest + Playwright)
```
frontend/src/**/*.test.ts     # Unit tests
frontend/tests/e2e/           # E2E tests
```

## Running Tests

### Backend
```bash
cd backend
source .venv/bin/activate

# Run all tests
python3 -m pytest tests/ -v

# Single file
python3 -m pytest tests/test_player.py -v

# Single class
python3 -m pytest tests/test_player.py::TestPlayerPlan -v

# Pattern matching
python3 -m pytest -k "test_plan" -v

# With coverage
python3 -m pytest tests/ -v --cov=lib --cov-report=html
```

### Frontend
```bash
cd frontend

# Unit tests
pnpm test

# E2E tests (headless)
pnpm test:e2e

# E2E tests (visible browser)
pnpm test:e2e:headed
```

## Test Patterns for Game Mechanics

### Player Tests
```python
def test_player_can_pickup_flag():
    # Setup: Player near enemy flag
    # Action: player.pickup_flag(flag)
    # Assert: player.has_flag == True

def test_player_cannot_tag_in_enemy_territory():
    # Setup: Player in enemy territory
    # Action: attempt tag
    # Assert: tag fails
```

### Pathfinding Tests
```python
def test_safe_path_avoids_enemies():
    # Setup: World with enemies
    # Action: find_safe_path()
    # Assert: path doesn't cross enemy zones
```

### RL Tests
```python
def test_state_extraction_dimensions():
    features = extract_state_features(player, world)
    assert features.shape == (19,)
    assert all(0 <= f <= 1 for f in features)
```

## E2E Test Patterns

```typescript
test('player can capture flag and score', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-testid="start-game"]');
  // Wait for game to load
  await expect(page.locator('.score')).toContainText('0');
  // Simulate gameplay...
});
```

## Test Coverage Goals

- Backend: 80%+ coverage on game_service, pathfinding_service
- Frontend: 70%+ coverage on managers
- E2E: Critical paths (game start, scoring, game over)
