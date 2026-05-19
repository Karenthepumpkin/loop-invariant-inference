# sll_shape — 单链表（含数据域）

**Header**: `sll_shape_def.h`
**Coq lib**: `sll_shape_lib`

## Struct
```c
struct list { int data; struct list *next; };
```
Has `int data` field in addition to `next` pointer.

## Predicates

### listrep(l)
Singly-linked list starting at `l`.

Definition: `listrep(l) = (l == 0 && emp) || exists v t, data_at(field_addr(l, data), v) * data_at(field_addr(l, next), struct list*, t) * listrep(t)`

Finite expansion (2 layers):
```
listrep(x) |-- exists v1 node1 v2 node2,
  data_at(field_addr(x, data), v1) *
  data_at(field_addr(x, next), struct list*, node1) *
  data_at(field_addr(node1, data), v2) *
  data_at(field_addr(node1, next), struct list*, node2) *
  listrep(node2)
```

Full expansion (to NULL):
```
listrep(x) |-- data_at(field_addr(x, data), _) * data_at(field_addr(x, next), struct list*, n1) *
               data_at(field_addr(n1, data), _) * data_at(field_addr(n1, next), struct list*, n2) *
               ...
               data_at(field_addr(nk, data), _) * data_at(field_addr(nk, next), struct list*, 0)
```

### lseg(x, y)
SLL segment from `x` to `y` (y not included in segment).

Definition: `lseg(x, y) = (x == y && emp) || exists v z, data_at(field_addr(x, data), v) * data_at(field_addr(x, next), struct list*, z) * lseg(z, y)`

Finite expansion (2 layers, x != y):
```
lseg(x, y) |-- exists v1 n1 v2 n2,
  data_at(field_addr(x, data), v1) *
  data_at(field_addr(x, next), struct list*, n1) *
  data_at(field_addr(n1, data), v2) *
  data_at(field_addr(n1, next), struct list*, n2) *
  lseg(n2, y)
```

Key: y is never inside the expanded segment. Stops when nk->next == y.
