#include "/home/tzh66/qcp_skill/infra/sll_nodata_def.h"

struct list *rev_append_twice(struct list *p, struct list *q)
/*@ Require p != q && listrep(p) * listrep(q)
    Ensure  listrep(__return)
 */
{
    struct list *w, *t, *v;
    w = q;
    v = p;
    /* INFILL */
    while (v) {
      t = v->next;
      v->next = w;
      w = v;
      v = t;
      if (v) {
        t = v->next;
        v->next = w;
        w = v;
        v = t;
      }
    }
    return w;
}