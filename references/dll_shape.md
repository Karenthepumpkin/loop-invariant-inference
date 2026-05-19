# dll_shape — Doubly-Linked List (with data)

**Header**: `dll_shape_def.h`
**Coq lib**: `dll_shape_lib`

## Struct
```c
struct list { struct list *next; struct list *prev; int data; };
```
Has `int data` field in addition to `next`/`prev` pointers.

## Predicates

### dlistrep_shape(l, p)
Doubly-linked list starting at `l` with prev pointer `p`.

Definition: `dlistrep_shape(l, p) = (l == 0 && emp) || exists v t, data_at(field_addr(l, data), v) * data_at(field_addr(l, next), struct list*, t) * data_at(field_addr(l, prev), struct list*, p) * dlistrep_shape(t, l)`

Finite expansion (2 layers, l != 0):
```
dlistrep_shape(x, 0)
  |-- exists v1 n1 v2 n2,
    data_at(field_addr(x, data), v1) *
    data_at(field_addr(x, next), struct list*, n1) *
    data_at(field_addr(x, prev), struct list*, 0) *
    data_at(field_addr(n1, data), v2) *
    data_at(field_addr(n1, next), struct list*, n2) *
    data_at(field_addr(n1, prev), struct list*, x) *
    dlistrep_shape(n2, n1)
```

Full expansion (to NULL, k nodes):
```
dlistrep_shape(x, 0)
  |-- data_at(field_addr(x, data), _) *
      data_at(field_addr(x, next), struct list*, n1) *
      data_at(field_addr(x, prev), struct list*, 0) *
      data_at(field_addr(n1, data), _) *
      data_at(field_addr(n1, next), struct list*, n2) *
      data_at(field_addr(n1, prev), struct list*, x) *
      ...
      data_at(field_addr(nk, data), _) *
      data_at(field_addr(nk, next), struct list*, 0) *
      data_at(field_addr(nk, prev), struct list*, n{k-1})
// Each node contributes 3 data_at items (data + next + prev).
// Last node nk: nk->next == 0, nk->prev == n{k-1}.
```

### dllseg_shape(x, xp, yp, y)
DLL segment from `x` to `y` (y not included). x->prev = xp.

| Param | Meaning |
|-------|---------|
| x | segment start |
| xp | start node's prev |
| yp | last node inside the segment |
| y | endpoint marker (yp->next == y, y NOT in segment) |

Definition: `dllseg_shape(x, xp, yp, y) = (x == y && xp == yp && emp) || exists v z, data_at(field_addr(x, data), v) * data_at(field_addr(x, next), struct list*, z) * data_at(field_addr(x, prev), struct list*, xp) * dllseg_shape(z, x, yp, y)`

Finite expansion (2 layers, x != y):
```
dllseg_shape(x, 0, yp, y)
  |-- exists v1 n1 v2 n2,
    data_at(field_addr(x, data), v1) *
    data_at(field_addr(x, next), struct list*, n1) *
    data_at(field_addr(x, prev), struct list*, 0) *
    data_at(field_addr(n1, data), v2) *
    data_at(field_addr(n1, next), struct list*, n2) *
    data_at(field_addr(n1, prev), struct list*, x) *
    dllseg_shape(n2, n1, yp, y)
```

When yp == n1 (single node segment):
```
dllseg_shape(n1, x, n1, y)
  |-- data_at(field_addr(n1, data), v) *
      data_at(field_addr(n1, next), struct list*, y) *
      data_at(field_addr(n1, prev), struct list*, x) *
      dllseg_shape(y, n1, n1, y)  // empty segment termination
```

**Parameter order trap**: param 3 = last node IN segment, param 4 = endpoint marker (NOT in segment). Common error: swapping yp and y.

Full expansion (x to y, with yp as last node before y):
```
dllseg_shape(x, 0, yp, y)
  |-- data_at(field_addr(x, data), _) *
      data_at(field_addr(x, next), struct list*, n1) *
      data_at(field_addr(x, prev), struct list*, 0) *
      data_at(field_addr(n1, data), _) *
      data_at(field_addr(n1, next), struct list*, n2) *
      data_at(field_addr(n1, prev), struct list*, x) *
      ...
      data_at(field_addr(yp, data), _) *
      data_at(field_addr(yp, next), struct list*, y) *
      data_at(field_addr(yp, prev), struct list*, yp_prev)
// Key: yp->next == y (end marker). y itself is NOT a data_at node.
// Each node expanded contributes 3 data_at items (data + next + prev).
```
