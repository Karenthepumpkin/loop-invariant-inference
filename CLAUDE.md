# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Claude Code skill that automatically infers loop invariants for QCP (Qualified C Programming) C programs. It symbolically executes unrolled loops, diffs the resulting program states across iterations, and generates invariants for QCP verification.

The full step-by-step workflow lives in `SKILL.md`. This file covers architecture and conventions.

## Architecture

```
Input .c file
  → unroll_loop.py (switch-based loop unrolling, default depth 3)
  → symexec binary (QCP symbolic execution with --basic-assertion --primary-assertion)
  → qcp_parse_log.py (extract recording points from log → workspace/*_states.txt)
  → manual invariant inference (diff RP_pre_loop → RP_iter_2 → RP_iter_3)
  → symexec binary again (verify invariant)
```

### Key scripts

| Script | Role |
|--------|------|
| `scripts/unroll_loop.py` | Replaces `while` loops with switch-based unrolled iterations. Strips existing `/*@ Inv */` blocks. `--ensure-emp` replaces `Ensure` with `emp`. |
| `scripts/symexec` | Closed-source QCP symbolic execution binary (~8.9MB). Called with `--basic-assertion --primary-assertion` for Form 3 (basic separation logic) output. |
| `scripts/qcp_parse_log.py` | Parses symexec log into structured recording points (PROP/LOCAL/SEP sections). Supports both switch-mode and legacy markers. |

### Recording points

After parsing, each recording point (RP) captures the program state before one unrolled iteration's condition check:
- **RP_pre_loop**: Before first `if (cond && in_loop)` — loop entry state
- **RP_iter_2, RP_iter_3, ...**: Before each subsequent iteration's guard

LOCAL items (`&var == addr`) are QCP stack-variable bindings, same across all RPs. They are never part of the invariant.

## Separation logic form

This project uses **Form 3 (basic separation logic assertions)**, per QCP tutorial T3-2. This means:
- All expressions in assertions are **memory-independent** (`&px` not `px`, `x` not `*px`)
- Variable storage uses `store_ptr(&var, addr)` patterns in the tool's internal representation
- Output uses `data_at` predicates with explicit address variables

The `--basic-assertion` flag on symexec enforces this. Do not change to Form 1 (`*px == x`) or Form 2 (`store_int(px, x)`).

## Predicate reference system

Input files `#include` one of four headers. The corresponding reference and Coq library are:

| `#include` header | Reference file | Coq lib (`-slp` arg) |
|---|---|---|
| `dll_nodata_def.h` | `references/dll_nodata.md` | `dll_nodata_shape_lib` |
| `sll_nodata_def.h` | `references/sll_nodata.md` | `sll_nodata_shape_lib` |
| `dll_shape_def.h` | `references/dll_shape.md` | `dll_shape_lib` |
| `sll_shape_def.h` | `references/sll_shape.md` | `sll_shape_lib` |

The `_nodata` variants have structs with only pointer fields (`next`, `prev`). The `_shape` variants add an `int data` field. Each reference file documents predicate definitions, parameter orders, finite expansions, and common traps.

## Invariant construction rules

When building invariants from diff analysis:
1. **Frame items**: SEP predicates present in ALL RPs → invariant frame
2. **Sliding items**: Same predicate structure, advancing pointer values → track with `data_at(field_addr(p, next/prev), ...)`
3. **PROP constraints**: Intersect across ALL RPs. Transient items (loop-condition branches) are excluded.
4. **has_permission checklist**: For every pointer-typed variable whose name does NOT appear as first argument of any spatial predicate, add `has_permission(&var)`. Missing `has_permission` is the #1 failure cause.
5. **No LOCAL items in invariants**: They are QCP-internal and auto-managed.

## Directories

| Path | Purpose |
|------|---------|
| `workspace/` | Intermediate files (unrolled .c, symexec log, parsed states) |
| `tmp/` | Invariant test files and verification logs (gitignored) |
| `scripts/infra/` | QCP libraries and Coq infrastructure (.v, .vo, .vos, .glob files) |
| `references/` | Predicate documentation for each supported data structure |
