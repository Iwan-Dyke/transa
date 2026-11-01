set shell := ["bash", "-euo", "pipefail", "-c"]

default:
    @just --list

# Downloads upstream source and builds its Docker image on first use.
setup:
    mkdir -p .local/state .local/downloads
    chmod 700 .local .local/state .local/downloads
    if [ ! -d .local/rmapi/.git ]; then git clone --depth 1 https://github.com/ddvk/rmapi.git .local/rmapi; fi
    docker build -t transa-rmapi:experiment .local/rmapi

# Fallback when Docker is unavailable; keeps toolchain and dependencies local.
setup-local:
    mkdir -p .local/state .local/downloads .local/bin .local/go-cache .local/go-mod
    chmod 700 .local .local/state .local/downloads
    if [ ! -d .local/rmapi/.git ]; then git clone --depth 1 https://github.com/ddvk/rmapi.git .local/rmapi; fi
    GOTOOLCHAIN=go1.23.12 GOMODCACHE="$PWD/.local/go-mod" GOCACHE="$PWD/.local/go-cache" go -C .local/rmapi build -mod=readonly -o "$PWD/.local/bin/rmapi" .

# Pair locally: enter the one-time code at rmapi's prompt.
pair:
    ./scripts/rmapi-test pair

# Lists notebooks and metadata without prompting for credentials.
list:
    ./scripts/rmapi-test list

# Use an ID from `just list`; downloads the original document archive.
download id:
    ./scripts/rmapi-test download {{quote(id)}}

# Installs a renderer version with support for newer reMarkable pen colours.
setup-render:
    UV_CACHE_DIR="$PWD/.local/uv-cache" uv venv --allow-existing .local/render-venv
    UV_CACHE_DIR="$PWD/.local/uv-cache" uv pip install --python .local/render-venv/bin/python 'rmc @ git+https://github.com/ricklupton/rmc.git@da87813a31496d156ca6ea8a27bf5128670fb45a' 'cairosvg==2.9.1'

render archive page="1":
    .local/render-venv/bin/python scripts/render-page.py {{quote(archive)}} {{quote(page)}}
