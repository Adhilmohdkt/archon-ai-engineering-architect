# Archon — AI Engineering Architect

> An agentic AI system that transforms software requirements into a reviewed, technology-backed architecture blueprint.

🌐 **Live Demo:** https://archon-ai-engineering-architect.vercel.app

---

## Overview

Archon is an AI-powered software architecture assistant that transforms a high-level software requirement into a structured, reviewed, technology-backed architecture proposal.

Instead of relying on a single LLM call, Archon uses a **LangGraph-based multi-agent workflow** where specialized agents collaborate to understand requirements, design architecture, research technologies, critique the design, revise it when necessary, escalate to a human, and produce a final architecture blueprint with a structured diagram.

---

## What Archon Does

```text
User Requirement
       │
       ▼
Requirements & Architecture Agent
       │
       ▼
Technology Recommendation Agent
       │
       ▼
Critic Agent
       │
       ├───────────────┐
       │               │
    Approved       Revision Needed
       │               │
       │               ▼
       │         Requirements /
       │         Technology Agent
       │               │
       │               ▼
       │             Critic
       │
       ▼
Human Review
       │
       ▼
Finalizer Agent
       │
       ▼
Diagram Agent
       │
       ▼
Final Architecture Blueprint
       │
       ▼
Architecture Diagram
```

---

## Architecture

```text
                         ┌─────────────────────┐
                         │        User         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       Vercel        │
                         │    Next.js Frontend │
                         └──────────┬──────────┘
                                    │ HTTPS
                                    ▼
                         ┌─────────────────────┐
                         │       Render        │
                         │    FastAPI Backend  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      LangGraph      │
                         │   Agentic Workflow  │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       Requirements Agent     Technology Agent      Critic Agent
                                    │
                                    ▼
                               MCP / Tools
                                    │
                                    ▼
                              Web Research

                         ┌─────────────────────┐
                         │    Human Review     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                              Finalizer
                                    │
                                    ▼
                               Diagram
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
             Neon PostgreSQL                  LangSmith
              Persistence                    Observability
```

---

# Agent Workflow

## 1. Supervisor Agent

The Supervisor controls the workflow and routes execution based on the current state.

It can route to:

- Requirements
- Technology
- Critic
- Finalizer
- Human

The workflow has a maximum automated revision limit of **3 revisions**, preventing uncontrolled critique loops.

## 2. Requirements & Architecture Agent

Converts the user's goal into:

- Functional requirements
- Non-functional requirements
- Constraints
- Architecture style
- Major components
- Data flow
- Architectural reasoning

During revisions, it incorporates Critic feedback.

## 3. Technology Recommendation Agent

Recommends technologies based on:

- Requirements
- Constraints
- Cost
- Scalability
- Maintainability
- Security
- Operational complexity
- Alternatives
- Trade-offs

The agent uses **MCP-based web research** for current technology information.

## 4. Critic Agent

Independently evaluates:

- Requirements coverage
- Non-functional requirements
- Constraints
- Architecture consistency
- Component responsibilities
- Data flow
- Scalability
- Reliability
- Security
- Technology consistency

It produces structured output containing:

```text
approved
issues
target_agent
revision_required
```

---

# Revision Loop

```text
                    Critic
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
     Requirements Issue    Technology Issue
             │                   │
             ▼                   ▼
      Requirements Agent   Technology Agent
             │                   │
             └─────────┬─────────┘
                       ▼
                     Critic
```

Up to **3 automated revisions** are allowed. If the limit is reached, the workflow escalates to human review.

---

# Human-in-the-Loop

When automated revisions are exhausted, Archon pauses using LangGraph's interrupt mechanism.

The human reviewer can:

- Approve
- Request a revision
- Reject
- Provide feedback

Human feedback becomes part of the graph state and is supplied to the appropriate agent when the workflow resumes.

---

# Finalizer Agent

Once the design is approved, the Finalizer consolidates the decisions into an implementation-oriented architecture blueprint covering:

1. System overview
2. Requirements summary
3. Architecture and major components
4. Technology stack
5. End-to-end data flow
6. Security considerations
7. Scalability and reliability
8. Implementation considerations
9. Assumptions and open decisions

---

# Diagram Agent

The Diagram Agent converts the approved blueprint into a structured architecture graph.

Nodes contain:

```text
id
label
type
```

Edges contain:

```text
source
target
label
```

The frontend renders the graph using **React Flow**.

---

# Key Engineering Features

- **Agentic AI:** Stateful multi-agent workflow rather than a single LLM call.
- **LangGraph:** Orchestration, routing, revisions, interrupts, resumption, and checkpoints.
- **MCP:** Tool-based web research for technology recommendations.
- **Structured Outputs:** Pydantic schemas for requirements, architecture, recommendations, critique, and diagrams.
- **Human-in-the-Loop:** Controlled escalation after automated revisions.
- **PostgreSQL Persistence:** Persistent LangGraph checkpoints.
- **LangSmith Observability:** Tracing of LangChain/LangGraph execution, LLM calls, latency, tokens, and errors.
- **Evaluation:** Separate deterministic workflow evaluation and LLM-as-a-judge quality evaluation.
- **FastAPI:** REST API for the AI workflow.
- **Docker:** Containerized backend.
- **CI/CD:** GitHub Actions for automated validation.

---

# Technology Stack

| Area | Technology |
|---|---|
| Language | Python |
| Backend | FastAPI |
| Agent Orchestration | LangGraph |
| LLM Framework | LangChain |
| LLM Provider | Groq |
| Tool Protocol | MCP |
| Web Research | Tavily / MCP |
| Structured Output | Pydantic |
| Database | PostgreSQL |
| Checkpointing | LangGraph PostgreSQL Checkpointer |
| Observability | LangSmith |
| Frontend | Next.js |
| UI | React + Tailwind CSS |
| Architecture Visualization | React Flow |
| API | REST |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Frontend Deployment | Vercel |
| Backend Deployment | Render |
| Database Hosting | Neon |

---

# Production Deployment

```text
                    Internet
                       │
                       ▼
                ┌─────────────┐
                │   Vercel    │
                │   Next.js   │
                └──────┬──────┘
                       │ HTTPS
                       ▼
                ┌─────────────┐
                │   Render    │
                │   FastAPI   │
                └──────┬──────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
       ┌─────────────┐   ┌─────────────┐
       │    Neon     │   │ Groq/Tavily │
       │ PostgreSQL  │   │   Services  │
       └─────────────┘   └─────────────┘

                       │
                       ▼
                 ┌───────────┐
                 │ LangSmith │
                 │  Tracing  │
                 └───────────┘
```

### Live Application

https://archon-ai-engineering-architect.vercel.app

### Backend API

https://archon-ai-engineering-architect.onrender.com

### API Documentation

https://archon-ai-engineering-architect.onrender.com/docs

---

# Evaluation

Archon uses **two complementary evaluation layers**. They are intentionally kept separate because they measure different properties of the system.

## 1. Structural / Deterministic Evaluation

### What it measures

> **Did the Archon workflow behave correctly?**

Six objective checks are performed for each test case:

1. Requirements produced
2. Architecture produced
3. Technology recommendations produced
4. Critique produced
5. Final blueprint produced
6. Human review triggered correctly when required

### Results

| Metric | Result |
|---|---:|
| Golden test cases | **10** |
| Checks per case | **6** |
| Total checks | **60** |
| Passed checks | **50 / 60** |
| Structural score | **83.33%** |
| Automatically completed | **8 / 10** |
| Human review required | **2 / 10** |
| Cases reaching 3-revision limit | **2 / 10** |

The two human-review cases were:

| Case | Scenario | Result |
|---|---|---|
| `archon_005` | Video Streaming | Human review after 3 revisions |
| `archon_007` | High-Scale API | Human review after 3 revisions |

These cases demonstrate the intended revision-limit and human-escalation behavior.

---

## 2. G-Eval Quality Evaluation

### What it measures

> **How good was the architecture blueprint produced by Archon?**

This evaluation uses **DeepEval GEval** with **Groq GPT-OSS-120B** as the LLM judge.

The blueprint is evaluated across five dimensions:

| Quality Dimension | What It Measures |
|---|---|
| **Requirements Coverage** | Whether important requirements are actually addressed |
| **Architecture Quality** | Coherence, responsibilities, data flow, scalability, reliability, and complexity |
| **Technology Decisions** | Suitability, justification, consistency, and trade-offs |
| **Reliability & Security** | Security, failure handling, resilience, observability, and recovery |
| **Final Blueprint Quality** | Clarity, technical depth, consistency, and implementability |

### G-Eval Scoring Scale

```text
1.0 = Exceptional
0.8 = Strong
0.6 = Adequate
0.4 = Weak
0.2 = Very weak
0.0 = Fails
```

### Individual Case Results

| Case | Category | Score |
|---|---|---:|
| `archon_001` | Document Processing | **0.90** |
| `archon_002` | E-Commerce | **0.90** |
| `archon_003` | Food Delivery | **0.90** |
| `archon_004` | Banking | **1.00** |
| `archon_005` | Video Streaming | **Incomplete** |
| `archon_006` | Ambiguous Requirements | **1.00** |
| `archon_007` | High-Scale API | **Incomplete** |
| `archon_008` | MCP Tool Usage | **0.90** |
| `archon_009` | Human Feedback Revision | **0.90** |
| `archon_010` | Failure & Reliability | **0.90** |

### Overall G-Eval Result

| Metric | Result |
|---|---:|
| Test cases | **10** |
| Successfully evaluated | **8 / 10** |
| Incomplete | **2 / 10** |
| Evaluation framework | **DeepEval GEval** |
| Judge model | **Groq GPT-OSS-120B** |
| Metrics per case | **1** |
| Evaluation dimensions | **5** |
| Global quality score | **0.925** |
| Global quality percentage | **92.5%** |

The global quality score is calculated from the eight successfully evaluated cases. The two cases that stopped at human review did not produce final blueprints and therefore were not included in the G-Eval quality average.

---

## Evaluation Summary

```text
                    ARCHON EVALUATION
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
   STRUCTURAL /                    G-EVAL QUALITY
   DETERMINISTIC                    EVALUATION
             │                           │
             │                           │
     "Did the workflow               "How good was
      behave correctly?"              the output?"
             │                           │
             ▼                           ▼
      Objective checks             LLM-as-a-Judge
             │                           │
             ▼                           ▼
       50 / 60 passed               8 evaluated cases
             │                           │
             ▼                           ▼
          83.33%                       92.5%
```

**The two scores are not combined into a single overall score because they measure different properties.**

The structural score measures **workflow correctness**, while the G-Eval score measures **the quality of the generated architecture**.

---

# Observability with LangSmith

LangSmith provides tracing for Archon's LangChain and LangGraph execution.

A typical trace contains:

```text
Archon Run
    │
    ├── Supervisor
    ├── Requirements Agent
    ├── Technology Agent
    │     └── MCP / Tool Calls
    ├── Critic Agent
    ├── Revision
    ├── Human Review
    ├── Finalizer
    └── Diagram Agent
```

This provides visibility into agent execution, LLM calls, latency, token usage, and failures.

---

# API

## Start an Archon Run

```http
POST /api/v1/archon
```

Example:

```json
{
  "user_goal": "Build a RAG based document question answering system"
}
```

The API returns a thread ID identifying the workflow.

## Get Run Status

```http
GET /api/v1/archon/{thread_id}
```

Possible statuses:

```text
running
human_review_required
completed
failed
```

## Resume Human Review

```http
POST /api/v1/archon/{thread_id}/resume
```

Example:

```json
{
  "decision": "approve",
  "feedback": "The architecture looks appropriate."
}
```

Possible decisions:

```text
approve
revise
reject
```

---

# Project Structure

```text
archon-ai-engineering-architect/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── backend/
│   ├── app/
│   │   ├── API/
│   │   │   ├── routes/
│   │   │   │   └── archon.py
│   │   │   └── services/
│   │   │       └── archon_service.py
│   │   ├── agents.py
│   │   ├── graph.py
│   │   ├── llm.py
│   │   ├── models.py
│   │   ├── state.py
│   │   └── main.py
│   │
│   ├── mcp_server/
│   ├── evaluation/
│   │   ├── datasets/
│   │   ├── results/
│   │   ├── runner.py
│   │   ├── scorer.py
│   │   ├── judge.py
│   │   ├── deepeval_demo.py
│   │   └── archon_quality.py
│   │
│   ├── tests/
│   │   └── test_smoke.py
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/
│   ├── app/
│   │   └── page.tsx
│   ├── components/
│   │   ├── archon/
│   │   └── ui/
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── types/
│   │   └── archon.ts
│   ├── package.json
│   └── vercel.json
│
├── .gitignore
└── README.md
```

---

# Local Development

## Prerequisites

- Python 3.12
- Node.js
- PostgreSQL
- Groq API key
- Tavily API key
- LangSmith API key

## Backend

```bash
cd backend
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts ctivate
```

Install dependencies:

```bash
pip install -e .
```

Create `backend/.env`:

```env
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
DATABASE_URL=your_postgresql_connection_string

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=archon-production
```

Start the backend:

```bash
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

## Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the frontend:

```bash
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# CI/CD

The project uses GitHub Actions for automated validation.

```text
                         GitHub
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       Backend Pipeline          Frontend Pipeline
              │                         │
              ▼                         ▼
           Render                    Vercel
```

---

# Engineering Decisions

## Why LangGraph?

The workflow requires conditional routing, stateful execution, iterative revisions, human interrupts, resumable execution, and persistent checkpoints.

## Why Multiple Agents?

Architecture design contains distinct responsibilities. Separating Requirements, Technology Research, Critique, Finalization, and Diagram Extraction makes the workflow easier to reason about and modify.

## Why a Critic Agent?

A dedicated Critic provides an explicit verification stage rather than relying on the same generation step to judge its own output.

## Why Human-in-the-Loop?

Architecture decisions can involve business requirements, constraints, or preferences that automated reasoning may not fully capture.

## Why PostgreSQL?

The workflow requires persistent LangGraph checkpoints so runs can be resumed using their thread IDs.

## Why React Flow?

The backend generates a structured graph representation while the frontend handles visualization, separating architecture reasoning from visualization.

---

# Known Limitations

- Some strict structured-output LLM calls can occasionally fail because of model-side output variability.
- The system depends on external LLM and web-search providers, so provider availability, quotas, latency, and model behavior can affect individual runs.
- The Render free-tier deployment may experience cold starts after periods of inactivity.
- The project is designed primarily as a portfolio and demonstration system rather than a large-scale enterprise platform.

---

# Future Improvements

- More robust structured-output retry and fallback handling
- Improved automatic diagram layout using Dagre or ELK
- Expanded evaluation datasets
- More comprehensive automated regression testing
- Authentication and multi-user support
- More detailed cost and latency tracking

---

# Project Status

- [x] Multi-agent architecture workflow
- [x] LangGraph orchestration
- [x] Requirements & architecture generation
- [x] Technology research
- [x] MCP integration
- [x] Critic and revision loop
- [x] Human-in-the-loop
- [x] PostgreSQL checkpoint persistence
- [x] Final architecture blueprint
- [x] Structured architecture diagram
- [x] React Flow visualization
- [x] FastAPI backend
- [x] Next.js frontend
- [x] Docker
- [x] Evaluation pipeline
- [x] LangSmith observability
- [x] CI/CD
- [x] Production deployment

---

# Author

Built as an AI Engineering portfolio project focused on:

**Agentic AI · LLM Applications · LangGraph · MCP · Evaluation · Production AI Systems**
