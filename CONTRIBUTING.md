# Contributing to Mordzix AI

Thank you for your interest in contributing to Mordzix AI! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### 1. Fork the Repository
- Click the "Fork" button on the GitHub repository page
- Clone your fork locally:
```bash
git clone https://github.com/your-username/mordzix-ai.git
cd mordzix-ai
```

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Changes
- Write clean, readable code
- Follow the existing code style
- Add comments for complex logic
- Update documentation if needed

### 4. Test Your Changes
```bash
# Run tests
python -m pytest tests/

# Check code style
python -m flake8 core/

# Test the API
python test_api.py
```

### 5. Commit Changes
```bash
git add .
git commit -m "Add: brief description of changes"
```

### 6. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```
Then create a Pull Request on GitHub.

## 📋 Code Style Guidelines

### Python
- Follow PEP 8
- Use type hints
- Write docstrings for functions
- Use meaningful variable names

### JavaScript
- Use modern ES6+ features
- Follow consistent indentation
- Use meaningful variable names
- Add comments for complex logic

### HTML/CSS
- Use semantic HTML
- Follow BEM methodology for CSS
- Use CSS custom properties
- Ensure responsive design

## 🧪 Testing

### Running Tests
```bash
# All tests
python -m pytest

# Specific test file
python -m pytest tests/test_api.py

# With coverage
python -m pytest --cov=core
```

### Writing Tests
- Test new features
- Test bug fixes
- Test edge cases
- Aim for high coverage

## 📝 Documentation

### Code Documentation
- Use docstrings for functions
- Add inline comments for complex logic
- Update README if needed

### API Documentation
- Document new endpoints
- Provide examples
- Update OpenAPI schema

## 🐛 Bug Reports

When reporting bugs, please include:
- Description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details
- Screenshots (if applicable)

## 💡 Feature Requests

When requesting features, please include:
- Description of the feature
- Use case
- Proposed implementation
- Benefits

## 🔍 Code Review Process

1. All submissions require review
2. Reviewers will check:
   - Code quality
   - Tests
   - Documentation
   - Performance
   - Security

3. Address feedback promptly
4. Keep commits clean and focused

## 🚀 Release Process

1. Version bump
2. Update CHANGELOG.md
3. Create release notes
4. Tag the release
5. Deploy to production

## 📞 Getting Help

- **Discord**: [Join our community](https://discord.gg/mordzix)
- **Issues**: [GitHub Issues](https://github.com/mordzix-ai/issues)
- **Email**: dev@mordzix-ai.com

## 🎯 Development Roadmap

### Current Priorities
- [ ] Performance optimization
- [ ] Additional AI models
- [ ] Mobile responsiveness
- [ ] Plugin system

### Future Features
- [ ] Multi-user support
- [ ] Advanced analytics
- [ ] API marketplace
- [ ] Enterprise features

## 📊 Project Structure

```
mordzix-ai/
├── core/                 # Core functionality
├── frontend/             # Frontend files
├── tests/                # Test files
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── requirements.txt      # Python dependencies
├── app.py               # Main application
└── README.md            # Project documentation
```

## 🔧 Development Setup

### Prerequisites
- Python 3.8+
- Git
- Code editor (VS Code recommended)

### Setup
```bash
# Clone repository
git clone https://github.com/mordzix-ai/mordzix-ai.git
cd mordzix-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
python app.py
```

## 🎉 Recognition

Contributors will be recognized in:
- README.md
- Release notes
- Project documentation
- Community highlights

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Mordzix AI! 🚀