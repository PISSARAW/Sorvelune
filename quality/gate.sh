#!/bin/sh
# Vérifier exactement l'index Git ou l'arbre du commit donné.
set -eu
temp=$(mktemp -d)
trap 'rm -rf "$temp"' EXIT
mkdir "$temp/src"
empty=$(git hash-object -w -t tree --stdin </dev/null)
case "${1:-staged}" in
  staged|message)
    tree=$(git write-tree)
    base=$(git rev-parse --verify HEAD 2>/dev/null || echo "$empty")
    if [ "${1:-staged}" = message ]; then cp "$2" "$temp/message"; fi ;;
  commit)
    tree=$(git rev-parse "$2^{tree}")
    base=$(git rev-parse --verify "$2^1" 2>/dev/null || echo "$empty")
    git log -1 --format=%B "$2" > "$temp/message" ;;
  *) echo 'usage: gate.sh staged | message FICHIER | commit SHA' >&2; exit 2 ;;
esac
GIT_INDEX_FILE="$temp/index" git read-tree "$tree"
GIT_INDEX_FILE="$temp/index" git checkout-index --all --prefix="$temp/src/"
python3 -E "$temp/src/quality/check.py" "$temp/src" "$base" "$tree"
