# 🛡️ NeuraGuard — Enterprise Agentic AI Control & Governance Platform

[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg?logo=streamlit)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-LangGraph-00A67E.svg)](https://www.langchain.com/)
[![Pinecone Vector DB](https://img.shields.io/badge/Pinecone-VectorDB-000000.svg)](https://www.pinecone.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **NeuraGuard** is a state-of-the-art Enterprise Agentic AI Control Platform designed for real-time AI governance, multi-agent orchestration (LangGraph), 11-pipeline RAG evaluation, FinOps cost management, automated incident self-healing, and human-in-the-loop oversight.

---

## ⚡ Key Highlights & Core Capabilities

| Capability | Module & Location | Description |
| :--- | :--- | :--- |
| **🔍 11 RAG Pipelines** | [`app/rag/strategies.py`](file:///d:/Azure/aegis-ai/app/rag/strategies.py) | Naive, Advanced, Hybrid, Agentic, Multi-Agent, Graph, Multimodal, Conversational, Self-RAG, Corrective & Modular RAG. |
| **🤖 8 LangGraph Agents** | [`app/agents/`](file:///d:/Azure/aegis-ai/app/agents/) | Supervisor, Research, RAG, Data Analysis, Vision, Compliance, Risk, Verification with dynamic routing. |
| **🛡️ Governance Engine** | [`app/governance/`](file:///d:/Azure/aegis-ai/app/governance/) | PII detection, Prompt Injection guardrails, Jailbreak prevention, YAML policy engine (`policies/policies.yaml`). |
| **🧪 Automated Red-Teaming** | [`app/redteam/attacks.py`](file:///d:/Azure/aegis-ai/app/redteam/attacks.py) | 10 automated attack vectors (jailbreaks, secret exfiltration, instruction hijacking). |
| **📊 Observability & Tracing** | [`app/observability/`](file:///d:/Azure/aegis-ai/app/observability/) | Request/agent/LLM latency timelines, error tracking, circuit breakers & retries. |
| **💰 FinOps & Token Cost** | [`app/finops/cost.py`](file:///d:/Azure/aegis-ai/app/finops/cost.py) | Token/cost tracking per agent & workflow, cost anomaly alerts, model optimization tips. |
| **🚨 Incident Self-Healing** | [`app/incidents/engine.py`](file:///d:/Azure/aegis-ai/app/incidents/engine.py) | Auto-detects failure/latency spikes, triggers self-healing chain (Retry ➔ Fallback ➔ Human Escalation). |
| **👤 Human-in-the-Loop** | [`app/memory/approval_queue.py`](file:///d:/Azure/aegis-ai/app/memory/approval_queue.py) | `REVIEW_REQUIRED` requests are queued for mandatory human approval/rejection. |
| **🖥️ Control Plane UI** | [`streamlit_app/`](file:///d:/Azure/aegis-ai/streamlit_app/) | 9 interactive dark glassmorphism dashboard pages. |

---

## 🛠️ Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          👤  User / Enterprise Client                               │
└───────────────────────────────────────┬─────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│              🖥️  NeuraGuard Streamlit Control Plane  (Port 8501)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │💬 AI Chat│ │🔍 RAG    │ │🤖 Agents │ │🛡️ Govern.│ │🧪 Eval.  │ │📊 Observ.│   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                                            │
│  │💰 FinOps │ │🚨 Incid. │ │👤 Human  │                                            │
│  └──────────┘ └──────────┘ └──────────┘                                            │
└───────────────────────────────────────┬─────────────────────────────────────────────┘
                                        │ HTTP / REST
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                  ⚙️  FastAPI Governance Backend  (Port 8000)                         │
│  /chat  /rag/*  /agents/*  /governance/*  /evaluation/*  /finops/*                 │
│  /incidents/*  /approvals/*  /rag/status  /rag/documents  /documents/upload        │
└───────┬───────────────┬───────────────┬───────────────┬───────────────┬─────────────┘
        │               │               │               │               │
        ▼               ▼               ▼               ▼               ▼
┌───────────────┐ ┌─────────────┐ ┌───────────────┐ ┌───────────┐ ┌───────────────┐
│ 🛡️ Governance │ │ 🤖 LangGraph│ │ 🔍 RAG Engine │ │ 📊 Observ │ │ 💰 FinOps     │
│ & Risk Engine │ │ Multi-Agent │ │ 11 Strategies │ │ & Tracing │ │ & Cost Track  │
│               │ │  Workflow   │ │               │ │           │ │               │
│ detectors.py  │ │ graph.py    │ │ naive         │ │ tracing.py│ │ cost.py       │
│ • PII Scanner │ │ state.py    │ │ advanced      │ │ • Latency │ │ • Token usage │
│ • Inj. Guard  │ │             │ │ hybrid        │ │ • Errors  │ │ • Per-agent $ │
│ guardrails.py │ │ agents.py   │ │ agentic       │ │ • Traces  │ │ • Anomalies   │
│ • Claim Verif │ │ 8 Agents:   │ │ multi_agent   │ │           │ │ • Budget tips │
│ • Jailbreak   │ │ Supervisor  │ │ graph         │ │ reliab.py │ │               │
│ policy.py     │ │ Research    │ │ multimodal    │ │ • Circuit │ │               │
│ • YAML Rules  │ │ RAG         │ │ conversational│ │   Breaker │ │               │
│ • NIST AI RMF │ │ Data Analy. │ │ self_rag      │ │ • Retries │ │               │
│ risk.py       │ │ Vision      │ │ corrective    │ │           │ │               │
│ • Risk Score  │ │ Compliance  │ │ modular       │ │           │ │               │
│ • Block/Review│ │ Risk        │ │               │ │           │ │               │
│               │ │ Verification│ │ vectorstore.py│ │           │ │               │
└───────┬───────┘ └──────┬──────┘ │ embeddings.py │ └───────────┘ └───────────────┘
        │                │        │ reranker.py   │
        │                │        │ ingestion.py  │
        ▼                ▼        └───────┬───────┘
┌───────────────┐ ┌─────────────┐         │
│ 🧪 Evaluation │ │ 🚨 Incidents│         ▼
│   Engine      │ │ Self-Healing│ ┌───────────────┐   ┌───────────────┐
│               │ │             │ │  🗄️ Pinecone  │   │  📂 In-Memory │
│ evaluator.py  │ │ engine.py   │ │  Vector DB    │   │  VectorStore  │
│ • Groundedness│ │ • Failure   │ │  (Cloud RAG)  │   │  (MOCK_MODE)  │
│ • Safety Score│ │   Detection │ └───────────────┘   └───────────────┘
│ • RAGAS-style │ │ • Retry     │
│ • CI/CD Gate  │ │ • Fallback  │ ┌──────────────────────────────────┐
│               │ │ • Escalate  │ │  🔧 Shared Tools & Infra         │
└───────────────┘ └──────┬──────┘ │  tools/llm_client.py             │
                          │        │  • Groq LLM (openai/gpt-oss-120b)│
┌───────────────┐         │        │  • Fallback Model (-20b)         │
│ 👤 Human      │         │        │  • MOCK_MODE stub                │
│ Approval Queue│◄────────┘        │                                  │
│               │                  │  app/storage.py                  │
│ approval_     │                  │  • Incident store (JSON)         │
│ queue.py      │                  │  • Approval queue (JSON)         │
│ REVIEW_REQUIRED                  │  • Audit log (JSON)              │
│ Approve/Reject│                  └──────────────────────────────────┘
└───────────────┘
                         ┌──────────────────────────────────────────┐
                         │  🧨 Automated Red-Teaming                │
                         │  app/redteam/attacks.py                  │
                         │  10 attack vectors:                      │
                         │  Jailbreak · Prompt Injection            │
                         │  Secret Exfiltration · Role Hijacking    │
                         │  DAN · Token Overflow · Encoding Bypass  │
                         │  Multi-turn Manipulation · Tool Abuse    │
                         │  Instruction Hijacking                   │
                         └──────────────────────────────────────────┘

                         ┌──────────────────────────────────────────┐
                         │  📋 Policy & Compliance Engine            │
                         │  policies/policies.yaml                  │
                         │  NIST.AI.100-1.pdf (NIST AI RMF)        │
                         │  evaluation_datasets/ (RAGAS benchmarks) │
                         └──────────────────────────────────────────┘
```

---

## 🚀 Quickstart & Local Setup

### 1. Clone & Environment Setup

```bash
git clone https://github.com/Vaibhavsable451/NeuraGuard-Enterprise-Agentic-AI-Control-Governance-Platform.git
cd NeuraGuard-Enterprise-Agentic-AI-Control-Governance-Platform

# Create virtual environment
python -m venv .venv
# Activate: Windows: .venv\Scripts\activate | Linux/macOS: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment configuration
cp .env.example .env
```

### 2. Configure Environment (`.env`)

Open `.env` and configure your API keys:

```env
# --- App Mode ---
MOCK_MODE=false              # false = call live Groq/Pinecone; true = deterministic local mock

# --- Primary LLM Provider (Groq) ---
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
GROQ_FALLBACK_MODEL=openai/gpt-oss-20b

# --- Vector Store (Pinecone) ---
PINECONE_API_KEY=pcsk_your_pinecone_api_key_here
PINECONE_INDEX_NAME=neuraguard-index
```

### 3. Start Backend & Frontend

```bash
# Terminal 1: Launch FastAPI Backend Server (Port 8000)
uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Launch Streamlit Control Plane UI (Port 8501)
uv run streamlit run streamlit_app/app.py --server.port 8501
```

Access the UI at: **`http://localhost:8501`**  
Access Swagger Docs at: **`http://127.0.0.1:8000/docs`**

---

## 🧪 Testing & Evaluation Suite

Run the full automated test suite (23 unit, integration & security tests):

```bash
# Run pytest test suite
uv run pytest

# Run CI/CD evaluation gate locally
uv run python scripts/run_evaluation_gate.py
```

---

## ☁️ Continuous Deployment to AWS EC2

This repository automatically deploys to an **AWS EC2** instance via SSH using GitHub Actions (`.github/workflows/deploy.yml`) upon successful completion of both **CI** and **Evaluation Gate** workflows on the `main` branch.

### Required GitHub Repository Secrets

Configure the following secrets under **Settings > Secrets and variables > Actions**:

| Secret | Description | Example |
| :--- | :--- | :--- |
| `EC2_HOST` | Public IP or DNS of your AWS EC2 instance | `54.210.12.34` or `ec2-xx.compute-1.amazonaws.com` |
| `EC2_USER` | SSH login username | `ubuntu` or `ec2-user` |
| `EC2_SSH_KEY` | Private SSH key (`.pem` file content) | `-----BEGIN RSA PRIVATE KEY-----...` |

### EC2 Security Group & Ports

Ensure the following inbound ports are allowed in your AWS EC2 Security Group:
- `8000`: FastAPI Backend
- `8501`: Streamlit Frontend UI
- `22`: SSH Access for GitHub Actions

### One-Click Startup Script on EC2

To launch or restart services directly on your EC2 instance:
```bash
chmod +x startup.sh
./startup.sh
```


---

## 📊 Dashboard Modules (Streamlit Frontend)

| # | Page | Path | Key Functionality |
| :-: | :--- | :--- | :--- |
| **1** | **💬 AI Chat** | [`pages/1_AI_Chat.py`](file:///d:/Azure/aegis-ai/streamlit_app/pages/1_AI_Chat.py) | Governed multi-agent conversation with risk scores & citations. |
| **2** | **🔍 RAG Playground** | [`pages/2_RAG_Playground.py`](file:///d:/Azure/aegis-ai/streamlit_app/pages/2_RAG_Playground.py) | Real-time comparison across all 11 enterprise RAG retrieval strategies. |
| **3** | **🤖 Agent Control Center** | [`pages/3_Agent_Control_Center.py`](file:///d:/Azure/aegis-ai/streamlit_app/pages/3_Agent_Control_Center.py) | LangGraph execution paths, agent node latency & health tracking. |
| **4** | **🛡️ Governance Dashboard** | [`pages/4_Governance_Dashboard.py`](file:///d:/Azure/aegis-ai/streamlit_app/pages/4_Governance_Dashboard.py) | Real-time PII detection, prompt injection logs & policy violations. |
| **5** | **🧪 Evaluation Dashboard** | [`pages/5_Evaluation_Dashboard.py`](file:///d:/Azure/aegis-ai/streamlit_app/pages/5_Evaluation_Dashboard.py) | Automated RAG groundedness, agent quality & safety scoring. |
| **6** | **📊 Observability** | [`pages/6_Observability_Dashboard.py`](file:///d:/Azure/aegis-ai/streamlit_app/pages/6_Observability_Dashboard.py) | Request metrics, LLM latency histograms & error trace logs. |
| **7** | **💰 FinOps Dashboard** | [`pages/7_FinOps_Dashboard.py`](file:///d:/Azure/aegis-ai/streamlit_app/pages/7_FinOps_Dashboard.py) | Token spend per agent/workflow, cost anomalies & savings tips. |
| **8** | **🚨 Incident Center** | [`pages/8_Incident_Center.py`](file:///d:/Azure/aegis-ai/streamlit_app/pages/8_Incident_Center.py) | Auto-detected incident timelines & self-healing chain triggers. |
| **9** | **👤 Human Approval Queue** | [`pages/9_Human_Approval_Queue.py`](file:///d:/Azure/aegis-ai/streamlit_app/pages/9_Human_Approval_Queue.py) | Mandatory human review queue for `REVIEW_REQUIRED` requests. |

---

## 📡 API Endpoint Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/chat` | Chat through the governed multi-agent pipeline |
| `POST` | `/rag/query` | Run direct RAG queries against any of the 11 strategies |
| `GET` | `/rag/status` | Inspect vector store status (In-Memory / Pinecone) |
| `GET` | `/rag/documents` | List indexed documents & preview chunks |
| `POST` | `/documents/upload` | Ingest new text/PDF document into vector store |
| `POST` | `/agents/run` | Execute LangGraph multi-agent workflow |
| `GET` | `/agents/status` | Retrieve per-agent run, failure & latency statistics |
| `POST` | `/governance/check` | Check text against PII/injection guardrails & calculate risk score |
| `GET` | `/governance/audit` | Retrieve complete governance audit log |
| `POST` | `/evaluation/run` | Run evaluation suite against benchmarks |
| `GET` | `/finops/cost` | Fetch token cost breakdown, anomalies & recommendations |
| `GET` | `/incidents` | List detected security/latency incidents |
| `POST` | `/incidents/{id}/self-heal` | Trigger automated self-healing chain for an incident |
| `GET` | `/approvals` | Fetch pending and historical human approval queue |
| `POST` | `/approvals/{id}/approve` | Approve a flagged request |
| `POST` | `/approvals/{id}/reject` | Reject a flagged request |

---

## 🔒 Security & Best Practices

- **Zero Secret Commits**: `.env` is listed in `.gitignore` so API keys are never pushed to version control.
- **`MOCK_MODE` Fallback**: Runs 100% offline with zero external API dependencies for CI/CD and local development.
- **Fail-Safe Circuit Breakers**: Automatic fallback to secondary models if primary APIs experience latency or rate limits.

---

## 📜 License

Distributed under the **MIT License**.
