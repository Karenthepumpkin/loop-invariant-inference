# sll_nodata — 单链表（无数据域）

**Header**: `sll_nodata_def.h`
**Coq lib**: `sll_nodata_shape_lib`

## Struct
```c
struct list { struct list *next; };
```
Single pointer field: `next`. No data field.

## Predicates

### listrep(l)
Singly-linked list starting at `l`.

Definition: `listrep(l) = (l == 0 && emp) || exists t, data_at(field_addr(l, next), struct list*, t) * listrep(t)`

Finite expansion (2 layers):
```
listrep(x) |-- exists node1 node2,
  data_at(field_addr(x, next), struct list*, node1) *
  data_at(field_addr(node1, next), struct list*, node2) *
  listrep(node2)
```

Full expansion (to NULL):
```
listrep(x) |-- data_at(field_addr(x, next), struct list*, n1) *
               data_at(field_addr(n1, next), struct list*, n2) *
               ...
               data_at(field_addr(nk, next), struct list*, 0)
```

### lseg(x, y)
SLL segment from `x` to `y` (y not included in segment).

Definition: `lseg(x, y) = (x == y && emp) || exists z, data_at(field_addr(x, next), struct list*, z) * lseg(z, y)`

Finite expansion (2 layers, x != y):
```
lseg(x, y) |-- exists n1 n2,
  data_at(field_addr(x, next), struct list*, n1) *
  data_at(field_addr(n1, next), struct list*, n2) *
  lseg(n2, y)
```

Key: y is never inside the expanded segment. Stops when nk->next == y.
