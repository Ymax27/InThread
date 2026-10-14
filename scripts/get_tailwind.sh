#!/usr/bin/env sh
# Télécharge le CLI autonome de Tailwind CSS (version épinglée) pour l'OS courant.
# Aucun npm / Node dans ce projet : le binaire est mis dans bin/ (non versionné).
# Utilisé localement et dans l'étape « css » du Dockerfile.
set -eu

TAILWIND_VERSION="${TAILWIND_VERSION:-v4.3.3}"
RACINE="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$RACINE/bin/tailwindcss"

case "$(uname -s)" in
  Linux)  os=linux ;;
  Darwin) os=macos ;;
  *) echo "OS non supporté : $(uname -s)" >&2 ; exit 1 ;;
esac

case "$(uname -m)" in
  x86_64 | amd64)  arch=x64 ;;
  aarch64 | arm64) arch=arm64 ;;
  *) echo "Architecture non supportée : $(uname -m)" >&2 ; exit 1 ;;
esac

asset="tailwindcss-${os}-${arch}"
url="https://github.com/tailwindlabs/tailwindcss/releases/download/${TAILWIND_VERSION}/${asset}"

mkdir -p "$(dirname "$DEST")"
echo "Téléchargement de Tailwind CSS ${TAILWIND_VERSION} (${asset})…"

if command -v curl >/dev/null 2>&1; then
  curl -fSL "$url" -o "${DEST}.tmp"
else
  wget -O "${DEST}.tmp" "$url"
fi

chmod +x "${DEST}.tmp"
mv "${DEST}.tmp" "$DEST"          # uniquement si le téléchargement a réussi
echo "Tailwind CSS installé : $DEST"
