set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set shell := ["bash", "-c"]


# ==============================================================================
# ✨ Default Command
# ==============================================================================
default: watch


# ==============================================================================
# 📦 Dependency Management
# ==============================================================================
install:
    uv sync

install-dev:
    uv sync --all-groups


# ==============================================================================
# 🚀 Run Application
# ==============================================================================

run:
    uv run python -m koloagent


watch:
    uv run watchfiles --filter python 'python -m koloagent' src
