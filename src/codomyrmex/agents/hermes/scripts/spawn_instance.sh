#!/bin/bash
# spawn_instance.sh — Create a new Hermes instance from Codomyrmex template
# Location: src/codomyrmex/agents/hermes/scripts/spawn_instance.sh
# Usage: ./spawn_instance.sh <instance-name> [personality] [model] [working-dir]
#
# Examples:
#   ./spawn_instance.sh research-bot "You are a research assistant"
#   ./spawn_instance.sh codomyrmex-watcher technical openrouter/hunter-alpha ~/codomyrmex
#   ./spawn_instance.sh civic-analyst "You analyze civic implications" nvidia/nemotron-3-super-120b-a12b:free

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../instance_templates"
TEMPLATE_CONFIG="$TEMPLATE_DIR/config.template.yaml"
TEMPLATE_ENV="$TEMPLATE_DIR/.env.example"

# Validate arguments
if [ -z "$1" ]; then
    echo "Usage: $0 <instance-name> [personality] [model] [working-dir]"
    echo ""
    echo "Arguments:"
    echo "  instance-name  Directory name (creates ~/<name>/.hermes/)"
    echo "  personality    Built-in name (technical/concise/researcher) or custom prompt"
    echo "  model          OpenRouter model ID (default: openrouter/hunter-alpha)"
    echo "  working-dir    Terminal working directory (default: .)"
    exit 1
fi

INSTANCE_NAME="$1"
PERSONALITY="${2:-technical}"
MODEL="${3:-openrouter/hunter-alpha}"
WORKDIR="${4:-.}"

HERMES_HOME="$HOME/$INSTANCE_NAME/.hermes"
echo "=== Spawning Hermes Instance: $INSTANCE_NAME ==="
echo "HERMES_HOME: $HERMES_HOME"
echo "Model: $MODEL"
echo "Personality: $PERSONALITY"
echo "Workdir: $WORKDIR"
echo ""

# Check if already exists
if [ -d "$HERMES_HOME" ]; then
    echo "ERROR: $HERMES_HOME already exists!"
    echo "Remove it first or choose a different name."
    exit 1
fi

# Create directory structure
echo "Creating directory structure..."
mkdir -p "$HERMES_HOME"/{sessions,skills,memories,cron,logs}

# Copy and customize config
echo "Creating config.yaml..."
cp "$TEMPLATE_CONFIG" "$HERMES_HOME/config.yaml"

# Customize model
sed -i '' "s|model: nvidia/nemotron-3-nano-30b-a3b:free|model: $MODEL|" "$HERMES_HOME/config.yaml"

# Customize working directory
sed -i '' "s|cwd: \.|cwd: $WORKDIR|" "$HERMES_HOME/config.yaml"

# If personality is a built-in name, set it; otherwise add as custom
BUILTINS="technical concise researcher helpful creative teacher kawaii catgirl pirate shakespeare surfer noir uwu philosopher hype"
if echo "$BUILTINS" | grep -qw "$PERSONALITY"; then
    sed -i '' "s|personality: technical|personality: $PERSONALITY|" "$HERMES_HOME/config.yaml"
else
    # Add custom personality
    sed -i '' "/personality: technical/a\\
  personalities:\\
    custom: |\\
      $PERSONALITY
" "$HERMES_HOME/config.yaml"
    sed -i '' "s|personality: technical|personality: custom|" "$HERMES_HOME/config.yaml"
fi

# Copy .env template
echo "Creating .env from template..."
cp "$TEMPLATE_ENV" "$HERMES_HOME/.env"

# Copy OpenRouter key from main instance if available
MAIN_ENV="$HOME/.hermes/.env"
if [ -f "$MAIN_ENV" ]; then
    OR_KEY=$(grep "^OPENROUTER_API_KEY=" "$MAIN_ENV" | cut -d= -f2)
    if [ -n "$OR_KEY" ]; then
        sed -i '' "s|OPENROUTER_API_KEY=sk-or-...|OPENROUTER_API_KEY=$OR_KEY|" "$HERMES_HOME/.env"
        echo "Copied OPENROUTER_API_KEY from main instance"
    fi
fi

echo ""
echo "=== Instance Created ==="
echo "Location: $HERMES_HOME"
echo ""
echo "Next steps:"
echo "1. Edit $HERMES_HOME/.env to add API keys"
echo "2. Validate: HERMES_HOME=$HERMES_HOME hermes doctor"
echo "3. Test: HERMES_HOME=$HERMES_HOME hermes chat -q 'Hello, who are you?'"
echo "4. Start: cd $WORKDIR && HERMES_HOME=$HERMES_HOME hermes gateway run &"
echo ""
echo "⚠️  IMPORTANT: Always start gateway with explicit CWD (cd to workdir first)"
echo "   See docs/agents/hermes/gotchas.md for details."
echo ""
echo "For Telegram:"
echo "  - Add TELEGRAM_BOT_TOKEN to .env"
echo "  - Uncomment telegram section in config.yaml"
echo "  - Run: HERMES_HOME=$HERMES_HOME hermes gateway start"
