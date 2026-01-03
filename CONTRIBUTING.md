# 🤝 Contributing to DevHive

Thank you for your interest in contributing to DevHive! This document provides guidelines for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Our Standards

**Positive behaviors:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behaviors:**
- Harassment or discriminatory language
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- Familiarity with FastAPI and Next.js

### Ways to Contribute

1. **Bug Reports**: Found a bug? Open an issue!
2. **Feature Requests**: Have an idea? We'd love to hear it!
3. **Code Contributions**: Submit pull requests
4. **Documentation**: Improve our docs
5. **Testing**: Help expand test coverage

---

## 💻 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/OmniDev.git
cd OmniDev
```

### 2. Set Up Development Environment

```bash
# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Or manually:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd dashboard && npm install && cd ..
```

### 3. Configure Environment

```bash
# Copy and edit .env
cp .env.sample .env
# Add your API keys
```

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

---

## 🔧 Making Changes

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `test/` - Test additions/changes
- `refactor/` - Code refactoring

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```bash
# Format
<type>(<scope>): <subject>

# Examples
feat(agents): add retry logic to PlannerAgent
fix(api): resolve race condition in task creation
docs(readme): update installation instructions
test(agents): add unit tests for ReviewerAgent
refactor(rag): optimize vector search performance
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Testing
- `refactor`: Code refactoring
- `style`: Formatting
- `chore`: Maintenance

---

## 📤 Submitting Changes

### Before Submitting

1. **Test Your Changes**
   ```bash
   # Backend tests
   pytest tests/ -v
   
   # Frontend tests
   cd dashboard && npm test
   
   # Linting
   ruff check agent-hub/
   black --check agent-hub/
   ```

2. **Update Documentation**
   - Update README if adding features
   - Add docstrings to new functions
   - Update ARCHITECTURE.md if needed

3. **Check for Breaking Changes**
   - Document any breaking changes
   - Update version appropriately

### Pull Request Process

1. **Push Your Branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Go to GitHub and create a PR
   - Fill out the PR template
   - Link related issues

3. **PR Title Format**
   ```
   [Type] Brief description of changes
   
   Example:
   [Feature] Add support for Claude API
   [Fix] Resolve database connection timeout
   ```

4. **PR Description Should Include:**
   - What changed and why
   - How to test the changes
   - Screenshots (if UI changes)
   - Related issues
   - Breaking changes (if any)

5. **Wait for Review**
   - Address reviewer feedback
   - Keep discussion constructive
   - Be patient and respectful

---

## 📏 Coding Standards

### Python (Backend)

**Style Guide:**
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for all public functions

**Example:**
```python
def calculate_cost(tokens: int, model: str) -> float:
    """
    Calculate the cost of LLM API usage.
    
    Args:
        tokens: Number of tokens used
        model: Model name (e.g., 'gpt-4')
    
    Returns:
        Estimated cost in USD
    """
    rates = {"gpt-4": 0.03}
    return (tokens / 1000) * rates.get(model, 0.01)
```

**Linting:**
```bash
# Format code
black agent-hub/

# Lint code
ruff check agent-hub/
```

### TypeScript (Frontend)

**Style Guide:**
- Use TypeScript strict mode
- Prefer functional components
- Use meaningful component names
- Keep components small and focused

**Example:**
```typescript
interface TaskCardProps {
  task: Task
  onSelect: (id: string) => void
}

export default function TaskCard({ task, onSelect }: TaskCardProps) {
  return (
    <div onClick={() => onSelect(task.id)}>
      <h3>{task.title}</h3>
      <span className={getStatusClass(task.status)}>
        {task.status}
      </span>
    </div>
  )
}
```

**Linting:**
```bash
cd dashboard
npm run lint
```

---

## 🧪 Testing Guidelines

### Writing Tests

**Test Structure:**
```python
def test_feature_behavior():
    """Test that feature behaves correctly"""
    # Arrange
    input_data = create_test_input()
    
    # Act
    result = feature_function(input_data)
    
    # Assert
    assert result.success is True
    assert result.output is not None
```

**Test Coverage:**
- Aim for 80%+ coverage for new code
- Test happy paths and edge cases
- Include error handling tests
- Mock external APIs

**Running Tests:**
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=agent-hub --cov-report=html

# Specific test
pytest tests/test_agents.py::test_planner_agent -v
```

### Test Types

1. **Unit Tests**: Test individual functions/classes
2. **Integration Tests**: Test component interactions
3. **E2E Tests**: Test complete workflows

---

## 📚 Documentation

### Code Documentation

**Docstrings (Python):**
```python
def process_task(task_id: str, options: Dict[str, Any]) -> TaskResult:
    """
    Process a development task through the agent pipeline.
    
    This function coordinates multiple agents to complete a task,
    from planning through implementation to review.
    
    Args:
        task_id: Unique identifier for the task
        options: Configuration options including:
            - priority: Task priority level
            - timeout: Maximum execution time
            - agents: List of agents to use
    
    Returns:
        TaskResult containing:
            - success: Whether task completed successfully
            - output: Task results
            - metrics: Performance metrics
    
    Raises:
        ValueError: If task_id is invalid
        TimeoutError: If task exceeds timeout
        
    Example:
        >>> result = process_task("task-123", {"priority": "high"})
        >>> if result.success:
        ...     print(f"Task completed: {result.output}")
    """
    pass
```

**Comments (TypeScript):**
```typescript
/**
 * Fetches task data from the API
 * 
 * @param taskId - The unique identifier of the task
 * @param options - Optional fetch configuration
 * @returns Promise resolving to task data
 * @throws {Error} If task not found or network error
 */
async function fetchTask(
  taskId: string,
  options?: FetchOptions
): Promise<Task> {
  // Implementation
}
```

### README Updates

When adding features:
1. Update feature list
2. Add usage examples
3. Update screenshots if needed
4. Modify quick start if applicable

---

## 🔍 Review Process

### What Reviewers Look For

1. **Code Quality**
   - Clean, readable code
   - Proper error handling
   - No code smells

2. **Testing**
   - Adequate test coverage
   - Tests pass
   - Edge cases covered

3. **Documentation**
   - Clear docstrings
   - Updated README
   - Code comments where needed

4. **Security**
   - No hardcoded secrets
   - Input validation
   - Safe operations

5. **Performance**
   - No obvious bottlenecks
   - Efficient algorithms
   - Reasonable resource usage

### Review Timeline

- Initial review: Within 2-3 days
- Follow-up reviews: Within 1-2 days
- Approval: After all concerns addressed

---

## 🎯 Good First Issues

Looking to contribute? Check out issues labeled:
- `good first issue`
- `help wanted`
- `documentation`

These are great starting points for new contributors!

---

## 🆘 Getting Help

- **Questions**: Open a discussion on GitHub
- **Bugs**: Open an issue with reproduction steps
- **Features**: Propose in discussions first
- **Chat**: [Discord/Slack link if available]

---

## 📊 Contribution Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- Credits in documentation

Significant contributors may be invited to join the maintainers team.

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to DevHive! 🚀**

Together, we're building the future of autonomous software development.
