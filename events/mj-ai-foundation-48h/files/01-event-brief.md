# MJ-AI — First Foundation Event

- Event ID: `EVT-20261127-MJ-AI-P1`
- Project: `MJ-AI`
- শুরু: `2026-11-27T08:12:41+06:00`
- Deadline: `2026-11-29T08:12:41+06:00`
- Timezone: `Asia/Dhaka`
- Status: `planning`

## লক্ষ্য

MJ-AI হবে একটি Local-First, Modular, Multi-Agent AI Assistant।
প্রথম 48 ঘণ্টার উদ্দেশ্য হলো implementation না করে:

- architecture boundary স্থির করা
- MVP scope নির্ধারণ করা
- agent ও memory responsibility নির্ধারণ করা
- security এবং sandbox policy সংজ্ঞায়িত করা
- implementation-ready folder structure approve করা

## 48-hour deliverables

- Folder tree ও module responsibility
- UI, API, core ও model execution flow
- Agent contract ও permission matrix
- Memory/data lifecycle
- Security baseline
- LLM selection ও fallback policy
- Test এবং handover checklist

## Scope guardrails

প্রথম ইভেন্টে বাস্তব agent/terminal execution চালু হবে না।
এর মধ্যে থাকবে না:

- destructive terminal capability
- arbitrary file deletion
- external action without approval
- secrets বা passwords repository-তে রাখা
- production deployment
- autonomous long-running actions
- external agent communication
- trained model data publication
