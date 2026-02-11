# Contributing to Lightweight SIEM

Thank you for your interest in contributing!

## How to Contribute

### Reporting Bugs

- Use GitHub Issues
- Include steps to reproduce
- Provide logs and error messages
- Specify your environment (OS, Docker version, etc.)

### Suggesting Features

- Open a GitHub Issue with "Feature Request" label
- Describe the feature and use case
- Explain why it would be valuable

### Code Contributions

1. **Fork the repository**

2. **Create a feature branch**
```bash
git checkout -b feature/my-new-feature
```

3. **Make your changes**
   - Follow existing code style
   - Add tests
   - Update documentation

4. **Run tests**
```bash
make test
make lint
```

5. **Commit your changes**
```bash
git commit -m "Add feature: description"
```

6. **Push to your fork**
```bash
git push origin feature/my-new-feature
```

7. **Open a Pull Request**

## Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/lightweight-siem.git
cd lightweight-siem

# Install dependencies
make install-deps

# Start in development mode
make dev
```

## Code Style

- Python: Follow PEP 8
- Use Black for formatting
- Run flake8 for linting
- Add type hints where possible

## Testing

- Write unit tests for new features
- Ensure all tests pass
- Aim for >80% code coverage

## Documentation

- Update README.md if needed
- Add docstrings to functions
- Update API documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
