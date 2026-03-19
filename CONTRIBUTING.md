# Contributing Guide

Thanks for contributing.

## 1. Fork and Branch

Create a topic branch for each change:

```bash
git checkout -b feature/short-description
```

## 2. Keep Changes Focused

- One feature or fix per pull request
- Update README or comments when behavior changes
- Avoid unrelated formatting changes

## 3. Local Validation

Run the relevant project before opening a pull request.

Kakurasu:

```bash
cd kakurasu/Kakurasu-Game-With-AI-Solver-Using-Propositional-Logic
python kakurasu.py
```

Pipes:

```bash
cd pipes
python main_pipes.py
```

## 4. Commit Style

Use clear commit messages:

- `docs: improve pipes setup section`
- `fix: handle missing level file in load_level`
- `feat: add new sample input`

## 5. Pull Request Checklist

- [ ] Code runs without errors
- [ ] README/docs updated (if needed)
- [ ] No large generated files added
- [ ] Input/output examples included for new features

## 6. Reporting Bugs

Please include:

- Environment (OS, Python version)
- Steps to reproduce
- Expected behavior
- Actual behavior
- Console error output
