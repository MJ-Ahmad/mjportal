# MJ-AI Layer Map

```text
UI Layer
├── Web UI
├── Mobile UI
└── Desktop UI

API Layer
├── REST API
└── WebSocket

Core Layer
├── Conversation Manager
├── Session Manager
├── Context Manager
├── Task Manager
├── Planner
├── Executor
└── Orchestrator

Agent Layer
├── Master Agent
├── Research Agent
├── Coding Agent
├── File Agent
├── Vision Agent
├── Voice Agent
├── Automation Agent
└── Security Agent

AI/LLM Layer
├── Qwen
├── Phi
├── Llama
└── Gemma

Memory Layer
├── Short-Term Memory
├── Long-Term Memory
├── Vector Store
└── Knowledge Graph

Storage Layer
├── SQLite
├── ChromaDB
├── FAISS
└── Backups

Security Layer
├── Authentication
├── Encryption
├── Audit
├── Sandbox
└── Permissions
```

## Request flow

```text
User
  -> UI
  -> API
  -> Session/Context
  -> Planner
  -> Security permission check
  -> Master Agent
  -> Specialist Agent or Tool
  -> Memory/RAG
  -> LLM
  -> Executor
  -> Audit log
  -> UI response
```

## Dependency rule

- UI layer কখনো সরাসরি database বা model file access করবে না।
- Specialist Agent কখনো implicit permission নেবে না।
- Tool execution-এ permission context বাধ্যতামূলক।
- Core layer UI framework-এর ওপর নির্ভর করবে না।
- LLM layer agent behavior-এ সরাসরি hard-code হবে না।
