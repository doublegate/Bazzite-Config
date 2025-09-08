#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def parse_lines(path: str):
    out = []
    if not Path(path).exists():
        return out
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        out.append(obj)
    return out


def summarize(label: str, items: list):
    print(f"=== {label}: {len(items)} JSON messages ===")
    tool_names = None
    for o in items:
        if o.get('id') == 2 and 'result' in o:
            tools = o['result'].get('tools') or o['result']
            if isinstance(tools, list):
                tool_names = [t.get('name') if isinstance(t, dict) else str(t) for t in tools]
                print(f"tools: {tool_names[:8]}")
                # Show simple schema preview for first few tools
                for t in tools[:6]:
                    if isinstance(t, dict):
                        name = t.get('name')
                        schema = (t.get('inputSchema') or {}).get('properties') or {}
                        keys = list(schema.keys())
                        print(f" • {name} args: {keys}")
            break
    for o in items:
        if o.get('id') in (3, 4, 5, 6, 10, 11, 12, 20) and 'result' in o:
            res = o['result']
            print(f"id={o['id']} keys: {list(res.keys())}")
            for k in ('results', 'items', 'documents', 'data'):
                if isinstance(res.get(k), list):
                    print(f"top {k} (first 3):")
                    for it in res[k][:3]:
                        if isinstance(it, dict):
                            title = it.get('title') or it.get('name') or it.get('url') or ''
                            url = it.get('url') or it.get('link') or ''
                            snippet = it.get('snippet') or it.get('text') or ''
                            print('-', title[:90], url, (snippet or '')[:160])
                        else:
                            print('-', str(it)[:160])
                    break
            # Print raw if unknown structure
            if not any(
                isinstance(res.get(k), list)
                for k in ('results', 'items', 'documents', 'data')
            ):
                from textwrap import shorten
                print(shorten(json.dumps(res) if not isinstance(res, str) else res, width=1000))


def main():
    brave = parse_lines('/tmp/brave.json')
    ctx7 = parse_lines('/tmp/context7.json')
    if not brave and not ctx7:
        print('No MCP outputs found. Run tools/mcp_quick_queries.sh first.', file=sys.stderr)
        sys.exit(1)
    if brave:
        summarize('brave', brave)
        print()
    if ctx7:
        summarize('context7', ctx7)


if __name__ == '__main__':
    main()
