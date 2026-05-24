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
| Any MCP tool (mcp__qcp__*) | Use Bash: `<SKILL_DIR>/scripts/symexec` for all QCP operations |
| `Grep` / `Glob` | All paths are listed in Key Paths above |
| Read any file outside the whitelist below | Use only permitted paths |

## File Access Policy (WHITELIST)

You may ONLY Read files under these paths:
- `<SKILL_DIR>/SKILL.md`
- `<SKILL_DIR>/references/` (predicate definitions)
- `<RESULT_DIR>/workspace/` and `<RESULT_DIR>/tmp/` (your own output)
- The assigned input file

EVERYTHING else is forbidden, including:
- Other agents' result directories
- `/home/tzh66/qcp_skill/`
- `/home/tzh66/QualifiedCProgramming/`
- Any `.vo`, `.strategies`, `_CoqProject` file
- Any previously-run `test_results_*` directory
- Any file under `/home/tzh66/.claude/`

Violating this whitelist → your result is invalid.

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

**Gate**: `tail -3 <SKILL_DIR>/workspace/<name>_symexec.log` must show "Successfully finished symbolic execution". **NEVER Read the full log** — it is parsed by step 1.3.

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

1.5. **Snapshot content**: Each RP in `_states.txt` has the following sections:

```
--- RP_pre_loop (line 1139, #1) ---
  exists: y_289
  PROP:
    (x@pre !=  0 )
  LOCAL:
    ( &x == x_275_addr )
    ( &y == y_272_addr )
  SEP:
    data_at ( &(x@pre->next) , struct list* , y_289 )
    dlistrep_shape (y_289, x@pre)
```

| Section | Meaning |
|------|------|
| `RP_<name> (line N, #M)` | Snapshot name, source line in the unrolled file, and RP occurrence number. |
| `exists:` | Existentially quantified variables. QCP introduces these as fresh symbolic values during list unfolding (e.g., `y_289` for the next node). Each iteration may add new `exists` variables as predicates unfold deeper. |
| `PROP:` | Pure logical constraints (`&&`-separated in the parsed output). Boolean conditions on values: pointer non-null (`x@pre != 0`), equalities, inequalities. These constrain the symbolic state. |
| `LOCAL:` | Stack-variable address bindings (`&var == addr`). QCP-internal mapping from source variable names to their stack addresses. Always identical across all RPs — never includes these in the invariant. |
| `SEP:` | Spatial (separation logic) predicates describing heap ownership. Includes `data_at(addr, type, value)` for individual fields and shape predicates (`dlistrep_shape`, `sll_nodata`, etc.) for recursive structures. SEP is the invariant's main source — these predicates define what memory the loop owns. |

Key observations:
- **PROP grows**: Each iteration that enters the loop body adds non-null constraints for newly traversed nodes.
- **SEP unfolds**: Shape predicates like `dlistrep_shape(y_289, x@pre)` get unfolded into `data_at` nodes + a recursive `dlistrep_shape` on the rest. This is how the snapshot shows list traversal progress.
- **exists grows**: Each unfold introduces fresh existential variables for the newly exposed nodes.

### 2. Loop Invariant Inference

2.1. **Analyze loop purpose**: Read the loop body. What operation? Which variables move?

2.2. **Diff analysis across consecutive RPs**: Compare `RP_pre_loop` → `RP_iter_2` → `RP_iter_3`:
- **Frame items**: SEP items present in ALL RPs → invariant frame (e.g. untouched lists)
- **Sliding items**: Same predicate structure but pointer values advance → track with shape predicates using program variables, e.g., `dlistrep_shape(u, t)` where `u` and `t` are the advancing pointers
- **Unfolding items**: New `data_at` nodes appear each iteration → the list is being traversed

2.3. **Post-loop check**: Read lines after the `while` loop. If a variable is accessed post-loop but not covered by predicates, it MUST be in the invariant frame.

2.4. **LOCAL (address bindings)**: Items of the form `( &var == addr )` are internal QCP stack-variable bindings. They are the same across all RPs and are automatically managed — do NOT include them in the invariant.

2.5. **PROP (pure constraints)**: RP intersection is the starting point but usually insufficient. Essential PROP constraints often do not appear in any RP snapshot. Infer additional PROP from the code path leading to the loop:

- **Non-null from branch guards**: Read the code before the loop. If the loop is only reachable under a condition (e.g., `if (x == 0) return; ... t = x;`), add the implied non-null constraints to PROP (here: `x != 0`, `t != 0`).
- **Invariant equalities from assignments**: If the loop body contains an assignment (e.g., `u = t->next`, `w = v`) and the assigned variable is not modified again in the same iteration, the equality may be useful in PROP — but only when no shape predicate already encodes the same link. E.g., if `dllseg_shape(x, 0, t, u)` is already present, `u == t->next` is redundant (the predicate's last node `t` has `t->next == u` by definition) and may cause `dup_data_at`.
- **Validate every PROP against all RPs**: Write PROP as C expressions (`t != 0`, not `t_val != 0`). Verify each constraint holds in every RP.

2.6. **Key predicates**:

- `data_at(addr, type, value)`: Declares ownership of a heap cell at address `addr`. QCP can only read/write a field through an existing `data_at` for it. Shape predicates (`dlistrep_shape`, `dllseg_shape`) are recursively defined; strategies unfold them into `data_at` nodes to expose individual fields for the loop body.

- `has_permission(&var)`: Declares that the stack cell for `var` exists but its value is undefined (QCP represents it as `undef_data_at`). It does NOT grant permission to dereference `var` — dereference permission comes from `data_at` or shape predicates. Local variables assigned in the loop body need `has_permission` if not covered by a shape predicate.

**`has_permission` checklist**: Add `has_permission(&var)` when the loop body operates on a pointer (dereference, field access, assignment through it) but that pointer is not already covered by a spatial predicate. Do NOT add `has_permission` for:
- Freshly declared, uninitialized pointers that aren't yet accessed.
- Pointers that already appear as the first argument of a spatial predicate (predicate ownership implies permission).

For each pointer-typed variable, check: (1) is it dereferenced/assigned-through in the loop body? (2) does it already appear as arg[0] of a SEP predicate? If yes to (1) and no to (2), add `has_permission(&var)`. Missing `has_permission` for an actually-accessed pointer is the #1 cause of manual witnesses.

2.7. **Assemble the invariant**: Write the invariant in `/*@ Inv Assert ... */` format.

`/*@ Inv Assert ... */` **replaces** the entire program state at the loop head. Any pre-loop stack binding not carried into the invariant may produce unprovable manual proof obligations. Use the 2.6 checklist to ensure every parameter and assigned local variable is covered.

**Overall form**: `PROP1 && PROP2 && ... && SEP1 * SEP2 * ...`
- PROP constraints are C expressions joined by `&&` (`t != 0`, `u == t->next`)
- SEP predicates are shape predicates (`dlistrep_shape(...)`, `dllseg_shape(...)`) joined by `*`
- Shape predicate arguments use program variable names (`x`, `t`, `u`, `y`) and C field expressions (`t->prev`) directly. QCP handles existential quantification automatically — no `exists` keyword or `data_at` wrappers needed.
- `has_permission(&var)` is written in SEP, joined by `*`

**SEP — from diff analysis**:
- **Local pointer variables**: If a pointer variable appears as a shape predicate argument, QCP handles its binding automatically — no extra `data_at` needed. Only add `has_permission(&var)` per 2.6 when the pointer needs permission but does not appear in any SEP predicate.
- **Frame items**: Shape predicates identical across all RPs → keep as-is.
- **Sliding items**: Replace the sliding argument with the program variable name. E.g., `dlistrep_shape(y_289, x@pre)` in pre_loop slides to `dlistrep_shape(y_297, y_289)` in iter_2 → write as `dlistrep_shape(u, t)`.
- **Unfolding items** (from 2.2): Diagnostic signal. Write the folded shape predicate, not individual `data_at` nodes.

**PROP — from 2.5 + RP validation**:
- Every PROP constraint inferred in 2.5 must be validated against all RPs.
- Write as C expressions: `t != 0` (not `t_val != 0`), `u == t->next` (not `u_val == ...`).

**Example** — forward traversal of a list (`p = p->next`):
```
/*@ Inv Assert exists p_prev,
    dllseg_shape(l, 0, p_prev, p) *
    dlistrep_shape(p, p_prev)
 */
```
- `p` is the traversal cursor, `p_prev` is an `exists` variable linking the two predicates.
- `dllseg_shape(l, 0, p_prev, p)` covers traversed nodes from head `l` up to (but not including) `p`.
- `dlistrep_shape(p, p_prev)` covers remaining nodes from `p` onward.
- No PROP constraints needed — the predicates alone describe the heap ownership.

The invariant is a generalization of the RPs, not a subset. It may contain predicates not appearing verbatim in any single RP — folded shape predicates, parameterized sliding items — as long as they describe the same heap memory more compactly.

### 3. QCP Verification

3.1. **Write file**: Replace `/* INFILL */` with `/*@ Inv Assert <invariant> */`. Save to `<SKILL_DIR>/tmp/<name>_inv.c`.

3.2. **Verify via symexec** (absolute path, do NOT cd). Before running, delete old proof files to avoid stale results:
```
rm -f <SKILL_DIR>/tmp/<name>_goal.v <SKILL_DIR>/tmp/<name>_proof_auto.v <SKILL_DIR>/tmp/<name>_proof_manual.v
```
Then run symexec:
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
- `tail -3 <SKILL_DIR>/tmp/<name>_verify.log` to check "Successfully finished symbolic execution"
- `grep -c "Admitted\." <SKILL_DIR>/tmp/<name>_proof_manual.v`
  - `0` → `QCP_VERIFIED: YES` → proceed to Output
  - `> 0` → `QCP_VERIFIED: NO` → retry from Step 2
- **NEVER Read `_verify.log` in full** — use `grep`/`tail` only for this file.

3.4. **Retry (max 2 additional attempts)**: If `QCP_VERIFIED: NO`, analyze the failure and refine the invariant.

**NEVER attempt to manually prove Coq goals.** If symexec passes but proof_manual.v has `Admitted` goals, the fix is to refine the invariant (SEP/PROP), not to write Coq proofs. 

**Always consult the common fix strategies below first.** They cover the most frequent failures. Do not invent fixes before checking them.

**Diagnosis — first check the verify log for fatal errors** (`grep "fatal error"`):

| Error | Meaning | Root cause |
|------|------|------|
| `Cannot derive the precondition of Memory Read` | QCP cannot find a `data_at` for the field being read (e.g., `p->prev`, `t->next`) | **(A)** The variable is not in the invariant at all → "cannot find program variable X". **(B)** The variable is in the invariant but the node it points to is not the first argument of any SEP shape predicate → strategies have no unfold entry point. |
| `dup_data_at_error` | The same heap field has 2 owners — one from the invariant, one from strategy unfolding | C field expression or redundant PROP creates a `data_at` that duplicates one produced by strategy unfolding. |

The target is always **exactly 1 owner** for each heap field accessed in the loop body.

**Diagnosis — then check proof_manual.v** (`grep "Admitted\."`):
- `entail_wit` (1, 2, ...): invariant entry/preservation failure → SEP or PROP insufficient
- `return_wit`: loop exit to postcondition failure → invariant + exit condition must imply Ensure
- `safety_wit`: memory read failure → missing permission or unfold condition (same root causes as Memory Read above, caught at Coq level)

**Constraint**: Every element of the invariant (SEP predicates, PROP constraints) must be consistent with ALL RPs. Check each item: does it hold in RP_pre_loop, RP_iter_2, RP_iter_3? Can the SEP predicate be folded/unfolded to match the RP form? Is each PROP constraint satisfied in every RP? If an item fails in any RP, it cannot be in the invariant.

**`Memory Read` — cause and fix**:

A `Memory Read` error means the loop body dereferences a pointer (e.g., `p = p->prev`, `u = t->next`) but QCP cannot produce a `data_at` for the target field from the invariant state. With 0 owners, the read has no legal source of permission.

- **Cause 1 — Variable not in invariant**: `/*@ Inv Assert ... */` **replaces** the program state. Any variable not mentioned in the invariant is dropped → "cannot find program variable X". **Fix**: Add the variable to the invariant. For local pointers that change value, they must appear in shape predicate arguments.

- **Cause 2 — Variable in invariant but no unfold path**: The variable is mentioned (e.g., via `p != 0` or `has_permission(&p)`) but the field being read is not exposed. Strategies can only unfold from the **first argument** of shape predicates — the field's owning node must be reachable from arg[0]. **Fix**: Ensure the dereferenced node is the first argument of a `dlistrep_shape` (e.g., `dlistrep_shape(u, t)` → can unfold `u->next` at `u`) or a field expression in arg[0] position (e.g., `dlistrep_shape(p->next, p)` → can produce `p->prev` during unfolding of `p->next`).

**Field expression vs `exists` variable**:

A C field expression in a predicate argument (`p->prev`, `t->next`) creates an explicit `data_at` for that field. An `exists` variable (`p_prev`) is a pure symbol with no associated `data_at`. This difference governs both error types:

- `Memory Read` **needs** `data_at` → use field expressions for fields the loop body dereferences
- `dup_data_at_error` **fears** duplicate `data_at` → replace field expressions with `exists` variables on fields the loop body does NOT access

The same field cannot appear as a field expression in more than one predicate argument.

**`dup_data_at_error` — cause and fix**:

`dup_data_at_error` means the same heap field appears twice in the assertion state — once from the invariant as written, once from strategies unfolding a predicate. QCP's separation logic requires each field to have exactly one owner.

- **Cause 1 — C field expression in predicate argument**: `dllseg_shape(l, prev, p->prev, p)` uses `p->prev` as a C expression. QCP creates `data_at(&(p->prev), ...)` to declare ownership. When strategies later unfold `dlistrep_shape(p, p->prev)` (rule dll_nodata, 5), the unfold also produces `data_at(&(p->prev), ...)` — same address, two owners. **Fix**: Replace the field expression with an `exists` variable (see strategy 2 below).

- **Cause 2 — Redundant equality PROP**: `u == t->next` in PROP is a C expression that references `t->next`, causing QCP to create `data_at(&(t->next), ...)`. If SEP already contains `dllseg_shape(x, 0, t, u)`, the predicate's parameters `(..., t, u)` already encode that the last node in the segment is `t` and its next field equals `u`. **Fix**: Omit `u == t->next` from PROP when a shape predicate already links `u` and `t`.

- **`has_permission`**: Can trigger `dup_data_at_error` when overlapping with shape predicate fields. Avoid `has_permission` unless strictly required per 2.6.

**Common fix strategies** (in priority order):

**General rule**: Prefer adjusting PROP over SEP. Adding a non-null constraint or an equality is cheaper and less risky than restructuring shape predicates. Do not remove an existing PROP unless that specific PROP is confirmed to be the cause of the failure (e.g., a field-expression equality causing `dup_data_at`). An invariant with the right SEP but wrong PROP is one constraint away from passing; an invariant with restructured SEP but no PROP diagnosis is two problems at once.

1. **Put the dereferenced variable at arg[0] of a shape predicate**: If Memory Read fails on `p->prev` or `t->next`, the node being dereferenced must be the first argument of a `dlistrep_shape` or the first argument's field expression. Split a monolithic `dlistrep_shape(x, 0)` into `dllseg_shape(x, 0, t, u) * dlistrep_shape(u, t)` or `dlistrep_shape(p->next, p)` so that the variable's node is directly accessible for unfolding.

2. **Check for redundant `data_at`**: A field expression in SEP or PROP creates an implicit `data_at` for that field. If a SEP predicate already encodes the same field (e.g., `dllseg_shape(x, 0, t, u)` implies `t->next == u`), the field expression creates a duplicate. In symexec this may not trigger `dup_data_at_error` (the predicate is folded), but after Coq unfolding, all 4 witness types admit together — this is a **delayed `dup_data_at`**, same root cause detected at a different stage. **Fix**: remove the redundant field expression from PROP, or replace it with a non-null constraint (`t != 0`) on the owning variable. Use `exists` variables only when the field expression is in a SEP predicate argument and the field is not accessed by the loop body.

3. **Carry frame items with PROP equalities**: If `return_wit` or `entail_wit_1` admits and the invariant does not obviously lack a shape predicate, check whether the pre-loop state has stack bindings or With-clause relationships that were dropped by `Inv Assert` replacement. Use equalities in PROP to carry them: `param == param@pre` keeps a parameter's stack cell in scope; `*param == <with_var>` preserves the binding between a dereferenced value and its With-clause variable. These equalities keep existing bindings from being dropped; they do not add new `data_at` claims and thus do not cause `dup_data_at`.

4. **Widen the boundary with field expressions on both sides**: If `entail_wit_2` or `return_wit` fail, the boundary between `dllseg` and `dlistrep` may be too tight for strategies to fold/unfold. Use field expressions on BOTH sides to explicitly expose the gap node's fields — the boundary becomes self-adapting and no strategy rule is needed at all.

**Example**: A DLL backward traversal loop (`p = p->prev`). Invariant `dllseg_shape(head, 0, p_prev, p) * dlistrep_shape(p, p_prev)` with an `exists` variable `p_prev` leaves 1 Admitted — after `p` changes, `p_prev` is a fixed symbol; strategies must contract `dllseg` from the right, a rule that does not exist. Fix: `dllseg_shape(head, 0, p->prev, p) * dlistrep_shape(p->next, p)` — both arguments are C field expressions that re-evaluate automatically after `p = p->prev`. The invariant before and after are independently computed from the same expressions; QCP compares the results directly.

**Why it works**: Field expressions resolve to concrete values each time the invariant is checked. Changing `p` automatically shifts both sides of the boundary. `exists` variables are fixed symbols — they cannot adapt to variable changes without strategy rules that do not exist. Field expressions on both sides also distribute ownership across two different fields (`p->prev` and `p->next`), one per predicate, avoiding `dup_data_at`.

5. **Add non-null PROP to trigger unfolds**: If entail or safety witnesses fail after symexec passes, strategies may need explicit non-null constraints to fire unfold rules for shape predicates. Add non-null PROP for the variable whose fields the loop body or post-loop code dereferences or assigns through. The constraint `v != 0` tells strategies the node exists, allowing them to unfold shape predicates (`dlistrep_shape`, `dllseg_shape`) and produce the `data_at` needed for field access — without creating duplicate ownership.

6. **Add `has_permission`**: Re-read the 2.6 checklist.

After each fix, retry from 3.1. If still NO after 2 additional attempts, output `QCP_VERIFIED: NO` as final result.

### 4. Output

```
QCP_VERIFIED: YES  (or NO, after retries)
```c
<complete file with invariant inserted>
```

### 5. Cleanup

Delete generated files from `workspace/` and `<SKILL_DIR>/tmp/`.