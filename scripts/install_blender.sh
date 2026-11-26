#!/usr/bin/env bash
set -euo pipefail

# Use the official Blender Foundation binary: distro builds may omit Cycles.
BLENDER_VERSION="${BLENDER_VERSION:-5.2.5}"
ARCHIVE="blender-${BLENDER_VERSION}-linux-x64.tar.xz"
BASE_URL="https://download.blender.org/release/Blender${BLENDER_VERSION%.*}/"
INSTALL_ROOT="${RUNNER_TEMP:-/tmp}/blender-${BLENDER_VERSION}"
mkdir -p "$INSTALL_ROOT"

sudo apt-get update
sudo apt-get install -y ffmpeg unzip curl xz-utils python3-numpy \
  libegl1 libgl1 libgl1-mesa-dri libegl-mesa0 libglx-mesa0 \
  libx11-6 libxxf86vm1 libxi6 libxrender1 libxfixes3 libxkbcommon0 \
  libsm6 libice6 libdbus-1-3 libdecor-0-0 libwayland-client0 \
  libwayland-egl1 libwayland-cursor0 libxrandr2 libxinerama1 \
  libxcursor1 libxcomposite1 libxdamage1 libxext6

curl -fL --retry 3 "$BASE_URL$ARCHIVE" -o "$INSTALL_ROOT/$ARCHIVE"
curl -fL --retry 3 "$BASE_URL/blender-$BLENDER_VERSION.sha256" -o "$INSTALL_ROOT/checksums.sha256"
grep -F "$ARCHIVE" "$INSTALL_ROOT/checksums.sha256" | (cd "$INSTALL_ROOT" && sha256sum -c -)
tar -xJf "$INSTALL_ROOT/$ARCHIVE" -C "$INSTALL_ROOT"
BLENDER_BIN="$INSTALL_ROOT/blender-$BLENDER_VERSION-linux-x64/blender"
test -x "$BLENDER_BIN"

if [[ -n "${GITHUB_PATH:-}" ]]; then
  echo "$(dirname "$BLENDER_BIN")" >> "$GITHUB_PATH"
fi
if [[ -n "${GITHUB_ENV:-}" ]]; then
  echo "BLENDER_BIN=$BLENDER_BIN" >> "$GITHUB_ENV"
fi

"$BLENDER_BIN" --version
"$BLENDER_BIN" --background --python-expr \
  "import bpy; engines=set(bpy.context.scene.render.bl_rna.properties['engine'].enum_items.keys()); print('AVAILABLE_RENDER_ENGINES', sorted(engines)); assert 'CYCLES' in engines, 'Official Blender build must include Cycles'"
