#!/bin/bash

echo "🧹 Starting repository cleanup for check-in..."

# Remove Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Remove virtual environment (will be recreated by users)
echo "Removing virtual environment..."
rm -rf venv/ 2>/dev/null || true

# Remove Node.js dependencies (will be reinstalled by users)
echo "Removing Node.js dependencies..."
rm -rf frontend/node_modules/ 2>/dev/null || true

# Remove any PID files
echo "Removing PID files..."
find . -name "*.pid" -delete 2>/dev/null || true
find . -name ".backend.pid" -delete 2>/dev/null || true
find . -name ".frontend.pid" -delete 2>/dev/null || true

# Remove log files
echo "Removing log files..."
find . -name "*.log" -delete 2>/dev/null || true

# Remove any temporary files
echo "Removing temporary files..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true

# Remove OS-specific files
echo "Removing OS-specific files..."
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true

# Remove any backup files
echo "Removing backup files..."
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.backup" -delete 2>/dev/null || true
find . -name "*~" -delete 2>/dev/null || true

# Remove any test coverage files
echo "Removing test coverage files..."
find . -name ".coverage" -delete 2>/dev/null || true
find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove any IDE-specific files
echo "Removing IDE-specific files..."
find . -name ".vscode" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".idea" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.swp" -delete 2>/dev/null || true
find . -name "*.swo" -delete 2>/dev/null || true

# Remove any npm/yarn cache files
echo "Removing npm/yarn cache files..."
find . -name ".npm" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".eslintcache" -delete 2>/dev/null || true
find . -name ".yarn-integrity" -delete 2>/dev/null || true

# Remove any build artifacts
echo "Removing build artifacts..."
find . -name "build" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove any Redis dump files
echo "Removing Redis dump files..."
find . -name "dump.rdb" -delete 2>/dev/null || true

echo "✅ Cleanup completed successfully!"
echo ""
echo "📋 Summary of what was removed:"
echo "  - Python cache files (__pycache__, *.pyc)"
echo "  - Virtual environment (venv/)"
echo "  - Node.js dependencies (node_modules/)"
echo "  - PID files (*.pid)"
echo "  - Log files (*.log)"
echo "  - Temporary files (*.tmp, *.temp)"
echo "  - OS-specific files (.DS_Store, Thumbs.db)"
echo "  - Backup files (*.bak, *.backup, *~)"
echo "  - Test coverage files (.coverage, htmlcov, .pytest_cache)"
echo "  - IDE-specific files (.vscode, .idea, *.swp)"
echo "  - NPM/Yarn cache files (.npm, .eslintcache, .yarn-integrity)"
echo "  - Build artifacts (build/, dist/, *.egg-info)"
echo "  - Redis dump files (dump.rdb)"
echo ""
echo "📝 Important files preserved:"
echo "  - All source code files"
echo "  - Configuration files (package.json, requirements.txt, etc.)"
echo "  - Documentation files"
echo "  - Docker files"
echo "  - Scripts (start.sh, stop.sh, etc.)"
echo ""
echo "🚀 To restore the development environment:"
echo "  1. Create virtual environment: python -m venv venv"
echo "  2. Activate it: source venv/bin/activate"
echo "  3. Install Python dependencies: pip install -r backend/requirements.txt"
echo "  4. Install Node.js dependencies: cd frontend && npm install"
echo "  5. Start the system: ./start.sh"
