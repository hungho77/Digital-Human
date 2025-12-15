# Git Branch Rules & Commit Guidelines

Git workflow rules and commit message conventions for the Digital Human Restaurant Assistant project.

## Table of Contents

1. [Branch Strategy](#branch-strategy)
2. [Branch Naming](#branch-naming)
3. [Commit Messages](#commit-messages)
4. [Pull Request Process](#pull-request-process)
5. [Code Review](#code-review)
6. [Release Process](#release-process)

## Branch Strategy

### Main Branches

```
main (production)
  └── develop (integration)
       ├── feature/* (new features)
       ├── bugfix/* (bug fixes)
       ├── hotfix/* (critical production fixes)
       ├── refactor/* (code refactoring)
       └── docs/* (documentation)
```

### Branch Descriptions

| Branch | Purpose | Protected | Base Branch |
|--------|---------|-----------|-------------|
| `main` | Production-ready code | ✅ Yes | - |
| `develop` | Integration branch | ✅ Yes | `main` |
| `feature/*` | New features | ❌ No | `develop` |
| `bugfix/*` | Bug fixes | ❌ No | `develop` |
| `hotfix/*` | Critical production fixes | ❌ No | `main` |
| `refactor/*` | Code refactoring | ❌ No | `develop` |
| `docs/*` | Documentation updates | ❌ No | `develop` |

### Branch Lifecycle

```
1. Create branch from base
2. Develop and commit changes
3. Push to remote
4. Create Pull Request
5. Code review
6. Merge to base branch
7. Delete feature branch
```

## Branch Naming

### Naming Convention

```
<type>/<ticket-id>-<short-description>
```

### Types

- `feature/` - New feature development
- `bugfix/` - Bug fixes
- `hotfix/` - Critical production fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test additions or modifications
- `chore/` - Maintenance tasks

### Examples

**Good:**
```
feature/DH-123-dialogue-agent-context
bugfix/DH-456-whisper-timeout-fix
hotfix/DH-789-reservation-crash
refactor/DH-234-agent-architecture
docs/DH-567-api-reference-update
```

**Bad:**
```
new-feature          # No type, no ticket
fix-bug             # Too vague
update              # No context
my-changes          # Not descriptive
```

### Branch Creation

```bash
# Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/DH-123-dialogue-agent-context

# Create hotfix branch
git checkout main
git pull origin main
git checkout -b hotfix/DH-789-reservation-crash
```

## Commit Messages

### Conventional Commits Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Components

#### 1. Type (Required)

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(agent): add multi-turn conversation memory` |
| `fix` | Bug fix | `fix(whisper): resolve timeout on long audio` |
| `docs` | Documentation | `docs(api): update REST API examples` |
| `style` | Code style (formatting) | `style: format code with black` |
| `refactor` | Code refactoring | `refactor(agent): simplify state management` |
| `perf` | Performance improvement | `perf(tts): optimize audio generation` |
| `test` | Add/update tests | `test(reservation): add booking flow tests` |
| `build` | Build system changes | `build: update docker compose config` |
| `ci` | CI/CD changes | `ci: add deployment workflow` |
| `chore` | Maintenance | `chore: update dependencies` |
| `revert` | Revert previous commit | `revert: revert feat(agent): add memory` |

#### 2. Scope (Optional)

The scope specifies the area of the codebase affected:

- `agent` - Agent-related changes
- `dialogue` - Dialogue agent
- `reservation` - Reservation agent
- `rag` - RAG system
- `tts` - Text-to-Speech
- `stt` - Speech-to-Text
- `avatar` - Avatar rendering
- `api` - REST API
- `websocket` - WebSocket API
- `db` - Database
- `docker` - Docker configuration
- `ci` - CI/CD

#### 3. Subject (Required)

- Use imperative mood ("add" not "added" or "adds")
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters
- Be descriptive but concise

**Good:**
```
add multi-turn conversation support
fix timeout in audio transcription
update deployment documentation
```

**Bad:**
```
Added new feature
Fixed bug
Updated stuff
```

#### 4. Body (Optional)

- Separate from subject with blank line
- Explain **what** and **why**, not how
- Wrap at 72 characters
- Can include multiple paragraphs

#### 5. Footer (Optional)

- Reference issues/PRs
- Breaking changes
- Deprecations

**Keywords:**
- `Closes #123` - Closes issue
- `Fixes #456` - Fixes bug
- `Refs #789` - References issue
- `Breaking change:` - Breaking API change
- `Deprecated:` - Deprecated feature

### Complete Examples

#### Example 1: Feature

```
feat(agent): add multi-turn conversation memory

Implement conversation history tracking to maintain context
across multiple dialogue turns. This enables the agent to
reference previous messages and provide more coherent responses.

- Add conversation history to DialogueState
- Implement context window management (last 10 messages)
- Add memory cleanup for old sessions

Closes #123
```

#### Example 2: Bug Fix

```
fix(whisper): resolve timeout on long audio files

Fixed timeout issue occurring when processing audio files
longer than 30 seconds by implementing chunked processing.

The audio is now split into 20-second chunks with 2-second
overlap to ensure smooth transcription.

Fixes #456
```

#### Example 3: Refactor

```
refactor(agent): simplify state management logic

Simplified agent state management by consolidating redundant
state fields and removing unused context variables.

This change reduces memory usage by ~15% and improves code
maintainability without changing external behavior.

Refs #234
```

#### Example 4: Breaking Change

```
feat(api): update reservation API response format

Changed reservation API response structure to include more
detailed information about table assignments and alternatives.

Breaking change: Response field `table` renamed to `table_info`
and now includes additional properties.

BREAKING CHANGE: Clients using the old `table` field must
update to use `table_info.table_number` instead.

Migration guide: docs/migrations/v2-api-changes.md

Closes #890
```

### Commit Best Practices

#### DO ✅

```bash
# Commit small, logical changes
git add src/agents/dialogue.py
git commit -m "feat(dialogue): add intent classification"

# Commit related changes together
git add src/agents/reservation.py tests/test_reservation.py
git commit -m "feat(reservation): add table availability check

- Implement availability checking logic
- Add unit tests for edge cases
- Update API documentation"

# Reference issues
git commit -m "fix(websocket): handle connection drops

Fixes #567"
```

#### DON'T ❌

```bash
# Don't commit unrelated changes together
git add src/agents/* src/services/* config/*
git commit -m "various updates"

# Don't use vague messages
git commit -m "update"
git commit -m "fix bug"
git commit -m "WIP"

# Don't commit without testing
git commit -m "feat: add new feature" # without running tests

# Don't include secrets
git commit -m "feat: add API integration" # with API keys in code
```

## Pull Request Process

### 1. Before Creating PR

```bash
# Ensure branch is up to date
git checkout develop
git pull origin develop
git checkout feature/your-branch
git merge develop

# Run quality checks
make check

# Run tests
make test

# Review changes
git diff develop
```

### 2. Creating PR

Use the PR template (`.github/PULL_REQUEST_TEMPLATE.md`):

**Title Format:**
```
<type>(<scope>): <description>
```

**Example:**
```
feat(agent): add conversation memory system
```

**PR Description:**
- Clear summary of changes
- Motivation and context
- Testing performed
- Screenshots/demos (if applicable)
- Breaking changes (if any)
- Migration guide (if needed)

### 3. PR Review Checklist

**For Authors:**
- [ ] Code follows project standards
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] CI checks passing
- [ ] Self-reviewed changes
- [ ] Linked related issues

**For Reviewers:**
- [ ] Code quality acceptable
- [ ] Logic is sound
- [ ] Tests are adequate
- [ ] Performance impact considered
- [ ] Security implications reviewed
- [ ] Documentation is clear

### 4. Merging

```bash
# Squash and merge (preferred for features)
# - Combines all commits into one
# - Keeps history clean

# Merge commit (for important features)
# - Preserves all commits
# - Shows development history

# Rebase and merge (for small changes)
# - Linear history
# - No merge commits
```

## Code Review

### Review Guidelines

#### What to Review

1. **Correctness**
   - Logic is sound
   - Edge cases handled
   - No obvious bugs

2. **Design**
   - Follows architecture
   - Appropriate abstractions
   - Maintainable code

3. **Testing**
   - Adequate test coverage
   - Tests are meaningful
   - Edge cases tested

4. **Documentation**
   - Code is documented
   - API docs updated
   - README updated if needed

5. **Performance**
   - No performance regressions
   - Efficient algorithms
   - Resource usage acceptable

6. **Security**
   - No security vulnerabilities
   - Input validation present
   - Secrets not exposed

#### Review Comments

**Good:**
```
Could we add error handling for the case where the database
connection fails? This would prevent crashes in production.

Consider extracting this into a separate function for better
testability and reusability.

Great implementation! The conversation memory management is
very clean and efficient.
```

**Bad:**
```
This is wrong.
Bad code.
Why did you do it this way?
```

### Response to Review

```bash
# Address review comments
git add changed_files
git commit -m "refactor: address review comments

- Add error handling for DB connection
- Extract function for testability
- Update tests accordingly"

git push origin feature/your-branch
```

## Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH

Example: 1.2.3
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)
```

### Release Workflow

```bash
# 1. Create release branch
git checkout develop
git checkout -b release/v1.2.0

# 2. Update version numbers
# - Update VERSION file
# - Update package.json
# - Update documentation

# 3. Test thoroughly
make test
make integration-test

# 4. Create changelog
# Update CHANGELOG.md with changes since last release

# 5. Merge to main
git checkout main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin main --tags

# 6. Merge back to develop
git checkout develop
git merge --no-ff release/v1.2.0
git push origin develop

# 7. Delete release branch
git branch -d release/v1.2.0
```

### Hotfix Workflow

```bash
# 1. Create hotfix branch from main
git checkout main
git checkout -b hotfix/v1.2.1

# 2. Fix the issue
# ... make changes ...
git commit -m "fix(critical): resolve production crash"

# 3. Test thoroughly
make test

# 4. Merge to main
git checkout main
git merge --no-ff hotfix/v1.2.1
git tag -a v1.2.1 -m "Hotfix version 1.2.1"
git push origin main --tags

# 5. Merge to develop
git checkout develop
git merge --no-ff hotfix/v1.2.1
git push origin develop

# 6. Delete hotfix branch
git branch -d hotfix/v1.2.1
```

## Quick Reference

### Common Commands

```bash
# Create feature branch
git checkout -b feature/DH-123-description

# Commit with conventional format
git commit -m "feat(agent): add feature description"

# Push branch
git push -u origin feature/DH-123-description

# Update branch with develop
git fetch origin
git merge origin/develop

# Interactive rebase (clean up commits)
git rebase -i develop

# Amend last commit
git commit --amend

# Cherry-pick commit
git cherry-pick <commit-hash>
```

### Commit Message Templates

**Feature:**
```
feat(scope): add feature description

Detailed explanation of the feature.

Closes #123
```

**Bug Fix:**
```
fix(scope): resolve issue description

Explanation of the bug and how it's fixed.

Fixes #456
```

**Documentation:**
```
docs(scope): update documentation

Description of documentation changes.
```

## Best Practices Summary

1. ✅ Always create branch from latest `develop`
2. ✅ Use descriptive branch names with ticket IDs
3. ✅ Write clear commit messages following conventional commits
4. ✅ Commit small, logical changes frequently
5. ✅ Run tests before committing
6. ✅ Keep PRs focused and reasonably sized
7. ✅ Respond to review comments promptly
8. ✅ Update documentation with code changes
9. ✅ Delete branches after merging
10. ✅ Never commit secrets or sensitive data

## References

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Git Best Practices](https://www.git-tower.com/learn/git/ebook/en/command-line/appendix/best-practices)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

## Support

For questions about Git workflow:
- Review this document
- Ask in team chat
- Create GitHub discussion
- Contact team lead

