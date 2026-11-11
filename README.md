# Agent Desk

A desktop AI-agent assistant built with PySide6 (Qt for Python): a chat
interface backed by a small, transparent agent loop that can read a mock
email inbox, list mock files, and build/run multi-step workflows -- all
gated by a visible permission system, with every decision logged to an
inspectable trace.

> **Important -- what's real and what's simulated:** The "LLM" in this
> project is a deliberately simple, rule-based decision layer (see
> [Limitations](#limitations)), not a call to a real language model, and
> every action it can take operates on built-in sample data (a mock
> inbox, a mock file tree) rather than your real email, files, or any
> other system on your computer. Nothing in this project reads real
> accounts or sends real requests anywhere. The architecture is built so
> a real LLM provider or a real data source could be substituted behind
> the same interfaces -- but that substitution is intentionally not
> included here.

## Why this project

Agent frameworks are usually explained in the abstract; this project
tries to make the actual mechanics visible: an LLM layer *decides* what
to do, a *permission system* gates whether it's allowed to, a *tool*
actually does it, and a *trace* records every step so the whole decision
is auditable rather than a black box. Built incrementally, one feature
per branch/pull request.

## Installation

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Features

- **A transparent agent loop.** `Agent.handle_message` decides (via the
  LLM layer), checks permissions, calls a tool, and replies -- recording
  every one of those steps to an inspectable `trace`.
- **Mock inbox and file-listing tools**, each gated by its own
  permission, with a revocable `PermissionRegistry`.

## Project layout

```
src/agentdesk/
    agent/
        tools.py        The Tool contract every sandboxed action implements
        mock_data.py      Sample inbox + a nested mock file tree
        actions.py          Concrete tools: read_emails, list_files
        permissions.py        The revocable permission registry
        llm.py                  LLMProvider interface + the rule-based MockLLMProvider
        agent.py                  The orchestrator (decide -> check -> call -> reply)
        factory.py                  Builds a ready-to-use Agent with default tools
    gui/            PySide6 desktop UI (added once the agent core exists)
tests/              pytest suite
```

## Usage (library)

```python
from agentdesk.agent.factory import build_default_agent

agent = build_default_agent()
response = agent.handle_message("check my inbox about budget")
print(response.reply)
for step in response.trace:
    print(f"[{step.kind}] {step.detail}")
```

## Testing

```bash
pytest --cov=agentdesk --cov-report=term-missing
ruff check src tests
```

## Limitations

- The "LLM" is a small rule-based intent matcher (keyword/pattern
  matching over the user's message), not a real language model. It is
  built behind an `LLMProvider` interface specifically so a real model
  API could be substituted later without touching the rest of the
  agent -- but no such integration is included here.
- "Reading emails" and "listing files" operate on fixed, built-in sample
  data, not any real account, inbox, or filesystem.
- Workflows run entirely in memory for the lifetime of the app; nothing
  is scheduled or persisted to disk between runs.
- The permission system is a demonstration of the *pattern* (gate every
  tool call on an explicit, user-visible, revocable permission) rather
  than a production authorization system.

## License

MIT -- see [LICENSE](LICENSE).
