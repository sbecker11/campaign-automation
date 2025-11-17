#!/bin/bash
# Install pre-commit hook to prevent committing files in outputs/ directory
# This hook ensures that output files are only committed to the separate outputs repository

HOOK_FILE=".git/hooks/pre-commit"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cat > "$REPO_ROOT/$HOOK_FILE" << 'EOF'
#!/bin/bash
# Pre-commit hook to prevent committing files in outputs/ directory
# Outputs should be committed to the separate campaign-automation-outputs repository

# Get list of staged files
staged_files=$(git diff --cached --name-only)

# Check if any files in outputs/ are staged
outputs_files=$(echo "$staged_files" | grep -E '^outputs/' || true)

if [ -n "$outputs_files" ]; then
    echo "❌ ERROR: Cannot commit files in outputs/ directory"
    echo ""
    echo "The following files are staged for commit:"
    echo "$outputs_files" | sed 's/^/  - /'
    echo ""
    echo "Output files should be committed to the separate campaign-automation-outputs repository."
    echo "To unstage these files, run:"
    echo "  git reset HEAD outputs/"
    echo ""
    echo "If you need to commit outputs, use the 'Commit Campaign' button in the refine UI"
    echo "or commit directly to the campaign-automation-outputs repository."
    exit 1
fi

# Also check for YAML/JSON files that might be in outputs (case-insensitive)
yaml_json_in_outputs=$(echo "$staged_files" | grep -iE '\.(yaml|yml|json)$' | grep -E '^outputs/' || true)

if [ -n "$yaml_json_in_outputs" ]; then
    echo "❌ ERROR: Cannot commit YAML/JSON files in outputs/ directory"
    echo ""
    echo "The following files are staged for commit:"
    echo "$yaml_json_in_outputs" | sed 's/^/  - /'
    echo ""
    echo "These files should be committed to the separate campaign-automation-outputs repository."
    exit 1
fi

exit 0
EOF

chmod +x "$REPO_ROOT/$HOOK_FILE"
echo "✅ Pre-commit hook installed successfully!"
echo "   The hook will prevent committing any files in the outputs/ directory."

