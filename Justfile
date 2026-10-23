set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set shell := ["bash", "-c"]


default: watch

install:
    uv sync

install-dev:
    uv sync --all-groups

run:
    uv run python -m koloagent

watch:
    uv run watchfiles --filter python 'python -m koloagent' src
