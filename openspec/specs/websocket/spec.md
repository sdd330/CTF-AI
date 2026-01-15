# WebSocket Service Specification

## Purpose
WebSocket server handling real-time bidirectional communication between game backend and frontend clients.

## Requirements

### Requirement: WebSocket Handler
The WebSocketHandler SHALL manage WebSocket connections and message processing.

#### Scenario: Connection handling
- **WHEN** a client connects via WebSocket
- **THEN** the connection is accepted and registered

#### Scenario: Message parsing
- **WHEN** a JSON message is received
- **THEN** the message is parsed and routed to appropriate handler

#### Scenario: Response sending
- **WHEN** an action response is ready
- **THEN** the response is serialized and sent to the client

### Requirement: Thread Safety
The WebSocket service SHALL be thread-safe for concurrent connections.

#### Scenario: Concurrent access
- **WHEN** multiple clients send messages simultaneously
- **THEN** messages are processed safely with proper locking

### Requirement: Request Handler
The RequestHandler SHALL parse and delegate incoming requests.

#### Scenario: Init request
- **WHEN** a message with type "init" is received
- **THEN** `start_fn` callback is invoked with game initialization data

#### Scenario: Status request
- **WHEN** a message with type "status" is received
- **THEN** `plan_fn` callback is invoked to get player actions

#### Scenario: Finished request
- **WHEN** a message with type "finished" is received
- **THEN** `end_fn` callback is invoked for cleanup

### Requirement: Message Format
The system SHALL use a standardized JSON message format.

#### Scenario: Incoming message structure
- **WHEN** receiving a game message
- **THEN** it contains type, players, flags, and game state fields

#### Scenario: Outgoing message structure
- **WHEN** sending action response
- **THEN** it contains actions, paths, and timings fields

### Requirement: Server Entry Points
The server SHALL expose three callback functions for game lifecycle.

#### Scenario: start_game callback
- **WHEN** game initialization is requested
- **THEN** `start_game(req)` initializes World and GameMap

#### Scenario: plan_next_actions callback
- **WHEN** action planning is requested each tick
- **THEN** `plan_next_actions(req)` returns `{"actions": {}, "paths": {}, "timings": {}}`

#### Scenario: game_over callback
- **WHEN** game ends
- **THEN** `game_over(req)` performs cleanup

### Requirement: Async Server
The server SHALL run asynchronously using asyncio.

#### Scenario: Server startup
- **WHEN** `run_game_server(port, callbacks)` is called
- **THEN** an async WebSocket server starts on the specified port

#### Scenario: Multiple team servers
- **WHEN** running a full game
- **THEN** two server instances run on ports 34712 (Team L) and 34713 (Team R)
