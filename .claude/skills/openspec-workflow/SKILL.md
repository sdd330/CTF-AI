---
name: openspec-workflow
description: OpenSpec spec-driven development workflow. Use when creating proposals, updating specs, planning features, or following the spec-driven development process.
allowed-tools: Read, Write, Edit, Bash(openspec:*), Glob, Grep
---

# OpenSpec Workflow Skill

You are an expert in spec-driven development using OpenSpec.

## Project OpenSpec Structure

```
openspec/
├── AGENTS.md           # Instructions for AI
├── project.md          # Project context
├── specs/              # Current truth (25 specs, 198 requirements)
│   ├── game-engine/
│   ├── player/
│   ├── world/
│   ├── dqn-agent/
│   ├── reinforcement-learning/
│   └── ...
└── changes/            # Proposals
    └── archive/        # Completed changes
```

## OpenSpec CLI Commands

```bash
# List all specs
openspec list --specs

# View specific spec
openspec show <spec-name>

# List active changes
openspec list

# Validate specs
openspec validate --specs --strict --no-interactive

# Validate specific change
openspec validate <change-id> --strict --no-interactive

# Archive completed change
openspec archive <change-id> --yes
```

## Creating a Change Proposal

### 1. Choose a verb-led change ID
Examples: `add-new-strategy`, `update-reward-function`, `refactor-pathfinding`

### 2. Create the structure
```bash
mkdir -p openspec/changes/<change-id>/specs/<capability>
```

### 3. Create proposal.md
```markdown
# Change: Brief description

## Why
1-2 sentences on problem/opportunity

## What Changes
- Bullet list of changes
- Mark breaking changes with **BREAKING**

## Impact
- Affected specs: [list]
- Affected code: [key files]
```

### 4. Create tasks.md
```markdown
## 1. Implementation
- [ ] 1.1 First task
- [ ] 1.2 Second task
- [ ] 1.3 Write tests
```

### 5. Create spec delta
```markdown
## ADDED Requirements
### Requirement: New Feature
The system SHALL provide...

#### Scenario: Success case
- **WHEN** condition
- **THEN** expected result

## MODIFIED Requirements
### Requirement: Existing Feature
[Complete updated requirement]
```

### 6. Validate
```bash
openspec validate <change-id> --strict --no-interactive
```

## Workflow Summary

1. **Draft**: Create proposal with spec updates
2. **Review**: Iterate until aligned
3. **Implement**: Work through tasks.md
4. **Archive**: Merge to specs/ after deployment

## Spec Format Rules

- Use `#### Scenario:` (4 hashtags) for scenarios
- Every requirement MUST have at least one scenario
- Use SHALL/MUST for normative requirements
- Delta headers: `## ADDED|MODIFIED|REMOVED|RENAMED Requirements`
