# Pathfinding Specification

## Purpose
Pathfinding service providing multiple algorithms (A*, BFS, Dijkstra) with support for safe navigation avoiding enemy zones and weighted pathfinding for strategic movement.

## Requirements

### Requirement: Pathfinding Service Interface
The PathFindingService SHALL provide a unified interface for all pathfinding operations.

#### Scenario: Path calculation
- **WHEN** `find_path_to(start, end, player_name)` is called
- **THEN** a valid path avoiding obstacles is returned

#### Scenario: Direction extraction
- **WHEN** `get_direction(path)` is called with a valid path
- **THEN** the next direction to move is returned

### Requirement: A* Algorithm
The system SHALL implement A* pathfinding with Manhattan distance heuristic.

#### Scenario: Optimal path finding
- **WHEN** `astar_find_path(start, goal, obstacles)` is called
- **THEN** the shortest path considering obstacles is returned

#### Scenario: Direction priority
- **WHEN** multiple paths have equal cost
- **THEN** directions are prioritized for consistent behavior

### Requirement: BFS Algorithm
The system SHALL implement Breadth-First Search for unweighted pathfinding.

#### Scenario: BFS expansion
- **WHEN** `bfs_expand(position, obstacles)` is called
- **THEN** all valid adjacent positions are returned

#### Scenario: BFS path finding
- **WHEN** `bfs_find_path(start, goal, obstacles)` is called
- **THEN** a shortest unweighted path is returned

### Requirement: Dijkstra Algorithm
The system SHALL implement Dijkstra's algorithm for weighted pathfinding.

#### Scenario: Weighted path calculation
- **WHEN** `dijkstra_find_weighted_path(start, goal, weight_map)` is called
- **THEN** the minimum-cost path considering weights is returned

### Requirement: Safe Pathfinding
The WeightedPathFinder SHALL calculate paths that avoid enemy influence zones.

#### Scenario: Safe path generation
- **WHEN** `find_safe_path(start, goal, player)` is called
- **THEN** a path avoiding high-risk enemy zones is returned

#### Scenario: Enemy zone weighting
- **WHEN** building weight map for safe pathfinding
- **THEN** enemy positions and territories have higher weights

### Requirement: Defence Pathfinding
The WeightedPathFinder SHALL support aggressive pathfinding toward enemies.

#### Scenario: Defence path generation
- **WHEN** `find_defence_path(start, enemy_position)` is called
- **THEN** a path approaching the enemy is returned

### Requirement: Weight Map Builder
The system SHALL construct weight maps based on enemy positions and territories.

#### Scenario: Weight map construction
- **WHEN** `build_weight_map(world, player)` is called
- **THEN** a grid with enemy influence weights is created

#### Scenario: Influence zone calculation
- **WHEN** calculating enemy influence
- **THEN** positions closer to enemies have higher weights

### Requirement: Pathfinding Strategy Pattern
The system SHALL support interchangeable pathfinding strategies.

#### Scenario: Strategy selection
- **WHEN** a pathfinding request specifies an algorithm
- **THEN** the corresponding strategy (BFS, A*, Dijkstra) is used

#### Scenario: Strategy interface
- **WHEN** implementing a new pathfinding strategy
- **THEN** the PathfindingStrategy abstract base class is extended
