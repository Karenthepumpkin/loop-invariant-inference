#!/usr/bin/env python3
"""Post-process agent results: copy transcript, generate conversation.txt and metrics.json."""
import json, shutil, sys
from pathlib import Path

TRANSCRIPT = Path(sys.argv[1]).resolve()
RESULT = Path(sys.argv[2])

# Copy transcript
shutil.copy2(str(TRANSCRIPT), str(RESULT / "agent_transcript.jsonl"))

# Parse
tool_counts = {}
conv_lines = []
with open(TRANSCRIPT) as fh:
    for line in fh:
        try: data = json.loads(line)
        except: continue
        t = data.get("type", "")
        msg = data.get("message", {})
        content = msg.get("content", "")
        if isinstance(content, list):
            for block in content:
                if not isinstance(block, dict): continue
                bt = block.get("type", "")
                if bt == "thinking":
                    text = block.get("thinking", "")
                    conv_lines.append(f"\n{'='*60}\n[THINKING] ({len(text)} chars)\n{'='*60}\n{text}")
                elif bt == "text":
                    conv_lines.append(f"\n[TEXT]\n{block.get('text', '')}")
                elif bt == "tool_use":
                    name = block.get("name", "?")
                    tool_counts[name] = tool_counts.get(name, 0) + 1
                    inp = block.get("input", {})
                    if name == "Read": cmd = f"Read: {inp.get('file_path', '?')}"
                    elif name == "Bash": cmd = f"Bash: {inp.get('command', str(inp)[:300])}"
                    elif name == "Write": cmd = f"Write: {inp.get('file_path', '?')}"
                    else: cmd = f"{name}: {str(inp)[:300]}"
                    conv_lines.append(f"\n[TOOL: {name}]\n{cmd}")
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    rstr = str(block.get("content", ""))
                    is_err = block.get("is_error", False)
                    tag = "TOOL_RESULT (ERROR)" if is_err else "TOOL_RESULT"
                    if len(rstr) > 1000: rstr = rstr[:1000] + f"\n... [truncated, total {len(rstr)} chars]"
                    conv_lines.append(f"\n[{tag}]\n{rstr}")

(RESULT / "conversation.txt").write_text("\n".join(conv_lines))
(RESULT / "metrics.json").write_text(json.dumps(
    {"tool_uses": sum(tool_counts.values()), "tool_breakdown": tool_counts}, indent=2))
print(f"Saved: {sum(tool_counts.values())} tools, {dict(tool_counts)}")
