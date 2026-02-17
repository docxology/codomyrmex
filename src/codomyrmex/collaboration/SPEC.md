# collaboration - Functional Specification

## Purpose

To multiply the effectiveness of individual Codomyrmex agents by enabling them to collaborate, specialize, and reach consensus on complex tasks.

## Design Principles

- **Decentralization**: Avoid single points of failure in agent coordination.
- **Interoperability**: Agents should be able to collaborate regardless of their underlying model or architecture.
- **Transparency**: Every step of the collaboration should be traceable.
- **Feedback Loops**: Constant evaluation and adjustment based on agent feedback.

## Architecture

```mermaid
graph TD
    User([User]) --> SM[SwarmManager]
    SM --> A1[Agent 1]
    SM --> A2[Agent 2]
    A1 <--> A2
    A1 --> SMH[Shared Memory]
    A2 --> SMH
```

## Functional Requirements

- Broadcast messages to an entire swarm or specific groups.
- Elect a 'Leader' or 'Orchestrator' agent for a specific mission.
- Implement 'Peer Review' patterns where one agent verifies another's output.
- Provide a 'Wall' or 'Log' of the collaborative process.

## Interface Contracts

### Communication (`collaboration.communication`)

```python
class Broadcaster:
    def subscribe(topic: str, subscriber_id: str, handler: Callable, ...) -> str
    async def publish(topic: str, message: AgentMessage) -> int
    def list_topics() -> List[TopicInfo]

class DirectMessenger:
    async def send_private(recipient_id: str, message: AgentMessage) -> bool
```

### Coordination (`collaboration.coordination`)

```python
class VotingMechanism:
    def create_proposal(title: str, proposer_id: str, ...) -> Proposal
    def cast_vote(proposal_id: str, voter_id: str, vote: VoteType, ...) -> Vote
    def tally_votes(proposal_id: str, total_voters: int) -> VotingResult

class ConsensusBuilder:
    def propose_value(key: str, agent_id: str, value: Any) -> None
    async def reach_consensus(key: str, agents: List[Agent], ...) -> Optional[Any]

class TaskDecomposer:
    def decompose(mission: str) -> List[Task]
```

## Technical Constraints

- Large swarms may face coordination overhead and messaging latency.
- Requires robust serialization for transferring state between agents.

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k collaboration -v
```
