# GitHub Actions Workflows - Manual Setup Required

## Why Manual Setup?

The GitHub Actions workflow file (`workflows/ci-testing.yml`) cannot be pushed directly via this automated process due to GitHub App workflow permissions. This is a security measure to prevent unauthorized workflow modifications.

## How to Add the Workflow

### Option 1: Manual File Creation (Recommended)

1. Go to your GitHub repository: https://github.com/doublegate/Bazzite-Config
2. Navigate to `.github/workflows/` directory (create if it doesn't exist)
3. Click "Add file" → "Create new file"
4. Name it `ci-testing.yml`
5. Copy the contents from the local file at `.github/workflows/ci-testing.yml`
6. Commit directly to your main or development branch

### Option 2: Push from Local Repository

If you have direct push access (not via GitHub App):

```bash
# From your local repository
git add .github/workflows/ci-testing.yml
git commit -m "ci: Add GitHub Actions automated testing workflow"
git push origin main  # or your branch name
```

### Option 3: Pull Request

1. Create a branch locally
2. Add the workflow file
3. Push the branch
4. Create a pull request
5. Merge after review

## Workflow File Location

The complete workflow file is available at:
```
.github/workflows/ci-testing.yml
```

## What the Workflow Does

The CI/CD pipeline provides:

- **Linting**: Black, isort, Flake8, Pylint, Bandit, Safety
- **Testing**: Python 3.8-3.12 matrix testing
- **GUI Tests**: GTK4 tests with mocking
- **Slow Tests**: Extended test suite (scheduled/manual)
- **Security Scanning**: Trivy vulnerability scanning
- **Build Testing**: Installation validation
- **Documentation**: Markdown validation
- **Coverage**: Codecov integration

## Testing Locally

You can test the workflow configuration locally before pushing:

```bash
# Install act (GitHub Actions local runner)
# https://github.com/nektos/act

# Run workflow locally
act push

# Run specific job
act -j test
```

## After Setup

Once the workflow is added, it will automatically run on:
- Push to main, develop, or claude/** branches
- Pull requests to main or develop
- Daily at 00:00 UTC (scheduled tests)

## Need Help?

See the complete documentation:
- TESTING.md - Testing guide
- .github/workflows/ci-testing.yml - Workflow file with comments
