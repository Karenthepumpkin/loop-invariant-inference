#include "/home/tzh66/qcp_skill/infra/sll_nodata_def.h"

struct list *reverse(struct list *p)
/*@ Require listrep(p)
    Ensure  listrep(__return)
 */
{
    struct list *w, *t, *v;
    w = 0;
    v = p;
    /* INFILL */
    while (v) {
        t = v->next;
        v->next = w;
        w = v;
        v = t;
    }
    return w;
}