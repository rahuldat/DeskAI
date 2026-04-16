# DeskAI — Intelligent IT Support Agent

An AI-powered multi-agent helpdesk system that automates L1 and L2 IT support ticket resolution.

## How it works

- User submits an IT issue via the UI
- L1 Agent attempts to resolve using a runbook of common fixes
- If unresolved, escalates to L2 Agent for deeper diagnosis
- If L2 cannot resolve, automatically sends an escalation email to the developer team with full context and a generated ticket ID

## Tech Stack

- Python
- Streamlit (UI)
- Groq API / LLaMA 3.3 70B (AI agents)
- SMTP / Gmail (escalation email)
- dotenv (secret management)

## Architecture