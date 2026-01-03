# 🚀 DevHive - Autonomous AI Development Team

> **Production-ready AI system that replaces a 5-developer team**

DevHive is an autonomous software engineering system that handles the complete software development lifecycle—from planning and implementation to testing, review, and deployment.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Documentation](#-documentation)
- [Architecture](#-architecture)
- [Contributing](#-contributing)
- [License](#-license)

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

---

## ✨ Features

### 🤖 Multi-Agent Architecture
Five specialized agents working in coordination with focused responsibilities and fail-safe design.

### 📚 Repository Intelligence
Full-repo indexing with vector search (RAG), AST-level code understanding, and automatic convention detection.

### 🔐 Security & Policies
Configurable guardrails, static analysis, security scanning, and dependency auditing.

### 📊 Observability
Structured logging, token/cost tracking, and Prometheus metrics export.

### 🎨 Modern Dashboard
Real-time task monitoring, live logs, interactive diff viewer, and metrics visualization.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- OpenAI API key or Anthropic API key
- GitHub Personal Access Token

### Installation

```bash
# Clone repository
git clone https://github.com/namitzz/OmniDev.git
cd OmniDev

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Edit .env with your API keys
nano .env

# Start services
chmod +x scripts/start.sh
./scripts/start.sh
```

### Access Dashboard

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📚 Documentation

- **[Architecture Guide](ARCHITECTURE.md)** - Complete system architecture and design
- **[Software Engineer Agent Guidelines](SOFTWARE_ENGINEER_AGENT_GUIDELINES.md)** - Agent specifications
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)

---

## 🏗️ Architecture

```
GitHub Integration
        ↓
  FastAPI Backend
  ├─ PlannerAgent
  ├─ FeatureDevAgent
  ├─ TesterAgent
  ├─ RefactorAgent
  └─ ReviewerAgent
        ↓
   Next.js Dashboard
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [SOFTWARE_ENGINEER_AGENT_GUIDELINES.md](SOFTWARE_ENGINEER_AGENT_GUIDELINES.md) for coding standards.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/namitzz/OmniDev/issues)
- **Discussions**: [GitHub Discussions](https://github.com/namitzz/OmniDev/discussions)

---

**Built with ❤️ for autonomous software development**