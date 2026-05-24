#include "/home/tzh66/qcp_skill/infra/sll_nodata_def.h"

struct list *iter_twice(struct list *l)
/*@ Require listrep(l)
    Ensure  listrep(__return)
 */
{
    struct list *p;
    p = l;
    /* INFILL */
    while (p) {
        p = p->next;
        if (p) {
          p = p -> next;
        }
    }
    return l;
}