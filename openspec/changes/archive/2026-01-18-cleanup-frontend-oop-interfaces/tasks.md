## 1. Analysis
- [x] 1.1 Audit all "向后兼容" exports and check actual usage
- [x] 1.2 Identify redundant comments that violate code-style spec
- [x] 1.3 Review OOP interface violations (public access to internal managers, etc.)
- [x] 1.4 Check Player class backward compatible properties usage

## 2. Backward Compatibility Cleanup
- [x] 2.1 Check GameStateManager type exports usage (TeamState, GameFlowState, GameFlowEvent, GameState)
- [x] 2.2 Check MapManager exports usage (TileData, GroundLayer, LevelLayer, BoundaryLayer)
- [x] 2.3 Check SocketManager TeamSocket export usage
- [x] 2.4 Check PhysicsManager CollisionCallbacks export usage
- [x] 2.5 Check UIManager exports usage (UIComponentFactory, ScoreTextComponent, etc.)
- [x] 2.6 Remove unused backward compatibility exports
- [x] 2.7 Remove "向后兼容" comments from remaining code

## 3. Code Comments Cleanup
- [x] 3.1 Remove redundant comments that repeat code behavior
- [x] 3.2 Remove verbose explanations for standard operations
- [x] 3.3 Keep only comments explaining "why" (non-obvious logic)
- [x] 3.4 Ensure code is self-documenting with clear names

## 4. OOP Interface Review
- [x] 4.1 Verify all classes follow single responsibility principle
- [x] 4.2 Check encapsulation: ensure private methods/properties are marked
- [x] 4.3 Review public interfaces: remove unnecessary public methods
- [x] 4.4 Check for public access to internal managers (should be private)
- [x] 4.5 Verify dependency injection is used (no global state access)

## 5. Player Class Cleanup
- [x] 5.1 Check usage of Player backward compatible properties (inPrison, hasFlag)
- [x] 5.2 If unused, remove backward compatible properties
- [x] 5.3 Update any callers to use PlayerStateManager directly if needed

## 6. Testing
- [x] 6.1 Run unit tests to verify no breaking changes
- [x] 6.2 Run E2E tests to verify functionality
- [x] 6.3 Check for any import errors after removing exports

## 7. Documentation
- [x] 7.1 Update frontend spec if interfaces change
- [x] 7.2 Update code comments to follow code-style spec
