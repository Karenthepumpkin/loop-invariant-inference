#!/usr/bin/env python3
"""
Unroll while loops using C-level switch statements for QCP symbolic execution.

Pattern (matching QCP_examples/LLM_friendly_cases/test_append_switch.c):
  int in_loop = 1;
  // repeat N times:
  if (cond && in_loop)
      switch (in_loop) {
          case 1:
              /*@ cond */    // QCP annotation for strategy firing
              body           // break→in_loop=0;break, continue→break
              break;
          default: in_loop = 0;
      }
  else in_loop = 0;

Usage:
  python unroll_loop.py --file <path> [--depth N] [--output <path>] [--force]
"""

import re
import argparse
from pathlib import Path


def find_matching_brace(text: str, open_pos: int) -> int:
    depth = 1; i = open_pos + 1
    while i < len(text) and depth > 0:
        if text[i] == '{': depth += 1
        elif text[i] == '}': depth -= 1
        i += 1
    return i - 1


def find_matching_paren(text: str, open_pos: int) -> int:
    depth = 1; i = open_pos + 1
    while i < len(text) and depth > 0:
        if text[i] == '(': depth += 1
        elif text[i] == ')': depth -= 1
        i += 1
    return i - 1


def find_while_loops(text: str) -> list[dict]:
    loops = []
    pattern = re.compile(r'\bwhile\s*\(')
    for m in pattern.finditer(text):
        cond_start = text.index('(', m.end() - 1)
        cond_end = find_matching_paren(text, cond_start)
        pos = cond_end + 1
        while pos < len(text) and text[pos] in ' \t\n\r': pos += 1
        if pos >= len(text): continue
        if text[pos] == '{':
            body_start, body_end = pos, find_matching_brace(text, pos)
            is_block = True
        else:
            body_start, body_end = pos, text.find(';', pos)
            is_block = False
        loops.append({
            'start': m.start(), 'cond_start': cond_start, 'cond_end': cond_end,
            'body_start': body_start, 'body_end': body_end, 'is_block': is_block,
            'cond_text': text[cond_start+1:cond_end].strip(),
        })
    return loops


def _get_indent(text: str, pos: int) -> str:
    line_start = text.rfind('\n', 0, pos) + 1
    return re.match(r'^(\s*)', text[line_start:pos]).group(1) or ''


def _reindent(text: str, indent: str) -> str:
    return '\n'.join(indent + line for line in text.split('\n'))


def transform_breaks(body: str) -> str:
    """break → in_loop=0;break, continue → break"""
    body = re.sub(r'\bbreak\s*;', 'in_loop = 0; break;', body)
    body = re.sub(r'\bcontinue\s*;', 'break;', body)
    return body


def unroll_switch(text: str, depth: int = 3, force: bool = False) -> str:
    loops = find_while_loops(text)
    if not loops: return text

    result_parts = []
    last_end = 0

    for loop in loops:
        result_parts.append(text[last_end:loop['start']])
        indent = _get_indent(text, loop['start'])
        body_indent = indent + '    '
        cond = loop['cond_text']

        # Extract and transform loop body
        if loop['is_block']:
            body = text[loop['body_start']+1:loop['body_end']]
        else:
            body = text[loop['body_start']:loop['body_end']+1]
        body = transform_breaks(body)

        # Build unrolled blocks
        unrolled = [f'{indent}int in_loop = 1;', '']
        for n in range(1, depth + 1):
            block = []
            block.append(f'{indent}// === Unrolled iteration {n}/{depth} ===')
            block.append(f'{indent}if ({cond} && in_loop)')
            block.append(f'{indent}    switch (in_loop) {{')
            block.append(f'{indent}        case 1:')
            for line in body.split('\n'):
                block.append(f'{body_indent}{line}')
            block.append(f'{body_indent}break;')
            block.append(f'{indent}        default:')
            block.append(f'{indent}            in_loop = 0;')
            block.append(f'{indent}    }}')
            block.append(f'{indent}else')
            block.append(f'{indent}    in_loop = 0;')
            unrolled.append('\n'.join(block))

        result_parts.append('\n'.join(unrolled))
        last_end = loop['body_end'] + 1

    result_parts.append(text[last_end:])
    return '\n'.join(result_parts)


def main():
    parser = argparse.ArgumentParser(description='Unroll while loops using switch-based pattern for QCP')
    parser.add_argument('--file', required=True, help='C source file path')
    parser.add_argument('--depth', type=int, default=3, help='Number of unrolled iterations')
    parser.add_argument('--output', default=None, help='Output file path')
    parser.add_argument('--force', action='store_true', help='Overwrite existing Inv')
    parser.add_argument('--ensure-emp', action='store_true', help='Replace Ensure with emp')
    args = parser.parse_args()

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: file not found: {args.file}", file=__import__('sys').stderr)
        __import__('sys').exit(1)

    original = filepath.read_text()
    # Strip existing Inv blocks
    original = re.sub(r'/\*@\s*Inv\b.*?\*/\s*', '', original, flags=re.DOTALL)
    modified = unroll_switch(original, depth=args.depth, force=args.force)

    if args.ensure_emp:
        modified = re.sub(r'Ensure\s+[^*]+?\*/', 'Ensure  emp */', modified, flags=re.DOTALL)

    output_path = args.output or str(filepath.parent / f'{filepath.stem}_unrolled.c')
    Path(output_path).write_text(modified)
    print(f"Written: {output_path}")


if __name__ == '__main__':
    main()
