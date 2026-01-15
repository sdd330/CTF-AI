# Change: Cleanup Frontend OOP Interfaces and Remove Deprecated Code

## Why
After the frontend refactoring, there are several issues that need cleanup:
1. **Backward compatibility exports**: Multiple "向后兼容" (backward compatibility) exports exist that may no longer be needed
2. **Redundant comments**: Excessive comments that repeat what the code does, violating code-style spec
3. **OOP interface violations**: Some interfaces may not follow OOP principles (encapsulation, minimal public interface)
4. **Deprecated code patterns**: Old code patterns that were kept for compatibility but are no longer used

## What Changes
- **Audit and remove backward compatibility exports**:
  - Check if exports marked as "向后兼容" are actually used
  - Remove unused backward compatibility exports from:
    - `GameStateManager.ts`: Type exports
    - `MapManager.ts`: TileData, GroundLayer, LevelLayer, BoundaryLayer exports
    - `SocketManager.ts`: TeamSocket export
    - `PhysicsManager.ts`: CollisionCallbacks export
    - `UIManager.ts`: UIComponentFactory, UIComponents exports
  - Remove "向后兼容" comments if exports are removed

- **Clean up redundant code comments**:
  - Remove comments that simply repeat what the code does
  - Remove verbose explanations for standard operations
  - Keep only comments that explain "why" (non-obvious logic, workarounds, complex algorithms)
  - Follow code-style spec: code should be self-documenting

- **Review and fix OOP interface violations**:
  - Ensure all classes follow single responsibility principle
  - Verify encapsulation: private methods/properties are properly marked
  - Check minimal public interface: only necessary methods are public
  - Remove any public access to internal managers that should be private
  - Ensure dependency injection is used instead of global state

- **Remove deprecated Player properties**:
  - Review Player class "向后兼容的属性" (backward compatible properties)
  - If no longer used, remove them and update callers to use new interfaces

## Impact
- **Affected specs**: 
  - `frontend/spec.md` (may need updates if interfaces change)
  - `code-style/spec.md` (already requires minimal comments)
- **Affected code**: 
  - Frontend manager classes (GameStateManager, MapManager, SocketManager, PhysicsManager, UIManager)
  - Player class
  - Any code importing the removed exports
- **Breaking changes**: 
  - Potentially breaking if backward compatibility exports are actually used
  - Need to verify usage before removal
