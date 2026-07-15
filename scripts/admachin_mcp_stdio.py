#!/usr/bin/env python3
"""Drive the locally-built AdMachin MCP 1.2.0 server over stdio.

Bypasses the stale Claude Code MCP manifest (a running session keeps the old tool
list; this talks straight to `node /Users/harry/admachin-mcp/dist/index.js`).

  schemas <name> [<name> ...]      print inputSchema for the named tools
  call <name> '<json-args>'        call one tool, print the result text
  list                             print all tool names

Reads the real ADMACHIN_PAT / ADMACHIN_API_BASE from ~/.claude.json (never printed).
"""
import json
import os
import select
import subprocess
import sys
import time

SERVER = os.environ.get("ADMACHIN_MCP_JS", "/Users/harry/admachin-mcp/dist/index.js")


def _pat_base():
    d = json.load(open(os.path.expanduser("~/.claude.json")))
    def find(s):
        for n, c in (s or {}).items():
            if "admachin" in n.lower():
                return c.get("env") or {}
        return {}
    e = find(d.get("mcpServers"))
    if not e:
        for _p, pc in (d.get("projects") or {}).items():
            e = find((pc or {}).get("mcpServers"))
            if e:
                break
    return e.get("ADMACHIN_PAT", ""), e.get("ADMACHIN_API_BASE", "https://admachin.com")


def session(messages, timeout=120):
    """Send init handshake + `messages` (JSON-RPC dicts). Return {id: response}."""
    pat, base = _pat_base()
    env = dict(os.environ, ADMACHIN_PAT=pat, ADMACHIN_API_BASE=base)
    p = subprocess.Popen(["node", SERVER], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, env=env, text=True, bufsize=1)

    def send(m):
        p.stdin.write(json.dumps(m) + "\n")
        p.stdin.flush()

    send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
          "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                     "clientInfo": {"name": "stdio-cli", "version": "0"}}})
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    want = set()
    for m in messages:
        send(m)
        if "id" in m:
            want.add(m["id"])
    out = {}
    start = time.time()
    while want and time.time() - start < timeout:
        r, _, _ = select.select([p.stdout], [], [], 1.0)
        if not r:
            continue
        line = p.stdout.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            m = json.loads(line)
        except Exception:
            continue
        if m.get("id") in want:
            out[m["id"]] = m
            want.discard(m["id"])
    try:
        p.stdin.close()
        p.terminate()
    except Exception:
        pass
    return out


def _tools_list():
    resp = session([{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}])
    return (resp.get(2, {}).get("result", {}) or {}).get("tools", [])


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "list":
        for t in _tools_list():
            print(t["name"])
    elif cmd == "schemas":
        wanted = set(sys.argv[2:])
        for t in _tools_list():
            if t["name"] in wanted:
                print(f"\n### {t['name']}\n{t.get('description','')[:300]}")
                print(json.dumps(t.get("inputSchema", {}), indent=2))
    elif cmd == "call":
        name = sys.argv[2]
        args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        resp = session([{"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                         "params": {"name": name, "arguments": args}}], timeout=240)
        m = resp.get(2)
        if not m:
            print("NO RESPONSE (timeout)")
            return
        if "error" in m:
            print("ERROR:", json.dumps(m["error"]))
            return
        res = m.get("result", {})
        if res.get("isError"):
            print("TOOL ERROR:")
        for c in res.get("content", []):
            if c.get("type") == "text":
                print(c["text"])
        if res.get("structuredContent"):
            print(json.dumps(res["structuredContent"], indent=2))
    else:
        print("unknown cmd", cmd)


if __name__ == "__main__":
    main()
