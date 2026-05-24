#include "/home/tzh66/qcp_skill/infra/sll_nodata_def.h"

struct list * append(struct list * x, struct list * y)
/*@ Require listrep(x) * listrep(y)
    Ensure  listrep(__return)
 */
{
    struct list *t, *u;
    if (x == 0) {
        return y;
    } else {
        t = x;
        u = t->next;
        /* INFILL */
        while (u) {
            t = u;
            u = t->next;
        }
        t->next = y;
        return x;
    }
}