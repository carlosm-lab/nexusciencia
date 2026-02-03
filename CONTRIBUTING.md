# Contributing to NexusCiencia

## 🎯 Development Setup

### Prerequisites
- Python 3.11+
- Virtual environment
- MySQL/SQLite

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/nexusciencia.git
cd nexusciencia

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Run migrations
flask db upgrade

# Run application
python run.py
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html tests/

# Coverage target: >70%
```

## 📝 Code Style

**Python:**
- Follow PEP 8
- Use `black` for formatting: `black app/ tests/`
- Use `flake8` for linting: `flake8 app/ tests/ --max-line-length=120`
- Use `isort` for imports: `isort app/ tests/`

**JavaScript:**
- ES6+ syntax
- Consistent naming (camelCase for variables, PascalCase for classes)

**CSS:**
- Use existing design system variables
- Mobile-first approach

## 🔀 Pull Request Process

1. **Fork** the repository
2. **Create branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** with clear, descriptive commits
4. **Run tests**: `pytest -v` (must pass)
5. **Run linters**:
   ```bash
   black app/ tests/
   flake8 app/ tests/
   isort app/ tests/
   ```
6. **Update documentation** if needed
7. **Push**: `git push origin feature/amazing-feature`
8. **Open PR** with description of changes

## ✅ PR Checklist

- [ ] Tests pass (`pytest`)
- [ ] Coverage >70% (`pytest --cov`)
- [ ] No lint errors (`flake8`)
- [ ] Code formatted (`black`)
- [ ] Imports sorted (`isort`)
- [ ] Documentation updated
- [ ] Commit messages are clear

## 🐛 Reporting Bugs

**Include:**
- OS and Python version
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs
- Screenshots if applicable

## 💡 Suggesting Features

**Provide:**
- Clear use case
- Expected behavior
- Why it's beneficial
- Implementation ideas (optional)

## 📖 Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add comments for complex logic

## 🔐 Security

Report security vulnerabilities privately to: security@nexusciencia.com

**Do not** create public issues for security problems.

---

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on collaboration

Thank you for contributing to NexusCiencia! 🚀
