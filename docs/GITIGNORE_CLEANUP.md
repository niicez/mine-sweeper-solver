# Gitignore Cleanup Guide

The `.gitignore` file has been created with comprehensive rules to keep your repository clean.

## What Was Added

A comprehensive `.gitignore` file (634 lines) covering:

### Python Cache & Build Files
- `__pycache__/` - Python bytecode cache
- `*.pyc`, `*.pyo` - Compiled Python files
- `build/`, `dist/` - Build artifacts
- `*.egg-info/` - Package metadata

### IDE & Editor Files
- `.idea/` - PyCharm/JetBrains
- `.vscode/` - VS Code
- `*.sublime-*` - Sublime Text
- Vim/Emacs swap files
- Eclipse/Atom/etc.

### Operating System Files
- `.DS_Store` - macOS
- `Thumbs.db` - Windows
- `*~` - Linux backup files

### Development Tools
- `.pytest_cache/` - pytest cache
- `.ruff_cache/` - Ruff linter cache
- `.mypy_cache/` - mypy cache
- `.coverage` - coverage reports
- `htmlcov/` - HTML coverage reports

### Virtual Environments
- `.venv/`, `venv/` - Virtual environments
- `.env` - Environment files (security)

### Security (NEVER commit)
- `.env` files with secrets
- `*.key`, `*.pem` - Private keys
- `.aws/`, credentials
- SSH keys

### Project-Specific
- `.agents/`, `.claude/` - Agent-specific directories
- Test outputs
- Local development files
- Temporary files

## Current Repository Status

The following files are currently tracked in Git but should be ignored:

```
.agents/                    # Agent skill files
.claude/                    # Claude-specific files
.coverage                   # Coverage report (generated)
__pycache__/                # Python cache (multiple directories)
```

## How to Clean Up

### Option 1: Automatic Cleanup (Recommended)

Run this one-time cleanup script:

```bash
# Remove tracked files that should be ignored
git rm -r --cached .agents 2>/dev/null || true
git rm -r --cached .claude 2>/dev/null || true
git rm --cached .coverage 2>/dev/null || true
git rm -r --cached __pycache__ 2>/dev/null || true
git rm -r --cached src/__pycache__ 2>/dev/null || true
git rm -r --cached tests/__pycache__ 2>/dev/null || true
git rm -r --cached tests_ui/__pycache__ 2>/dev/null || true
git rm -r --cached tests_ui/utils/__pycache__ 2>/dev/null || true
git rm -r --cached tests_ui/integration/__pycache__ 2>/dev/null || true
git rm -r --cached tests_ui/e2e/__pycache__ 2>/dev/null || true
git rm -r --cached ui/__pycache__ 2>/dev/null || true

# Stage the .gitignore file
git add .gitignore

# Commit the changes
git commit -m "Add comprehensive .gitignore and remove unnecessary files

- Add enterprise-grade .gitignore (634 lines)
- Remove cached files (__pycache__, .coverage)
- Remove agent-specific directories (.agents, .claude)
- Keep repository clean and focused on source code"
```

### Option 2: Manual Cleanup

```bash
# Step 1: Remove cached files from git (but keep locally)
git rm -r --cached __pycache__
git rm -r --cached .agents
git rm -r --cached .claude
git rm --cached .coverage

# Step 2: Add the .gitignore
git add .gitignore

# Step 3: Check what's staged
git status

# Step 4: Commit
git commit -m "Clean up: Add .gitignore and remove cached files"
```

## What Happens Next

After cleanup:

1. **Cache files won't be tracked** - `__pycache__`, `.pyc` files ignored
2. **Coverage reports ignored** - `.coverage`, `htmlcov/` not tracked
3. **Agent files ignored** - `.agents/`, `.claude/` not tracked
4. **IDE settings ignored** - `.idea/`, `.vscode/` not tracked
5. **Environment files protected** - `.env` files never committed

## Files That Will Be Removed from Git

These files/directories will be removed from Git tracking but kept locally:

- All `__pycache__/` directories
- `.agents/` directory
- `.claude/` directory
- `.coverage` file
- Any `.pyc` files

## Files That Stay in Git

These important files remain:

- `src/` - Source code
- `ui/` - UI code
- `tests/` - Test files
- `tests_ui/` - UI test files
- `docs/` - Documentation
- `scripts/` - Helper scripts
- `.github/` - GitHub workflows
- `pyproject.toml` - Project config
- `requirements*.txt` - Dependencies
- `README.md`, `AGENTS.md` - Documentation
- `.pre-commit-config.yaml` - Pre-commit config

## Best Practices

1. **Always check before committing**:
   ```bash
   git status
   ```

2. **Review what's staged**:
   ```bash
   git diff --cached --name-only
   ```

3. **If you accidentally added ignored files**:
   ```bash
   git rm -r --cached <file-or-directory>
   ```

4. **Keep .gitignore updated** - Add new patterns as needed

## Important Notes

⚠️ **The .agents/ directory** - If these are important skill files you want to keep, you should:
1. Move them to a different location (like `docs/skills/`)
2. Or remove the `.agents/` entry from .gitignore

⚠️ **The .claude/ directory** - Same as above. These are typically IDE-specific.

## Verification

After cleanup, verify with:

```bash
# Check no ignored files are tracked
git ls-files | grep -E "(__pycache__|\.pyc$|\.coverage|\.agents|\.claude)"
# Should return nothing

# Check .gitignore is working
git check-ignore -v __pycache__/test.py
# Should show the .gitignore rule
```

## Questions?

- **Q: Will this delete my files?**
  - A: No, `git rm --cached` only removes from Git tracking. Files stay on disk.

- **Q: What if I need those files back?**
  - A: They're still in your working directory. Just not tracked by Git.

- **Q: Can I keep .agents/ in Git?**
  - A: Yes! Just remove `/.agents/` from `.gitignore` and re-add the files.

- **Q: What about .vscode/settings.json?**
  - A: Currently ignored. If you want to share VS Code settings, add exception:
    ```
    !.vscode/settings.json
    ```
