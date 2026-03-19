#!/usr/bin/env bash
# install_hermes_skill.sh — Install a Hermes skill into ~/.hermes/skills/
#
# Usage:
#   ./scripts/install_hermes_skill.sh [OPTIONS]
#
# Options:
#   --skill-repo <url>         Git URL of the skill repo to clone and install
#                              (default: nativ3ai/hermes-geopolitical-market-sim)
#   --bootstrap-stack          Also bootstrap companion services (WorldOSINT, MiroFish)
#   --with-video-transcriber   Include universal video transcriber skill
#   --doctor                   Run dependency doctor check only (no install)
#   --hermes-home <path>       Override HERMES_HOME (default: ~/.hermes)
#   -h, --help                 Show this help message
#
# Examples:
#   # Install PrediHermes (default):
#   ./scripts/install_hermes_skill.sh
#
#   # Install with full companion stack:
#   ./scripts/install_hermes_skill.sh --bootstrap-stack
#
#   # Install a different skill repo:
#   ./scripts/install_hermes_skill.sh --skill-repo https://github.com/acme/my-hermes-skill
#
#   # Doctor check only:
#   ./scripts/install_hermes_skill.sh --doctor
#
# Part of: Codomyrmex — https://github.com/docxology/codomyrmex
# Last Updated: March 2026

set -euo pipefail

# ── Defaults ─────────────────────────────────────────────────────────────────

DEFAULT_SKILL_REPO="https://github.com/nativ3ai/hermes-geopolitical-market-sim.git"
SKILL_REPO="${DEFAULT_SKILL_REPO}"
BOOTSTRAP_STACK=false
WITH_VIDEO_TRANSCRIBER=false
DOCTOR_ONLY=false
HERMES_HOME="${HERMES_HOME:-${HOME}/.hermes}"

# ── Colours ───────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()      { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ── Argument parsing ──────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skill-repo)
            SKILL_REPO="$2"; shift 2 ;;
        --bootstrap-stack)
            BOOTSTRAP_STACK=true; shift ;;
        --with-video-transcriber)
            WITH_VIDEO_TRANSCRIBER=true; shift ;;
        --doctor)
            DOCTOR_ONLY=true; shift ;;
        --hermes-home)
            HERMES_HOME="$2"; shift 2 ;;
        -h|--help)
            grep '^#' "$0" | sed 's/^# \{0,1\}//' | tail -n +2
            exit 0 ;;
        *)
            log_error "Unknown option: $1"; exit 1 ;;
    esac
done

HERMES_SKILLS_DIR="${HERMES_HOME}/skills"

# ── Doctor check ──────────────────────────────────────────────────────────────

doctor_check() {
    local fail=0

    log_info "Running Codomyrmex × Hermes Skill Doctor Check"
    echo "──────────────────────────────────────────────────"

    # git
    if command -v git &>/dev/null; then
        log_ok "git $(git --version | awk '{print $3}')"
    else
        log_error "git not found — install git first"; fail=1
    fi

    # python3
    if command -v python3 &>/dev/null; then
        log_ok "python3 $(python3 --version 2>&1 | awk '{print $2}')"
    else
        log_error "python3 not found — install Python 3.10+"; fail=1
    fi

    # hermes
    if command -v hermes &>/dev/null; then
        HERMES_VER=$(hermes version 2>/dev/null | head -1 || echo "unknown")
        log_ok "hermes ${HERMES_VER}"
    else
        log_error "hermes CLI not found — install NousResearch/hermes-agent first"; fail=1
    fi

    # node / npm (optional — needed by some skill companions)
    if command -v node &>/dev/null; then
        log_ok "node $(node --version)"
    else
        log_warn "node not found — some companion services may require Node.js 18+"
    fi

    # uv (optional)
    if command -v uv &>/dev/null; then
        log_ok "uv $(uv --version 2>&1 | head -1)"
    else
        log_warn "uv not found — recommended for Python companion installs"
    fi

    # HERMES_HOME
    if [[ -d "${HERMES_HOME}" ]]; then
        log_ok "HERMES_HOME = ${HERMES_HOME}"
    else
        log_warn "HERMES_HOME dir does not exist yet: ${HERMES_HOME} (will be created by hermes setup)"
    fi

    # Existing PrediHermes install
    PREDI_PATH="${HERMES_SKILLS_DIR}/research/geopolitical-market-sim"
    if [[ -d "${PREDI_PATH}" ]]; then
        log_ok "PrediHermes skill already installed at ${PREDI_PATH}"
    else
        log_info "PrediHermes not yet installed"
    fi

    echo "──────────────────────────────────────────────────"
    if [[ $fail -eq 0 ]]; then
        log_ok "Doctor check passed"
        return 0
    else
        log_error "Doctor check found issues (see above)"
        return 1
    fi
}

# ── Installation ──────────────────────────────────────────────────────────────

install_skill() {
    local repo_url="$1"
    local repo_name
    repo_name=$(basename "${repo_url}" .git)
    local clone_dir
    clone_dir="$(mktemp -d)/codomyrmex-skill-${repo_name}"

    log_info "Cloning skill repo: ${repo_url}"
    git clone --depth 1 "${repo_url}" "${clone_dir}"

    if [[ ! -f "${clone_dir}/install.sh" ]]; then
        log_error "No install.sh found in ${clone_dir} — is this a valid Hermes skill repo?"
        exit 1
    fi

    chmod +x "${clone_dir}/install.sh"

    local install_args=()
    if [[ "${BOOTSTRAP_STACK}" == "true" ]]; then
        install_args+=("--bootstrap-stack")
    fi
    if [[ "${WITH_VIDEO_TRANSCRIBER}" == "true" ]]; then
        install_args+=("--with-video-transcriber")
    fi

    local args_display=""
    if [[ ${#install_args[@]} -gt 0 ]]; then
        args_display=" with ${install_args[*]}"
    fi
    log_info "Running install.sh${args_display}"
    (cd "${clone_dir}" && bash install.sh ${install_args[@]+"${install_args[@]}"})

    # Verify the skill is visible to hermes
    verify_skill_installed
}

verify_skill_installed() {
    log_info "Verifying installed skills via 'hermes skills list'…"
    if ! command -v hermes &>/dev/null; then
        log_warn "Hermes CLI not in PATH — skipping verification"
        return 0
    fi

    local skills_output
    skills_output=$(hermes skills list 2>/dev/null || true)

    if echo "${skills_output}" | grep -q "geopolitical-market-sim"; then
        log_ok "geopolitical-market-sim skill is visible to Hermes"
    else
        log_warn "'geopolitical-market-sim' not found in 'hermes skills list' output."
        log_warn "Manual check — skills dir: ${HERMES_SKILLS_DIR}"
        if [[ -d "${HERMES_SKILLS_DIR}" ]]; then
            ls "${HERMES_SKILLS_DIR}" 2>/dev/null || true
        fi
    fi

    log_info "Full skill list:"
    echo "${skills_output}"
}

post_install_instructions() {
    cat <<'EOF'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PrediHermes × Codomyrmex — Post-Install Checklist
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Use from Hermes chat:
     hermes -s geopolitical-market-sim

2. Use from Codomyrmex Python:
     from codomyrmex.skills.hermes_skill_bridge import HermesSkillBridge
     bridge = HermesSkillBridge()
     entry = bridge.get_skill("geopolitical-market-sim")
     resp = entry.run("Use PrediHermes health")

3. Use from Codomyrmex MCP:
     hermes_execute(
         prompt="Use PrediHermes health",
         hermes_skill="geopolitical-market-sim"
     )

4. Use the typed Python facade:
     from codomyrmex.skills.skills.custom.geopolitical_market_sim \
         import GeopoliticalMarketPipeline
     pipeline = GeopoliticalMarketPipeline()
     pipeline.health()

5. (Optional) If you have companion services, set their secrets:
     ~/predihermes/companions/MiroFish/.env
       LLM_API_KEY=...
       ZEP_API_KEY=...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
}

# ── Main ──────────────────────────────────────────────────────────────────────

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════╗"
    echo "║  Codomyrmex — Hermes Skill Installer             ║"
    echo "╚══════════════════════════════════════════════════╝"
    echo ""

    # Always run doctor first
    if ! doctor_check; then
        if [[ "${DOCTOR_ONLY}" == "true" ]]; then
            exit 1
        fi
        log_warn "Doctor found issues — proceeding anyway (use --doctor to abort on failure)"
    fi

    if [[ "${DOCTOR_ONLY}" == "true" ]]; then
        exit 0
    fi

    install_skill "${SKILL_REPO}"
    post_install_instructions
    log_ok "Installation complete!"
}

main "$@"
