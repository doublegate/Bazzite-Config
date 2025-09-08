#!/usr/bin/env bash
set -euo pipefail

# Quick MCP stdio queries for brave-search and context7
# Usage: BRAVE_API_KEY=... ./tools/mcp_quick_queries.sh [optional_query]

BRAVE_API_KEY=$BRAVE_API_KEY
QUERY_DEFAULT="rpm-ostree kargs best practices immutable ostree"
QUERY_INPUT="${1:-}"
QUERY="${QUERY_INPUT:-$QUERY_DEFAULT}"

echo "[INFO] Using BRAVE_API_KEY: \\${BRAVE_API_KEY:0:6}… (set BRAVE_API_KEY to override)"
echo "[INFO] Base query: $QUERY"

BRAVE_OUT="/tmp/brave.json"
CTX7_OUT="/tmp/context7.json"
CTX7_DOCS_OUT="/tmp/context7_docs.json"

rm -f "$BRAVE_OUT" "$CTX7_OUT" "$CTX7_DOCS_OUT"

echo "[INFO] Querying brave-search MCP (stdio) …"
(
  printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"clientInfo":{"name":"codex-cli","version":"1.0"},"capabilities":{}}}\n'
  printf '{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n'
  # Use correct tool name from tools/list: brave_web_search
  printf '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"brave_web_search","arguments":{"query":"%s","count":6}}}\n' "$QUERY"
  printf '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"brave_web_search","arguments":{"query":"rpm-ostree kargs append-if-missing replace delete","count":6}}}\n'
  printf '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"brave_web_search","arguments":{"query":"rpm-ostree kargs transaction in progress stuck","count":6}}}\n'
  printf '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"brave_web_search","arguments":{"query":"site:docs.fedoraproject.org rpm-ostree kargs","count":6}}}\n'
) | timeout 70s npx @brave/brave-search-mcp-server --transport stdio --brave-api-key "$BRAVE_API_KEY" | tee "$BRAVE_OUT" >/dev/null || true

echo "[INFO] Querying context7 MCP (stdio) …"
(
  printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"clientInfo":{"name":"codex-cli","version":"1.0"},"capabilities":{}}}\n'
  printf '{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n'
  # Per tools/list: resolve-library-id expects {"libraryName": "..."}
  printf '{"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"resolve-library-id","arguments":{"libraryName":"rpm-ostree"}}}\n'
  printf '{"jsonrpc":"2.0","id":11,"method":"tools/call","params":{"name":"resolve-library-id","arguments":{"libraryName":"ostree"}}}\n'
  printf '{"jsonrpc":"2.0","id":12,"method":"tools/call","params":{"name":"resolve-library-id","arguments":{"libraryName":"fedora docs"}}}\n'
) | timeout 60s npx -y @upstash/context7-mcp@latest | tee "$CTX7_OUT" >/dev/null || true

# Try to extract a library ID and request docs
LIBID=$(python3 - "$CTX7_OUT" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1])
libid=''
for line in p.read_text().splitlines():
    try:
        o=json.loads(line)
    except Exception:
        continue
    if o.get('id') in (10,11,12) and isinstance(o.get('result'), dict):
        # Heuristics: check common keys for an ID
        for k in ('context7CompatibleLibraryID','libraryId','id','libraryID'):
            v=o['result'].get(k)
            if isinstance(v, str) and len(v) >= 6:
                libid=v
                break
    if libid:
        break
print(libid)
PY
)

if [ -n "$LIBID" ]; then
  echo "[INFO] Resolved context7 library id: $LIBID"
  (
    printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"clientInfo":{"name":"codex-cli","version":"1.0"},"capabilities":{}}}\n'
    printf '{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n'
    printf '{"jsonrpc":"2.0","id":20,"method":"tools/call","params":{"name":"get-library-docs","arguments":{"context7CompatibleLibraryID":"%s","topic":"rpm-ostree kargs","tokens":800}}}\n' "$LIBID"
  ) | timeout 60s npx -y @upstash/context7-mcp@latest | tee "$CTX7_DOCS_OUT" >/dev/null || true
else
  echo "[WARN] No context7 library id resolved from $CTX7_OUT; skipping docs retrieval"
fi

echo "[INFO] Saved outputs: $BRAVE_OUT, $CTX7_OUT ${LIBID:+, $CTX7_DOCS_OUT}"
