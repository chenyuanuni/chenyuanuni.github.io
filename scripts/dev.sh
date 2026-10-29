#!/usr/bin/env bash
set -euo pipefail
site_dir="$(cd "$(dirname "$0")/.." && pwd)"
cd "$site_dir"
local_runtime="$site_dir/../../tmp/website-runtime/env.sh"
if [ -f "$local_runtime" ]; then
  source "$local_runtime"
  exec "$FENG_RUBY_ROOT/bin/ruby" "$FENG_RUBY_ROOT/bin/bundle" exec jekyll serve --host 127.0.0.1 --port "${PORT:-4175}" "$@"
fi
exec bundle exec jekyll serve --host 127.0.0.1 --port "${PORT:-4175}" "$@"
