# Contributing to Synergos AI

Thank you for your interest in contributing to Synergos AI! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use the issue template** when creating new issues
3. **Provide detailed information** including:
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Browser/OS information
   - Screenshots if applicable

### Suggesting Features

1. **Check the roadmap** to see if the feature is already planned
2. **Create a feature request** with detailed description
3. **Explain the use case** and benefits
4. **Consider implementation complexity**

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch** from `main`
3. **Make your changes** following our coding standards
4. **Write tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

## 🏗️ Development Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- Git

### Local Development

1. Clone your fork:
   ```bash
   git clone https://github.com/your-username/synergos-ai.git
   cd synergos-ai
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python src/main.py
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 📝 Coding Standards

### Python (Backend)

- Follow **PEP 8** style guidelines
- Use **type hints** where appropriate
- Write **docstrings** for functions and classes
- Keep functions **small and focused**
- Use **meaningful variable names**

Example:
```python
def process_document(file_data: str, filename: str) -> dict:
    """
    Process uploaded document and extract relevant information.
    
    Args:
        file_data: Base64 encoded file content
        filename: Original filename
        
    Returns:
        Dictionary containing processed document information
    """
    # Implementation here
    pass
```

### JavaScript/React (Frontend)

- Use **ES6+ features**
- Follow **React best practices**
- Use **functional components** with hooks
- Implement **proper error handling**
- Write **meaningful component names**

Example:
```javascript
const DocumentUpload = ({ interview, onDocumentsUploaded }) => {
  const [uploadStatus, setUploadStatus] = useState({});
  
  const handleFileUpload = async (file, documentType) => {
    try {
      // Implementation here
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };
  
  return (
    // JSX here
  );
};
```

### CSS

- Use **consistent naming conventions**
- Follow **mobile-first approach**
- Use **CSS custom properties** for theming
- Keep **specificity low**
- Group **related styles together**

## 🧪 Testing

### Backend Testing

```bash
cd backend
python -m pytest tests/
```

### Frontend Testing

```bash
cd frontend
npm test
```

### Test Coverage

- Aim for **80%+ test coverage**
- Write **unit tests** for business logic
- Write **integration tests** for API endpoints
- Write **component tests** for React components

## 📚 Documentation

### Code Documentation

- Write **clear comments** for complex logic
- Update **API documentation** for endpoint changes
- Include **usage examples** in README files
- Document **configuration options**

### Commit Messages

Use **conventional commit format**:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Examples:
```
feat(upload): add support for DOCX files
fix(api): resolve CORS issue for file uploads
docs(readme): update installation instructions
```

## 🔄 Pull Request Process

### Before Submitting

1. **Rebase your branch** on the latest `main`
2. **Run all tests** and ensure they pass
3. **Update documentation** if needed
4. **Check code style** compliance
5. **Verify the application works** locally

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Screenshots
(If applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

### Review Process

1. **Automated checks** must pass
2. **At least one reviewer** approval required
3. **Address feedback** promptly
4. **Squash commits** before merging (if requested)

## 🚀 Release Process

### Versioning

We use **Semantic Versioning** (SemVer):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

### Release Checklist

1. Update version numbers
2. Update CHANGELOG.md
3. Create release notes
4. Tag the release
5. Deploy to production
6. Announce the release

## 🏷️ Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `priority-high`: High priority issue
- `priority-low`: Low priority issue

## 💬 Communication

### Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Request Comments**: Code review discussions

### Code of Conduct

- Be **respectful and inclusive**
- **Constructive feedback** only
- **Help others learn** and grow
- **Focus on the code**, not the person

## 🎯 Roadmap

### Current Priorities

1. Enhanced AI question generation
2. Real-time transcription improvements
3. Mobile app development
4. Advanced analytics dashboard

### Future Plans

1. Multi-language support
2. Video interview capabilities
3. Integration with HR systems
4. Advanced reporting features

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Annual contributor highlights

Thank you for contributing to Synergos AI! 🚀

