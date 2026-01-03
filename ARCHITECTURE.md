# 🚀 DevHive - Autonomous AI Development Team

> **Production-ready AI system that replaces a 5-developer team**

DevHive is an autonomous software engineering system that handles the complete software development lifecycle—from planning and implementation to testing, review, and deployment.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Security](#-security)
- [Known Limitations](#-known-limitations)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)

---

## 🎯 Overview

DevHive autonomously handles development tasks by coordinating specialized AI agents:

- **PlannerAgent**: Creates detailed implementation plans
- **FeatureDevAgent**: Writes production-ready code
- **TesterAgent**: Generates comprehensive tests
- **RefactorAgent**: Improves code quality
- **ReviewerAgent**: Performs security and quality reviews

### What DevHive Does

✅ Ingests GitHub issues and creates implementation plans  
✅ Writes clean, tested, production-ready code  
✅ Performs static analysis and security scanning  
✅ Opens and manages pull requests  
✅ Integrates with CI/CD pipelines  
✅ Provides full observability and cost tracking  

### What DevHive Doesn't Do

❌ Deploy to production without human approval  
❌ Make architectural decisions beyond issue scope  
❌ Modify infrastructure without explicit permission  
❌ Handle merge conflicts automatically  

---

## ✨ Features

### 🤖 Multi-Agent Architecture
- Five specialized agents working in coordination
- Each agent has focused responsibilities
- Fail-safe design with human escalation

### 📚 Repository Intelligence
- Full-repo indexing with vector search (RAG)
- AST-level code understanding with Tree-sitter
- Fast keyword search with ripgrep
- Automatic convention detection

### 🔐 Security & Policies
- Configurable guardrails and policies
- Static analysis (ruff, bandit)
- Security scanning (gitleaks)
- Dependency auditing
- LOC limits per PR

### 📊 Observability
- Structured logging with run IDs
- Token and cost tracking
- Prometheus metrics export
- Full execution timeline

### 🎨 Modern Dashboard
- Real-time task monitoring
- Live logs viewer
- Interactive diff viewer
- Control panel (approve/retry/cancel)
- Metrics visualization

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Integration                     │
│              (Issues, PRs, Comments, Reviews)             │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                        │
│                    (agent-hub/)                           │
├─────────────────────────────────────────────────────────┤
│  Task Runner (Orchestrator)                               │
│  ├─ PlannerAgent      → Creates implementation plan      │
│  ├─ FeatureDevAgent   → Writes code                      │
│  ├─ TesterAgent       → Generates tests                  │
│  ├─ RefactorAgent     → Improves quality                 │
│  └─ ReviewerAgent     → Final review & approval          │
├─────────────────────────────────────────────────────────┤
│  Supporting Systems:                                      │
│  ├─ RAG (Vector DB)   → Semantic code search            │
│  ├─ Git Operations    → Local git management            │
│  ├─ Policy Engine     → Enforces guardrails             │
│  └─ Indexer           → Repository intelligence         │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Next.js Dashboard                       │
│              Real-time monitoring & controls              │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Issue Ingestion**: GitHub issue triggers task creation
2. **Planning**: PlannerAgent analyzes and creates plan
3. **Implementation**: FeatureDevAgent writes code
4. **Testing**: TesterAgent generates tests
5. **Review**: ReviewerAgent validates changes
6. **PR Creation**: Changes pushed as pull request
7. **Human Review**: Team reviews and merges

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- OpenAI API key or Anthropic API key
- GitHub Personal Access Token

### 1. Clone Repository

```bash
git clone https://github.com/your-org/OmniDev.git
cd OmniDev
```

### 2. Set Up Environment

```bash
# Copy and configure environment variables
cp .env.sample .env
# Edit .env with your API keys and configuration
```

### 3. Install Backend Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd dashboard
npm install
cd ..
```

### 5. Initialize Database

```bash
# The database will be automatically initialized on first run
```

### 6. Start Services

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
cd agent-hub
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd dashboard
npm run dev
```

### 7. Access Dashboard

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🔧 Installation

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio black ruff

# Install pre-commit hooks (recommended)
pip install pre-commit
pre-commit install
```

### Production Setup

```bash
# Use production WSGI server
pip install gunicorn

# Run backend
gunicorn agent-hub.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Build frontend
cd dashboard
npm run build
npm start
```

### Docker Setup (Optional)

```bash
# Coming soon
docker-compose up -d
```

---

## ⚙️ Configuration

### Required Environment Variables

```bash
# API Keys
OPENAI_API_KEY=sk-...                    # Required
GITHUB_TOKEN=ghp_...                     # Required
GITHUB_OWNER=your-org                    # Required
GITHUB_REPO=your-repo                    # Required

# Application
APP_NAME=DevHive                         # DevHive, AutoForge, or MergeMind
ENVIRONMENT=production                   # development, staging, production
```

### Policy Configuration

```bash
# Guardrails
MAX_LOC_PER_PR=500                       # Maximum lines per PR
ALLOW_NEW_DEPS=false                     # Allow new dependencies
MIN_TEST_COVERAGE=80                     # Minimum coverage %
ALLOW_BREAKING_CHANGES=false             # Allow breaking changes
MAX_RETRY_ATTEMPTS=3                     # Max retry count
```

### Model Configuration

```bash
# Models per agent
PLANNER_MODEL=gpt-4-turbo-preview
FEATURE_DEV_MODEL=gpt-4-turbo-preview
TESTER_MODEL=gpt-4-turbo-preview
REFACTOR_MODEL=gpt-4-turbo-preview
REVIEWER_MODEL=gpt-4-turbo-preview

# Generation settings
CODE_GENERATION_TEMPERATURE=0.2          # 0.0-1.0
MAX_TOKENS_PER_RESPONSE=4000
```

See [.env.sample](.env.sample) for all available options.

---

## 📖 Usage

### Creating a Task from GitHub Issue

**Via Dashboard:**
1. Click "New Task" button
2. Enter GitHub issue number
3. Task starts automatically

**Via API:**
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"issue_number": 42}'
```

**Via GitHub Webhook:**
Set up webhook pointing to `/webhook/github` to auto-create tasks.

### Monitoring Task Progress

- **Dashboard**: Real-time updates on task status
- **API**: `GET /tasks/{task_id}` for programmatic access
- **Logs**: Check `./logs/omnidev.log` for detailed logs

### Reviewing Agent Output

1. Agents create a branch: `devhive/issue-{number}`
2. Changes are committed with conventional commits
3. PR is automatically opened
4. Review and merge when ready

---

## 📚 API Documentation

### Base URL

```
http://localhost:8000
```

### Endpoints

#### Create Task
```http
POST /tasks
Content-Type: application/json

{
  "issue_number": 42,
  "priority": "normal"
}
```

#### Get Task Status
```http
GET /tasks/{task_id}
```

#### List Tasks
```http
GET /tasks?status=in_progress&limit=50
```

#### Retry Task
```http
POST /tasks/{task_id}/retry
```

#### Cancel Task
```http
POST /tasks/{task_id}/cancel
```

#### Get Metrics
```http
GET /metrics
```

#### Health Check
```http
GET /health
```

### Full API Docs

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger documentation.

---

## 🛠️ Development

### Running Tests

```bash
# Backend tests
pytest tests/ -v

# Frontend tests
cd dashboard
npm test
```

### Code Quality

```bash
# Linting
ruff check agent-hub/
black --check agent-hub/

# Format code
black agent-hub/
ruff --fix agent-hub/
```

### Adding a New Agent

1. Create agent class in `agent-hub/agents/`
2. Extend `BaseAgent`
3. Implement `get_system_prompt()` and `process()`
4. Register in `TaskRunner`
5. Add tests

---

## 🔒 Security

### Best Practices

- ✅ Never commit API keys or secrets
- ✅ Use environment variables for sensitive data
- ✅ Review all code changes before merging
- ✅ Enable security scanning in policies
- ✅ Limit agent permissions appropriately

### Security Scanning

DevHive includes:
- Static analysis with `ruff` and `bandit`
- Secret detection with `gitleaks`
- Dependency vulnerability scanning with `safety`

### Reporting Security Issues

Email: security@yourcompany.com  
Please do not open public issues for security vulnerabilities.

---

## ⚠️ Known Limitations

1. **No Merge Conflict Resolution**: Human intervention required
2. **Single Repository Focus**: One repo per instance
3. **No Infrastructure Changes**: Agents won't modify CI/CD or deployment configs
4. **English Only**: Currently supports English issues/code
5. **Token Costs**: Can be expensive with GPT-4 for large tasks
6. **Rate Limits**: Subject to GitHub and LLM API rate limits

---

## 🗺️ Roadmap

### v2.0 (Q2 2024)

- [ ] Multi-repository support
- [ ] Custom agent creation UI
- [ ] Advanced conflict resolution
- [ ] Support for more languages (Python, Go, Rust, Java)
- [ ] Integration with Jira, Linear, Asana
- [ ] Local LLM support (Llama 2, Mistral)

### v3.0 (Q3 2024)

- [ ] Autonomous merge conflict resolution
- [ ] Infrastructure-as-code modifications
- [ ] Multi-language support (Spanish, French, German)
- [ ] Advanced cost optimization
- [ ] Team collaboration features
- [ ] Enterprise SSO integration

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- OpenAI for GPT-4
- Anthropic for Claude
- FastAPI framework
- Next.js framework
- The open-source community

---

## 📞 Support

- **Documentation**: [docs.yourcompany.com](https://docs.yourcompany.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/OmniDev/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/OmniDev/discussions)
- **Email**: support@yourcompany.com

---

**Built with ❤️ by the DevHive team**
