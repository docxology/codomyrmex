#!/usr/bin/env bash
# install_hermes_skill.sh — Install a Hermes skill into the active Hermes instance.
#
# Usage:
#   ./scripts/agents/hermes/install_hermes_skill.sh [OPTIONS]
#
# Options:
#   --skill-repo <url>   Git URL of the skill to install.
#                        Default: https://github.com/nativ3ai/hermes-geopolitical-market-sim.git
#   --skill-name <name>  Expected CLI skill name for post-install verification.
#                        Default: derived from repo URL basename.
#   --hermes-home <dir>  Override HERMES_HOME.
#   -h, --help           Show this help.
#
# Examples:
#   ./scripts/agents/hermes/install_hermes_skill.sh
#   ./scripts/agents/hermes/install_hermes_skill.sh \
#       --skill-repo https://github.com/nativ3ai/hermes-polymarket-skill.git \
#       --skill-name polymarket
#
# Exit codes:
#   0   Success
#   1   Failure (diagnostics printed to stderr)
#
# shellcheck shell=bash
set -euo pipefail

# ── Defaults ────────────────────────────────────────────────────────────────
DEFAULT_SKILL_REPO="https://github.com/nativ3ai/hermes-geopolitical-market-sim.git"
SKILL_REPO="${DEFAULT_SKILL_REPO}"
SKILL_NAME=""
HERMES_HOME="${HERMES_HOME:-${HOME}/.hermes}"

# ── Argument parsing ─────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --skill-repo)
            SKILL_REPO="$2"
            shift 2
            ;;
        --skill-name)
            SKILL_NAME="$2"
            shift 2
            ;;
        --hermes-home)
            HERMES_HOME="$2"
            shift 2
            ;;
        -h|--help)
            sed -n '/^# install_hermes_skill/,/^# shellcheck/{ /^# shellcheck/d; s/^# \{0,1\}//; p }' "$0"
            exit 0
            ;;
        *)
            echo "[ERROR] Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

# Derive skill name from repo URL if not specified
if [[ -z "${SKILL_NAME}" ]]; then
    SKILL_NAME="$(basename "${SKILL_REPO}" .git)"
fi

# ── Helpers ──────────────────────────────────────────────────────────────────
log_info()  { echo "[INFO]  $*"; }
log_ok()    { echo "[OK]    $*"; }
log_warn()  { echo "[WARN]  $*"; }
log_error() { echo "[ERROR] $*" >&2; }

divider() { printf '%-50s\n' | tr ' ' '─'; }

# ── Banner ───────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  Codomyrmex — Hermes Skill Installer             ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ── Doctor check ─────────────────────────────────────────────────────────────
log_info "Running Codomyrmex × Hermes Skill Doctor Check"
divider

FAILED=0
check() {
    local label="$1"
    shift
    local val
    val="$("$@" 2>/dev/null | head -1)" || val=""
    if [[ -n "${val}" ]]; then
        log_ok "${label} ${val}"
    else
        log_error "${label} NOT FOUND"
        FAILED=1
    fi
}

check "git   " git --version
check "python3" python3 --version
check "hermes" hermes version
check "node  " node --version
check "uv    " uv version

log_info "HERMES_HOME = ${HERMES_HOME}"

if [[ ! -d "${HERMES_HOME}" ]]; then
    log_warn "HERMES_HOME does not exist yet — hermes setup may be required first"
fi

divider

if [[ "${FAILED}" -eq 1 ]]; then
    log_error "Doctor check failed — aborting install"
    exit 1
fi
log_ok "Doctor check passed"

# ── Clone skill repo ──────────────────────────────────────────────────────────
TMPDIR="$(mktemp -d)"
DEST_DIR="${TMPDIR}/codomyrmex-skill-${SKILL_NAME}"
trap 'rm -rf "${TMPDIR}"' EXIT

log_info "Cloning skill repo: ${SKILL_REPO}"
if ! git clone --depth=1 "${SKILL_REPO}" "${DEST_DIR}"; then
    log_error "Failed to clone ${SKILL_REPO}"
    exit 1
fi

# ── Run install.sh ────────────────────────────────────────────────────────────
INSTALL_SCRIPT="${DEST_DIR}/install.sh"

if [[ ! -f "${INSTALL_SCRIPT}" ]]; then
    log_warn "No install.sh found in ${DEST_DIR} — trying hermes skills install"
    if hermes skills install "${SKILL_REPO}" 2>&1; then
        log_ok "Installed via hermes skills install"
    else
        log_error "hermes skills install also failed"
        exit 1
    fi
else
    log_info "Running install.sh"
    chmod +x "${INSTALL_SCRIPT}"
    # NOTE: 'install_args' is declared here as an empty array to prevent the
    # 'unbound variable' error that occurs when install.sh uses '${install_args[@]}'
    # without ever setting it (bash nounset propagation).
    install_args=()
    export install_args
    (
        cd "${DEST_DIR}"
        bash "${INSTALL_SCRIPT}" "${install_args[@]+"${install_args[@]}"}"
    ) || {
        log_error "install.sh exited with error"
        exit 1
    }
fi

# ── Verify post-install ───────────────────────────────────────────────────────
log_info "Verifying skill '${SKILL_NAME}' appears in hermes skills list..."
SKILLS_OUTPUT="$(hermes skills list 2>/dev/null || true)"

# Accept partial match (skill names are often truncated in table output)
MATCH_NAME="${SKILL_NAME:0:12}"
if echo "${SKILLS_OUTPUT}" | grep -qi "${MATCH_NAME}"; then
    log_ok "Skill '${SKILL_NAME}' confirmed in skills list"
else
    log_warn "Skill '${SKILL_NAME}' not yet visible in 'hermes skills list'"
    log_warn "It may need a gateway restart: hermes gateway restart"
fi

echo ""
echo "✅ Skill installation complete: ${SKILL_NAME}"
echo "   Restart gateway if needed:  hermes gateway restart"
echo ""
exit 0
