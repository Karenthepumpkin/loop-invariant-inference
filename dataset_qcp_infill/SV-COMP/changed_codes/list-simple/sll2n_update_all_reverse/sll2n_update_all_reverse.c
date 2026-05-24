#include "/home/tzh66/qcp_skill/infra/sll_nodata_def.h"

struct list * update_all_reverse(struct list *p, int data) 
/*@ With data0
    Require data == data0 && listrep(l)
    Ensure  listrep(__return)
 */
{
  struct list *w, *t, *v;
  w = (void *)0;
  v = p;
  /* INFILL */
  while (v) {
    t = v->next;
    v->next = w;
    if (v->prev != data) {
      v ->prev = data;
    }
    w = v;
    v = t;
  }
  return w;
}
