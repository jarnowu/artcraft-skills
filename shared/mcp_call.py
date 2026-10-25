#!/usr/bin/env python3
"""Call tools on an MCP server that speaks JSON-RPC over stdio, from the shell.

Use it when the app's MCP tools are not loaded in the session, for example to drive a running
app through its CLI's bridge mode. All calls in one invocation share one server session, so ids
and edits from earlier calls are still there for later ones.

usage:
  python mcp_call.py [--out-dir DIR] [--list] -- SERVER_COMMAND... [:: TOOL JSON]...

  python mcp_call.py --list -- "C:/Program Files/FigCraft/figcraft-cli.exe" mcp --attach 7981
  python mcp_call.py --out-dir shots -- "C:/Program Files/FigCraft/figcraft-cli.exe" mcp --attach 7981 \
      :: inspect_document '{"depth":2}' :: screenshot '{}'

Text results are printed; image results are written to --out-dir (default: the current folder)
as <n>-<tool>.png and their paths printed. Exit status is 1 if any call returned an error.
"""
import argparse
import base64
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    argv = sys.argv[1:]
    if "--" not in argv:
        sys.exit("usage: mcp_call.py [--out-dir DIR] [--list] -- SERVER_COMMAND... [:: TOOL JSON]...")
    split = argv.index("--")
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=".")
    parser.add_argument("--list", action="store_true", help="print the server's tools and their parameters")
    opts = parser.parse_args(argv[:split])

    rest = argv[split + 1:]
    server, calls = [], []
    if "::" in rest:
        first = rest.index("::")
        server, tail = rest[:first], rest[first:]
        while tail:
            if len(tail) < 3 or tail[0] != "::":
                sys.exit("each call is written as :: TOOL '{json arguments}'")
            try:
                arguments = json.loads(tail[2])
            except json.JSONDecodeError as e:
                sys.exit(f"arguments for {tail[1]} are not valid JSON: {e}")
            calls.append((tail[1], arguments))
            tail = tail[3:]
    else:
        server = rest
    if not server:
        sys.exit("no server command given")

    proc = subprocess.Popen(server, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8")
    next_id = 0

    def send(method, params=None, notify=False):
        nonlocal next_id
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            next_id += 1
            msg["id"] = next_id
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()
        if notify:
            return None
        # Skip notifications (progress, logs) until the reply with our id arrives.
        while True:
            line = proc.stdout.readline()
            if not line:
                sys.exit("server closed the connection: " + proc.stderr.read().strip()[:500])
            reply = json.loads(line)
            if reply.get("id") == next_id:
                return reply

    init = send("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                               "clientInfo": {"name": "mcp_call", "version": "1"}})
    if "error" in init:
        sys.exit("initialize failed: " + json.dumps(init["error"]))
    send("notifications/initialized", notify=True)

    if opts.list:
        for tool in send("tools/list")["result"]["tools"]:
            props = tool.get("inputSchema", {}).get("properties", {})
            print(f"{tool['name']}({', '.join(props)}): {tool.get('description', '').splitlines()[0][:160]}")

    failed = False
    os.makedirs(opts.out_dir, exist_ok=True)
    for n, (tool, arguments) in enumerate(calls, 1):
        reply = send("tools/call", {"name": tool, "arguments": arguments})
        if "error" in reply:
            failed = True
            print(f"[{n}] {tool} ERROR {json.dumps(reply['error'])}")
            continue
        result = reply["result"]
        failed |= bool(result.get("isError"))
        print(f"[{n}] {tool}" + (" ERROR" if result.get("isError") else ""))
        for item in result.get("content", []):
            if item.get("type") == "image":
                path = os.path.join(opts.out_dir, f"{n}-{tool}.png")
                with open(path, "wb") as f:
                    f.write(base64.b64decode(item["data"]))
                print(f"  image saved: {os.path.abspath(path)}")
            elif item.get("type") == "text":
                print(item["text"])
    proc.stdin.close()
    try:
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
