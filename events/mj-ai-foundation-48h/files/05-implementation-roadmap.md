# MJ-AI Implementation Roadmap

## Phase 0 — Foundation planning

- scope freeze
- architecture decision
- threat model
- folder structure
- security contract
- test strategy

## Phase 1 — Local conversation MVP

- UI
- FastAPI/REST API
- SQLite
- session/context manager
- local LLM loader
- master agent
- basic chat
- audit logging

## Phase 2 — Memory MVP

- short-term memory
- profile memory
- project memory
- preference memory
- embedding and vector store
- memory router

## Phase 3 — Coding/file agents

- read/write tools
- scoped workspace
- approval flow
- code reviewer
- debugger
- file organizer

## Phase 4 — RAG

- chunker
- embedder
- retriever
- reranker
- source attribution
- data refresh policy

## Phase 5 — Voice & vision

- STT
- TTS
- image OCR
- object analysis
- permission and data retention

## Phase 6 — Automation

- approved workflows
- scheduler
- workflow recovery
- timeout/cancellation
- audit/replay

## Phase 7 — UI expansion

- PWA
- desktop
- mobile
- accessibility
- offline behavior
- notification policy

## Exit criteria for Phase 1

- user can chat locally
- local model can be loaded
- user session persists
- context remains bounded
- tool calls require permission
- audit log records actions
- model failure has fallback
- tests run locally
- backup/restore works
