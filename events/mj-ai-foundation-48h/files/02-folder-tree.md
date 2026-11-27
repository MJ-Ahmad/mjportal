# MJ-AI MVP Folder Tree

## MVP proposal

```text
MJ-AI/
├── README.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── config/
├── core/
├── llm/
├── memory/
├── agents/
├── tools/
├── rag/
├── knowledge/
├── database/
├── api/
├── ui/
├── auth/
├── security/
├── monitoring/
├── logs/
├── tests/
├── docs/
├── deployment/
└── scripts/
```

## MVP Phase-01 priority

### প্রথম পর্যায়

```text
config/
core/
llm/
memory/
agents/master_agent/
agents/coding_agent/
agents/file_agent/
tools/filesystem/
tools/notes/
security/
database/sqlite/
api/
ui/web/
tests/
docs/
scripts/
```

### দ্বিতীয় পর্যায়

```text
agents/research_agent/
agents/vision_agent/
agents/voice_agent/
agents/automation_agent/
agents/security_agent/
rag/
knowledge/
database/chroma/
database/faiss/
api/websocket/
ui/mobile/
ui/desktop/
deployment/
monitoring/
```

## Folder ownership rule

- `core/`: system orchestration—model logic নয়
- `llm/`: model loading, prompt ও inference
- `agents/`: specialist behavior ও agent contracts
- `tools/`: single-purpose, permission-aware operations
- `memory/`: state storage এবং retrieval
- `rag/`: document indexing ও retrieval
- `security/`: authorization এবং threat boundary
- `api/`: external interface
- `ui/`: presentation only
- `logs/`: runtime evidence; secrets নয়
- `deployment/`: environment and packaging
- `tests/`: acceptance evidence
