# Socket Manager Specification

## Purpose
Frontend WebSocket management handling real-time communication with backend game servers, including connection lifecycle, message handling, and event emission.

## Requirements

### Requirement: Socket Manager Singleton
The SocketManager SHALL be a singleton managing all WebSocket connections.

#### Scenario: Singleton access
- **WHEN** `SocketManager.getInstance()` is called
- **THEN** the same SocketManager instance is returned

#### Scenario: Multiple team connections
- **WHEN** connecting to game servers
- **THEN** separate connections for Team L (34712) and Team R (34713) are managed

### Requirement: Team Socket
The TeamSocket class SHALL manage individual team WebSocket connections.

#### Scenario: Connection establishment
- **WHEN** `teamSocket.connect(url)` is called
- **THEN** a WebSocket connection is established

#### Scenario: Connection retry
- **WHEN** connection fails
- **THEN** automatic reconnection is attempted

#### Scenario: Message sending
- **WHEN** `teamSocket.send(message)` is called
- **THEN** the message is serialized and sent

### Requirement: Event Emitter Pattern
The SocketManager SHALL use an event emitter for message notifications.

#### Scenario: Event subscription
- **WHEN** `socketManager.on(event, callback)` is called
- **THEN** the callback is registered for that event

#### Scenario: Event emission
- **WHEN** a WebSocket message is received
- **THEN** registered callbacks are invoked with the message data

### Requirement: Socket Events
The system SHALL emit standardized socket events.

#### Scenario: Connect event
- **WHEN** WebSocket connection is established
- **THEN** CONNECT event is emitted

#### Scenario: Disconnect event
- **WHEN** WebSocket connection is closed
- **THEN** DISCONNECT event is emitted

#### Scenario: Message event
- **WHEN** a message is received
- **THEN** MESSAGE event is emitted with parsed data

#### Scenario: Actions received event
- **WHEN** player actions are received from backend
- **THEN** ACTIONS_RECEIVED event is emitted

#### Scenario: Error event
- **WHEN** a WebSocket error occurs
- **THEN** ERROR event is emitted with error details

### Requirement: Message Protocol
The SocketManager SHALL handle the game message protocol.

#### Scenario: Init payload handling
- **WHEN** GameInitPayload is received
- **THEN** game initialization data is extracted and distributed

#### Scenario: Status payload handling
- **WHEN** GameStatusPayload is received
- **THEN** player and flag states are updated

#### Scenario: Finished payload handling
- **WHEN** GameFinishedPayload is received
- **THEN** game end state is processed

### Requirement: Payload Construction
The SocketManager SHALL construct outgoing payloads.

#### Scenario: Action payload
- **WHEN** sending player actions
- **THEN** PlayerActions payload with directions is constructed

#### Scenario: Payload validation
- **WHEN** constructing payloads
- **THEN** required fields are validated before sending
