---
name: loop-invariant-inference
description: Automatically infer loop invariants for QCP form C programs to support code verification and correctness proofs. Useful for analyzing loops to identify properties that hold throughout execution and to prove loop correctness, especially for cases involving complex data structures and intricate memory manipulation.Triggered when users request invariant inference, loop-property discovery, assertion generation, or loop verification.
---

# Loop Invariant Inference

## Overview

Analyze loops and automatically infer invariants—properties that remain true throughout loop execution. The input file is already QCP-formatted (QCP struct/predicate names, `#include` header).

## Key Paths

**SKILL_DIR**: The skill's base directory (provided at invocation). All relative paths below use this.

| What | Where |
|------|-------|
| Skill workflow | `<SKILL_DIR>/SKILL.md` |
| Scripts (unroll, parse) | `<SKILL_DIR>/scripts/` |
| Predicate references | `<SKILL_DIR>/references/dll_nodata.md`, `sll_nodata.md`, `dll_shape.md`, `sll_shape.md` |
| Working directory | `<SKILL_DIR>/workspace/` |
| Invariant test file | `<SKILL_DIR>/tmp/<name>_inv.c` |
| QCP binary | `<SKILL_DIR>/scripts/symexec` |
| QCP infra | `<SKILL_DIR>/scripts/infra/` |

## PROHIBITED

| ❌ NEVER | ✅ INSTEAD |
|------|------|
| Any MCP tool (mcp__qcp__*) | Use Bash: `linux-binary/symexec` for all QCP operations |
| `Grep` / `Glob` | All paths are listed in Key Paths above |

## Available Predicates

The input file's `#include` header provides QCP predicates. Read the corresponding reference for predicate definitions and semantics:

| Header in `#include` | Reference |
|------|------|
| `dll_nodata_def.h` | `references/dll_nodata.md` |
| `dll_shape_def.h` | `references/dll_shape.md` |
| `sll_nodata_def.h` | `references/sll_nodata.md` |
| `sll_shape_def.h` | `references/sll_shape.md` |

## Workflow

### 1. Symbolic Execution & State Collection

All tools are self-contained within `<SKILL_DIR>/scripts/` — no external dependencies.

1.1. **Unroll the loop** using switch-based pattern:
```
python <SKILL_DIR>/scripts/unroll_loop.py --file <input_file> --output <SKILL_DIR>/workspace/<name>_unrolled.c --ensure-emp
```

1.2. **Run symexec** (use absolute path, do NOT cd):
```
<SKILL_DIR>/scripts/symexec \
  --goal-file=<SKILL_DIR>/tmp/<name>_goal.v \
  --proof-auto-file=<SKILL_DIR>/tmp/<name>_proof_auto.v \
  --proof-manual-file=<SKILL_DIR>/tmp/<name>_proof_manual.v \
  --coq-logic-path=SimpleC.EE.infra.<lib> \
  -slp <SKILL_DIR>/scripts/infra/ SimpleC.EE.infra \
  --input-file=<SKILL_DIR>/workspace/<name>_unrolled.c \
  --basic-assertion --primary-assertion \
  2>&1 | tee <SKILL_DIR>/workspace/<name>_symexec.log
```
`<lib>`: read from the `#include` — `dll_nodata_def.h` → `dll_nodata_shape_lib`, `sll_nodata_def.h` → `sll_nodata_shape_lib`, etc.

**Gate**: Log must end with "Successfully finished symbolic execution".

1.3. **Parse the log**:
```
python <SKILL_DIR>/scripts/qcp_parse_log.py \
  --file <SKILL_DIR>/workspace/<name>_symexec.log \
  --out-states <SKILL_DIR>/workspace/<name>_states.txt \
  --out-json <SKILL_DIR>/workspace/<name>_states.json
```

1.4. **Recording points**: Each RP captures the state before one unrolled iteration's condition check:
- **RP_pre_loop**: Before the first `if (cond && in_loop)` — loop entry state.
- **RP_iter_2**, **RP_iter_3**, ...: Before each subsequent iteration's condition check.
- The loop body executes between consecutive RPs. SEP size grows as QCP unfolds list predicates.

**Gate**: `_states.txt` must contain at least RP_pre_loop and RP_iter_2.

### 2. Loop Invariant Inference

2.1. **Analyze loop purpose**: Read the loop body. What operation? Which variables move?

2.2. **Diff analysis across consecutive RPs**: Compare `RP_pre_loop` → `RP_iter_2` → `RP_iter_3`:
- **Frame items**: SEP items present in ALL RPs → invariant frame (e.g. untouched lists)
- **Sliding items**: Same predicate structure but pointer values advance → track with `data_at(field_addr(p, next/prev), ...)`
- **Unfolding items**: New `data_at` nodes appear each iteration → the list is being traversed

2.3. **Post-loop check**: Read lines after the `while` loop. If a variable is accessed post-loop but not covered by predicates, it MUST be in the invariant frame.

2.4. **LOCAL (address bindings)**: Items of the form `( &var == addr )` are internal QCP stack-variable bindings. They are the same across all RPs and are automatically managed — do NOT include them in the invariant.

2.5. **PROP (pure constraints)**: All other `&&`-terminated items are pure logical constraints. Intersect across ALL RPs — those appearing in every RP are invariant. Items appearing only in some RPs are transient (e.g. loop-condition branches).

2.6. **MANDATORY — has_permission checklist**:
Count ALL pointer-typed variables (params + locals). For each: if its name does NOT appear as the first argument of any spatial predicate, add `has_permission(&var)`. Number of `has_permission` entries must equal number of uncovered variables. Missing `has_permission` is the #1 cause of manual witnesses.

### 3. QCP Verification

3.1. **Write file**: Replace `/* INFILL */` with `/*@ Inv <invariant> */`. Save to `<SKILL_DIR>/tmp/<name>_inv.c`.

3.2. **Verify via symexec** (absolute path, do NOT cd):
```
<SKILL_DIR>/scripts/symexec \
  --goal-file=<SKILL_DIR>/tmp/<name>_goal.v \
  --proof-auto-file=<SKILL_DIR>/tmp/<name>_proof_auto.v \
  --proof-manual-file=<SKILL_DIR>/tmp/<name>_proof_manual.v \
  --coq-logic-path=SimpleC.EE.infra.<lib> \
  -slp <SKILL_DIR>/scripts/infra/ SimpleC.EE.infra \
  --input-file=<SKILL_DIR>/tmp/<name>_inv.c \
  --basic-assertion --primary-assertion \
  2>&1 | tee <SKILL_DIR>/tmp/<name>_verify.log
```

3.3. **Evaluate**:
- Log ends with "Successfully finished symbolic execution" → `grep -c "Admitted\." <SKILL_DIR>/tmp/<name>_proof_manual.v`
  - `0` → `QCP_VERIFIED: YES` → proceed to Output
  - `> 0` → `QCP_VERIFIED: NO` → retry from Step 2
- Log contains error → `QCP_VERIFIED: NO` → retry from Step 2

3.4. **Retry (max 2 additional attempts)**: If `QCP_VERIFIED: NO`, analyze the failure and refine the invariant:
- Check `<SKILL_DIR>/tmp/<name>_proof_manual.v` — which goals were `Admitted`? These are the unproven proof obligations (entailment, safety, return, etc.).
- Re-read the RPs from `_states.txt`, paying attention to which items caused the failure.
- Adjust the invariant (reorder SEP, add missing predicates, fix pure constraints).
- Repeat from Step 3.1 with the refined invariant.
- If all retries exhausted and still NO, output `QCP_VERIFIED: NO` as final result.

### 4. Output

```
QCP_VERIFIED: YES  (or NO, after retries)
```c
<complete file with invariant inserted>
```

### 5. Cleanup

Delete generated files from `workspace/` and `<SKILL_DIR>/tmp/`.