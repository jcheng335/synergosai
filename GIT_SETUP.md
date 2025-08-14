# Git Setup Instructions

This guide will help you set up this project in a Git repository and push it to GitHub.

## 📁 Project Structure

```
synergos-ai-complete/
├── README.md                 # Main project documentation
├── DEPLOYMENT.md            # Deployment instructions
├── CONTRIBUTING.md          # Contributing guidelines
├── LICENSE                  # MIT License
├── .gitignore              # Git ignore rules
├── GIT_SETUP.md            # This file
├── frontend/               # React.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.jsx        # Main app component
│   │   └── App.css        # Styles
│   ├── index.html         # HTML template
│   ├── package.json       # Dependencies
│   └── vite.config.js     # Build configuration
└── backend/               # Flask backend
    ├── src/
    │   ├── models/        # Database models
    │   ├── routes/        # API endpoints
    │   ├── services/      # Business logic
    │   └── main.py        # Flask app entry point
    ├── requirements.txt   # Python dependencies
    └── requirements_deploy.txt # Production dependencies
```

## 🚀 Quick Setup

### Option 1: Initialize New Repository

1. **Navigate to the project directory:**
   ```bash
   cd synergos-ai-complete
   ```

2. **Initialize Git repository:**
   ```bash
   git init
   ```

3. **Add all files:**
   ```bash
   git add .
   ```

4. **Create initial commit:**
   ```bash
   git commit -m "Initial commit: Synergos AI Interview Companion Tool"
   ```

5. **Create GitHub repository:**
   - Go to https://github.com/new
   - Repository name: `synergos-ai`
   - Description: `AI-powered interview companion tool for HR professionals`
   - Make it Public or Private as preferred
   - Don't initialize with README (we already have one)

6. **Connect to GitHub:**
   ```bash
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/synergos-ai.git
   git push -u origin main
   ```

### Option 2: Using GitHub CLI

If you have GitHub CLI installed:

1. **Navigate to project directory:**
   ```bash
   cd synergos-ai-complete
   ```

2. **Initialize and create repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Synergos AI Interview Companion Tool"
   gh repo create synergos-ai --public --source=. --remote=origin --push
   ```

## 🔐 Authentication Methods

### Method 1: Personal Access Token (Recommended)

1. **Create Personal Access Token:**
   - Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
   - Click "Generate new token (classic)"
   - Select scopes: `repo`, `workflow`
   - Copy the token (save it securely!)

2. **Use token for authentication:**
   ```bash
   git remote set-url origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/synergos-ai.git
   git push -u origin main
   ```

### Method 2: SSH Key

1. **Generate SSH key (if you don't have one):**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **Add SSH key to GitHub:**
   - Copy public key: `cat ~/.ssh/id_ed25519.pub`
   - Go to GitHub Settings > SSH and GPG keys > New SSH key
   - Paste the key

3. **Use SSH URL:**
   ```bash
   git remote set-url origin git@github.com:YOUR_USERNAME/synergos-ai.git
   git push -u origin main
   ```

## 📝 Commit Message Guidelines

Use conventional commit format:

```
type(scope): description

feat: add new feature
fix: bug fix
docs: documentation changes
style: formatting changes
refactor: code refactoring
test: adding tests
chore: maintenance tasks
```

Examples:
```bash
git commit -m "feat(upload): add support for DOCX files"
git commit -m "fix(api): resolve CORS issue for file uploads"
git commit -m "docs(readme): update installation instructions"
```

## 🌿 Branch Strategy

### For Development:

1. **Create feature branch:**
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. **Push feature branch:**
   ```bash
   git push origin feature/new-feature-name
   ```

4. **Create Pull Request on GitHub**

5. **Merge and cleanup:**
   ```bash
   git checkout main
   git pull origin main
   git branch -d feature/new-feature-name
   ```

## 🏷️ Tagging Releases

1. **Create and push tag:**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **Create GitHub Release:**
   - Go to repository > Releases > Create a new release
   - Select the tag
   - Add release notes

## 🔄 Keeping Fork Updated

If you forked the repository:

1. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/synergos-ai.git
   ```

2. **Sync with upstream:**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   git push origin main
   ```

## 🚨 Troubleshooting

### Common Issues:

1. **"Repository not found" error:**
   - Check repository name and URL
   - Verify authentication credentials

2. **"Permission denied" error:**
   - Check SSH key setup
   - Verify personal access token permissions

3. **"src refspec main does not match any" error:**
   - Make sure you have commits: `git log --oneline`
   - Create initial commit if needed

4. **Large file issues:**
   - Check .gitignore includes large files
   - Use Git LFS for large assets if needed

### Reset if needed:

```bash
# Remove git history and start fresh
rm -rf .git
git init
git add .
git commit -m "Initial commit"
```

## 📊 Repository Settings

### Recommended Settings:

1. **Branch Protection:**
   - Protect main branch
   - Require pull request reviews
   - Require status checks

2. **Security:**
   - Enable vulnerability alerts
   - Enable automated security updates

3. **Pages (for documentation):**
   - Enable GitHub Pages
   - Use docs/ folder or gh-pages branch

## 🎯 Next Steps

After setting up the repository:

1. **Set up CI/CD** (GitHub Actions)
2. **Configure branch protection rules**
3. **Add collaborators** if working in a team
4. **Set up issue templates**
5. **Configure project boards** for task management

## 📞 Need Help?

- GitHub Documentation: https://docs.github.com
- Git Documentation: https://git-scm.com/doc
- GitHub Community: https://github.community

Happy coding! 🚀

