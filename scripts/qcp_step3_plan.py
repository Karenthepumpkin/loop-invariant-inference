#!/usr/bin/env python3
"""Parse an unrolled _qcp.c file and output a step-by-step QCP execution plan.

Recording points:
  - RP_pre_loop: state at while condition before entering the loop
  - RP_loop_body_end: state at loop body '}' — hit once per iteration (d0, d1, ...)
  - RP_break / RP_continue: state at break/continue (if any)

Usage: python qcp_step3_plan.py --file workspace/append_qcp_unrolled.c
"""

import sys, re, json, argparse
from pathlib import Path


def _strip_comments(line: str) -> str:
    s = re.sub(r'//.*$', '', line)
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.DOTALL)
    return s


def _find_matching_brace(lines: list, open_line: int) -> int:
    depth = 0
    started = False
    for i in range(open_line, len(lines)):
        clean = _strip_comments(lines[i])
        for ch in clean:
            if ch == '{':
                depth += 1
                started = True
            elif ch == '}':
                depth -= 1
                if started and depth == 0:
                    return i + 1  # 1-indexed
    return None


def parse_unrolled(filepath: str) -> dict:
    text = Path(filepath).read_text()
    lines = text.split('\n')

    while_line = None
    inv_branches = []
    break_lines = []
    continue_lines = []
    loop_body_end = None

    # --- pass 1: find while, inv block ---
    for i, line in enumerate(lines):
        if while_line is None and re.match(r'\s*while\s*\(', line):
            while_line = i + 1

        m_inv = re.match(r'\s*/\*@\s*Inv\s+(.+)', line)
        if m_inv:
            inv_branches = re.findall(r'\b(d\d+)\b', m_inv.group(1))
            j = i + 1
            while j < len(lines) and '*/' not in lines[j]:
                inv_branches += re.findall(r'\b(d\d+)\b', lines[j])
                j += 1

    if not while_line:
        return {"error": "No while loop found", "file": filepath}

    inv_branches = list(dict.fromkeys(inv_branches))  # deduplicate
    if not inv_branches:
        return {"error": "No Inv d0..dN block found. Run unroll_loop.py first.", "file": filepath}

    # --- pass 2: find loop body limits ---
    open_brace = None
    for i in range(while_line - 1, min(while_line + 5, len(lines))):
        if '{' in _strip_comments(lines[i]):
            open_brace = i
            break

    if open_brace is not None:
        loop_body_end = _find_matching_brace(lines, open_brace)

        for i in range(open_brace + 1, loop_body_end - 1 if loop_body_end else len(lines)):
            stripped = lines[i].strip()
            if re.match(r'^break\s*;', stripped):
                break_lines.append(i + 1)
            elif re.match(r'^continue\s*;', stripped):
                continue_lines.append(i + 1)

    # --- build recording points ---
    recording_points = []

    recording_points.append({
        "id": "RP_pre_loop",
        "line": while_line,
        "description": "Pre-loop state at while condition. Step to this line, check, then step INTO the loop body.",
    })

    if loop_body_end:
        recording_points.append({
            "id": "RP_loop_body_end",
            "line": loop_body_end,
            "description": f"Iteration-end state at loop body '}}'. Will be hit once per iteration: {', '.join(inv_branches[:-1])} each produce a state here; {inv_branches[-1]} exits the loop.",
        })

    for bl in break_lines:
        recording_points.append({
            "id": f"RP_break_L{bl}",
            "line": bl,
            "description": "Break statement. State here should imply post-condition.",
        })

    for cl in continue_lines:
        recording_points.append({
            "id": f"RP_continue_L{cl}",
            "line": cl,
            "description": "Continue statement. State here should satisfy the loop invariant.",
        })

    # --- build instructions ---
    instructions = [
        "1. mcp__qcp__load_target_file with the absolute path of this unrolled file",
        f"2. mcp__qcp__step until reaching line {while_line} (while condition).",
        f"3. mcp__qcp__check at line {while_line} -- RP_pre_loop: capture the pre-loop state.",
        "4. mcp__qcp__step INTO the loop body.",
    ]

    step_n = 5
    if loop_body_end:
        instructions.append(f"{step_n}. mcp__qcp__step through loop body statements to reach line {loop_body_end} (loop body '}}').")
        step_n += 1
        instructions.append(f"{step_n}. mcp__qcp__check at line {loop_body_end} -- RP_loop_body_end: capture iteration-end state for the active branch.")
        step_n += 1
        instructions.append(f"{step_n}. Continue stepping (loop will cycle back to while, re-enter for next branch). Repeat check at line {loop_body_end} for each active branch until {inv_branches[-1]} exits the loop.")
        step_n += 1

    for bl in break_lines:
        instructions.append(f"{step_n}. Ensure mcp__qcp__check at line {bl} -- RP_break.")
        step_n += 1
    for cl in continue_lines:
        instructions.append(f"{step_n}. Ensure mcp__qcp__check at line {cl} -- RP_continue.")
        step_n += 1

    instructions += [
        "",
        "After collecting all states:",
        f"  - Branches: {', '.join(inv_branches)}. {inv_branches[:-1]} each produce a state at RP_loop_body_end; {inv_branches[-1]} exits.",
        "  - For each branch, extract SEP (spatial, *-separated) and PROP (pure, &&-separated) from current_assertions.",
        "  - Together with RP_pre_loop, this gives N+1 layers of state data for N iterations of unrolling.",
        "  - Run mcp__qcp__symbolic at the function's last line for baseline witness counts.",
    ]

    plan = {
        "file": filepath,
        "while_line": while_line,
        "loop_body_end": loop_body_end,
        "break_lines": break_lines,
        "continue_lines": continue_lines,
        "inv_branches": inv_branches,
        "recording_points": recording_points,
        "instructions": instructions,
    }

    return plan


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    args = ap.parse_args()

    plan = parse_unrolled(args.file)
    print(json.dumps(plan, indent=2))
