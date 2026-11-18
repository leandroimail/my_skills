#!/usr/bin/env bash
# Installs crapper and dryer (optionally mutator) for the quality gates in
# references/quality-gates.md. Linux and macOS. Windows: install-quality-tools.ps1.
# Usage: bash install-quality-tools.sh [--with-mutator] [--latest] [--dir DIR]
# Default DIR: ~/.claude/tools/ub-mode. Do not move DIR after install (pip -e points to it).
# By default clones are pinned to the commits this skill was written against.
set -euo pipefail

DIR="$HOME/.claude/tools/ub-mode"; MUTATOR=0; LATEST=0
while [ $# -gt 0 ]; do
  case "$1" in
    --with-mutator) MUTATOR=1 ;;
    --latest) LATEST=1 ;;
    --dir) DIR="${2:?--dir needs a path}"; shift ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac; shift
done

command -v git >/dev/null || { echo "ERROR: git not found" >&2; exit 1; }
PY=""
for c in python3 python; do  # a stub that only prints an error (Windows Store) must not win
  if command -v "$c" >/dev/null && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)' 2>/dev/null; then PY="$c"; break; fi
done
[ -n "$PY" ] || { echo "ERROR: working python 3.11+ not found" >&2; exit 1; }

install_one() { # name commit
  local name="$1" commit="$2"
  if [ ! -d "$DIR/$name/.git" ]; then
    git clone "https://github.com/unclebob/$name" "$DIR/$name"
  fi
  if [ "$LATEST" = 0 ]; then
    git -C "$DIR/$name" fetch --quiet origin
    git -C "$DIR/$name" checkout --quiet "$commit"
  fi
  "$PY" -m pip install -e "$DIR/$name"
}

mkdir -p "$DIR"
install_one crapper c757ec79a6c15dc815238bbd9c2f4601eb54d3cc
install_one dryer 66ff6d21a42c04afcad89c78a80066176d1294b0
# mutator reads function names from ../crapper, so it must sit next to it (it does).
[ "$MUTATOR" = 1 ] && install_one mutator 830ec7e9c39664d753f8699015bc796df67727b9

PYTHONUTF8=1 "$PY" -m crapper --help >/dev/null && PYTHONUTF8=1 "$PY" -m dryer --help >/dev/null \
  && echo "OK: crapper and dryer installed for $PY (clones in $DIR)"
echo "Note: the first analysis downloads tree-sitter grammars from GitHub releases."
