#!/usr/bin/env python3
"""
Parse symexec log and extract recording-point states for invariant inference.

Supports both legacy markers (Before while-loop invariant etc.) and
switch-based unrolling (captures state before each if (cond && in_loop) guard).

Usage:
  python scripts/qcp_parse_log.py --file workspace/<name>_symexec.log \
      --out-states workspace/<name>_states.txt --out-json workspace/<name>_states.json
"""

import sys, re, json, argparse
from pathlib import Path


# ---- legacy log markers ----
MARKER_BEFORE_WHILE = "Before while-loop invariant"
MARKER_PARTIAL_INV  = "1-st assertion try to do Partial Inv Check"
MARKER_AFTER_BODY   = "After while-body"
MARKER_AFTER_COND   = "After while-condition, before while-body"

# ---- switch-mode patterns ----
# Matches: (ps type 5): if ((y && in_loop_0))
SWITCH_IF_RE = re.compile(r'\(ps type \d+\)\s*:\s*if\s*\(\((.+?)\s*&&\s*(in_loop\b[^)]*)\s*\)\)')

ASSERT_BEGIN_RE = re.compile(r'-{3,}\s*Assertion begin\s*-{3,}')
ASSERT_END_RE   = re.compile(r'-{3,}\s*Assertion end\s*-{3,}')
CTRL_BEFORE_RE  = re.compile(r'^\s*Before ControlFlowExec\s*:\s*$')


def parse_assertion_body(body: str) -> dict:
    """Parse a single assertion body into structured parts (PROP/LOCAL/SEP)."""
    result = {
        "branch_name": None, "next_branch_name": None, "spec_name": None,
        "exists": [], "var_list": [],
        "prop": [], "local": [], "sep": [],
        "raw": body.strip(),
    }

    lines = body.strip().split('\n')
    section = None  # 'PROP', 'LOCAL', 'SEP', or None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        m_branch = re.match(r'branch name\s*:\s*(.*)', stripped)
        if m_branch:
            result["branch_name"] = m_branch.group(1).strip()
            continue

        m_next = re.match(r'next branch name\s*:\s*(.*)', stripped)
        if m_next:
            result["next_branch_name"] = m_next.group(1).strip()
            continue

        m_spec = re.match(r'spec name\s*:\s*(.*)', stripped)
        if m_spec:
            result["spec_name"] = m_spec.group(1).strip()
            continue

        m_exists = re.match(r'exists\s+(.+?)\s*,\s*$', stripped)
        if m_exists:
            result["exists"] = m_exists.group(1).strip().split()
            continue

        m_vars = re.match(r'^([\w_]+(?:\s+[\w_]+)*)\s*,\s*$', stripped)
        if m_vars and not stripped.startswith('(') and not stripped.startswith('['):
            result["var_list"] = m_vars.group(1).strip().split()
            continue

        # Detect section headers
        if stripped.startswith('PROP['):
            section = 'PROP'
            continue
        elif stripped.startswith('LOCAL['):
            section = 'LOCAL'
            continue
        elif stripped.startswith('SEP['):
            section = 'SEP'
            continue
        elif stripped == ']':
            section = None
            continue

        # Parse items based on current section
        if section == 'PROP':
            item = stripped.rstrip(';').strip()
            if item:
                result["prop"].append(item)
        elif section == 'LOCAL':
            item = stripped.rstrip(';').strip()
            if item:
                result["local"].append(item)
        elif section == 'SEP':
            item = stripped.rstrip('*').strip()
            if item and item != ',':
                result["sep"].append(item)
        else:
            # Legacy format: &var == addr → LOCAL, other && → PROP, * → SEP
            if stripped.endswith('&&'):
                item = stripped[:-2].strip()
                if item:
                    # Address-of bindings: ( &var == addr ) → LOCAL
                    if re.match(r'\(\s*&\s*\w+\s*==\s*\w+\s*\)$', item):
                        result["local"].append(item)
                    else:
                        result["prop"].append(item)
            elif stripped.endswith('*'):
                sep_item = stripped[:-1].strip()
                if sep_item:
                    result["sep"].append(sep_item)
            elif stripped == 'emp':
                result["sep"].append('emp')
            elif stripped not in (',', '@'):
                result["sep"].append(stripped)

    return result


def extract_assertion_block(lines: list[str], start_i: int) -> tuple[int, str | None]:
    """Extract assertion body between Assertion begin/end markers."""
    if start_i >= len(lines): return start_i, None
    if not ASSERT_BEGIN_RE.match(lines[start_i]): return start_i, None
    body_lines = []
    i = start_i + 1
    while i < len(lines):
        if ASSERT_END_RE.match(lines[i]):
            return i + 1, '\n'.join(body_lines)
        body_lines.append(lines[i])
        i += 1
    return i, None


def _is_inv_block(body: str) -> bool:
    stripped = body.strip()
    return (stripped == 'emp' or stripped == ',' or stripped == ',\nemp'
            or stripped == '' or stripped == ',\n\nemp')


def parse_legacy_markers(lines: list[str]) -> list[dict]:
    """Parse recording points using legacy while-loop markers."""
    recording_points = []
    counts = {"before_while": 0, "after_body": 0, "partial_inv": 0, "after_cond": 0}
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        marker = None
        if stripped == MARKER_BEFORE_WHILE: marker = "before_while"
        elif MARKER_PARTIAL_INV in stripped: marker = "partial_inv"
        elif stripped == MARKER_AFTER_BODY: marker = "after_body"
        elif stripped == MARKER_AFTER_COND: marker = "after_cond"

        if marker:
            counts[marker] += 1
            occ = counts[marker]
            # Find next assertion block
            j = i + 1
            while j < len(lines):
                if ASSERT_BEGIN_RE.match(lines[j]):
                    _, body = extract_assertion_block(lines, j)
                    if body is not None and not _is_inv_block(body):
                        rp_type = {
                            "before_while": "RP_pre_loop" if occ == 1 else "RP_iter_start",
                            "partial_inv": "RP_partial_inv",
                            "after_body": "RP_iter_end",
                            "after_cond": "RP_after_cond",
                        }[marker]
                        recording_points.append({
                            "type": rp_type, "occurrence": occ,
                            "line": i + 1, "state": parse_assertion_body(body),
                        })
                    break
                j += 1
        i += 1
    return recording_points


def parse_switch_markers(lines: list[str]) -> list[dict]:
    """Parse recording points from switch-based unrolled code.

    Captures state before each 'if (cond && in_loop_N)' check (pre-state).
    The pre-state of iteration N is the post-state of iteration N-1,
    so diff analysis between consecutive iterations works naturally.
    """
    recording_points = []
    occurrence = 0

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        # Look for: (ps type 5): if ((cond && in_loop_N))
        m = SWITCH_IF_RE.match(stripped)
        if m:
            # Walk backward to find the last assertion block before this if-check
            last_assertion = None
            j = i - 1
            while j >= 0:
                if ASSERT_END_RE.match(lines[j]):
                    k = j - 1
                    while k >= 0:
                        if ASSERT_BEGIN_RE.match(lines[k]):
                            body = '\n'.join(lines[k+1:j])
                            if not _is_inv_block(body):
                                last_assertion = body
                            break
                        k -= 1
                    break
                j -= 1

            if last_assertion:
                occurrence += 1
                cond = m.group(1).strip()
                rp_type = "RP_pre_loop" if occurrence == 1 else f"RP_iter_{occurrence}"
                recording_points.append({
                    "type": rp_type, "occurrence": occurrence,
                    "line": i + 1, "condition": cond,
                    "state": parse_assertion_body(last_assertion),
                })
        i += 1

    return recording_points


def simplify_state(state: dict) -> dict:
    return {
        "PROP": state.get("prop", []),
        "LOCAL": [l for l in state.get("local", []) if "in_loop" not in l],
        "SEP": [s for s in state.get("sep", []) if "in_loop" not in s],
        "exists": state.get("exists", []),
    }


def format_states_txt(data: dict) -> str:
    out = []
    for rp in data["recording_points"]:
        s = simplify_state(rp["state"])
        out.append(f"--- {rp['type']} (line {rp['line']}, #{rp['occurrence']}) ---")
        if s['exists']:
            out.append(f"  exists: {' '.join(s['exists'])}")
        if s['PROP']:
            out.append(f"  PROP:")
            for p in s['PROP']:
                out.append(f"    {p}")
        if s['LOCAL']:
            out.append(f"  LOCAL:")
            for l in s['LOCAL']:
                out.append(f"    {l}")
        if s['SEP']:
            out.append(f"  SEP:")
            for sp in s['SEP']:
                out.append(f"    {sp}")
        out.append("")
    return '\n'.join(out)


def parse_log(filepath: str) -> dict:
    lines = Path(filepath).read_text().split('\n')

    # Try switch-mode first
    recording_points = parse_switch_markers(lines)

    # Fall back to legacy markers if no switch-mode RPs found
    if not recording_points:
        recording_points = parse_legacy_markers(lines)

    counts = {}
    for rp in recording_points:
        t = rp["type"]
        counts[t] = counts.get(t, 0) + 1

    return {
        "file": filepath,
        "recording_points": recording_points,
        "summary": counts,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--out-states", default=None)
    ap.add_argument("--out-json", default=None)
    args = ap.parse_args()

    data = parse_log(args.file)

    s = data["summary"]
    print(f"Parsed {len(data['recording_points'])} recording points from {args.file}")
    for t, c in sorted(s.items()):
        print(f"  {t}: {c}")
    print()

    for rp in data["recording_points"]:
        st = simplify_state(rp["state"])
        sep_names = [x.split('(')[0].strip() for x in st['SEP'][:6]]
        cond = rp.get('condition', '')
        cond_str = f' cond=({cond})' if cond else ''
        print(f"[{rp['type']}] #{rp['occurrence']} L{rp['line']}{cond_str}")
        print(f"  PROP:  {st['PROP'][:3]}{'...' if len(st['PROP'])>3 else ''}")
        print(f"  LOCAL: {st['LOCAL'][:3]}{'...' if len(st['LOCAL'])>3 else ''}")
        print(f"  SEP:   {sep_names}{'...' if len(st['SEP'])>6 else ''}")
        print()

    if args.out_states:
        Path(args.out_states).write_text(format_states_txt(data))
        print(f"States written to {args.out_states}")

    if args.out_json:
        json_data = {
            "file": data["file"],
            "summary": data["summary"],
            "recording_points": [
                {
                    "type": rp["type"], "occurrence": rp["occurrence"],
                    "line": rp["line"],
                    "condition": rp.get("condition", ""),
                    "state": simplify_state(rp["state"]),
                }
                for rp in data["recording_points"]
            ]
        }
        Path(args.out_json).write_text(json.dumps(json_data, indent=2))
        print(f"JSON written to {args.out_json}")
