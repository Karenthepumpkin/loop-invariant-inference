#include "/home/tzh66/qcp_skill/infra/dll_nodata_def.h"


struct list * update_all_reverse(struct list *p, int data) 
/*@ With data0
    Require data == data0 && dlistrep_shape(l, 0)
    Ensure  dlistrep_shape(__return, 0)
 */
{
  struct list *w, *t, *v;
  w = (void *)0;
  v = p;
  /* INFILL */
  while (v) {
    t = v->next;
    v->next = w;
    v->prev = t;
    if (v->data != data) {
      v -> data = data;
    }
    w = v;
    v = t;
  }
  return w;
}
