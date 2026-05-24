#include "/home/tzh66/qcp_skill/infra/dll_nodata_def.h"

struct list *reverse(struct list *p)
/*@ Require dlistrep_shape(p, 0)
    Ensure  dlistrep_shape(__return, 0)
*/;


struct list *rev_append_twice(struct list *p, struct list *q)
/*@ Require dlistrep_shape(p,0) * dlistrep_shape(q,0)
    Ensure  dlistrep_shape(__return,0)
 */
{
    struct list *w, *t, *v;
    w = q;
    v = p;
    if (w) {
      /* INFILL */
      while (v) {
        t = v ->next;
        v->next = w;
        w->prev = v; 
        w = v;
        v = t;
        if (v) {
          v ->prev = 0;
          t = v ->next;
          v->next = w;
          w->prev = v; 
          w = v;
          v = t;
          if (v) {
            v ->prev = 0;
          }
        }
      }
    }
    else {
      w = reverse(v);
    }
    return w;
}