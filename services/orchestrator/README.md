# Orchestrator Agent

**Type:** Reasoning agent

## Role

Owns the conversation session; decides which specialist to call next from learner intent and session state; merges results into one reply.

## Inputs (reads)

- Raw learner message
- Session state

## Outputs (writes)

- Routed sub-agent call
- Composed reply

## Tools

- `session_store`
- `subagent_invoke`
- `dialogue_memory`

---
Source: [ARCHITECTURE.md](../../ARCHITECTURE.md), Section 03, card 01. Status: skeleton only — no implementation yet.
