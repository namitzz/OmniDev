# OmniDev

## Autonomous Software Engineer Agent Framework

OmniDev provides comprehensive guidelines and specifications for building autonomous software engineer agents that operate within real GitHub development workflows.

### Overview

This repository contains detailed documentation for implementing AI agents that can:
- Receive and understand development tickets
- Analyze existing codebases and repository metadata
- Plan and implement code changes following best practices
- Generate production-ready, testable Git patches
- Operate with the precision and judgment of senior developers

### Documentation

- **[Software Engineer Agent Guidelines](SOFTWARE_ENGINEER_AGENT_GUIDELINES.md)** - Complete specification for autonomous software engineer agents, including:
  - Role and principles
  - Input/output format specifications
  - Best practices and patterns
  - Policy flags and constraints
  - Examples and troubleshooting

### Key Features

#### 🎯 **Production-Ready Code**
Agents produce code that compiles, runs, and passes all tests - never pseudocode or incomplete implementations.

#### 🔧 **Surgical Precision**
Changes are minimal and targeted, modifying only what's necessary to address the specific issue.

#### 📋 **Clean Git Patches**
All outputs are unified diffs in git patch format that can be applied cleanly without conflicts.

#### 🏛️ **Repository Convention Respect**
Agents automatically adapt to existing code style, naming conventions, and architectural patterns.

#### 🔒 **Conservative Dependency Management**
New dependencies are only introduced when explicitly allowed and properly justified.

#### ✅ **Test Integrity**
Existing tests are preserved and enhanced, never deleted without explicit instruction.

### Agent Input Format

Agents receive structured input including:
- **Ticket Description**: Objectives, constraints, and acceptance criteria
- **Code Context**: File snippets, repository structure, and style guides
- **Test Results**: Test output, lint logs, and build results (optional)
- **Policy Flags**: Configuration parameters like `LOC_CAP`, `ALLOW_NEW_DEPS`, etc.

### Agent Output Format

Agents provide standardized output:
1. Executive summary of changes
2. Analysis and reasoning
3. Detailed change descriptions
4. Test plan and coverage
5. Unified diff patches
6. Verification checklist
7. Risks and deployment notes

### Policy Flags

Configure agent behavior with policy flags:
- `LOC_CAP=<number>`: Maximum lines of code per file
- `ALLOW_NEW_DEPS=<true|false>`: Whether new dependencies can be added
- `TEST_COVERAGE_MIN=<percentage>`: Minimum required test coverage
- `BREAKING_CHANGES_ALLOWED=<true|false>`: Whether backwards-incompatible changes are permitted

### Use Cases

- **Automated Bug Fixes**: Analyze issues and generate patches to fix bugs
- **Feature Implementation**: Implement new features following specifications
- **Code Refactoring**: Improve code quality while maintaining functionality
- **Test Coverage**: Add tests to improve coverage in specific areas
- **Security Patches**: Address security vulnerabilities systematically

### Getting Started

1. Review the [Software Engineer Agent Guidelines](SOFTWARE_ENGINEER_AGENT_GUIDELINES.md)
2. Understand the input format your agent will receive
3. Implement the output format specification
4. Follow the workflow process and best practices
5. Test with example tickets and scenarios

### Contributing

Contributions to improve these guidelines are welcome. Please ensure any changes:
- Maintain clarity and precision
- Include practical examples
- Consider real-world development scenarios
- Follow the existing documentation structure

### License

This project is open source and available for use in building autonomous software engineering agents.

### Support

For questions, issues, or suggestions regarding these guidelines, please open an issue in this repository.