#include "/home/tzh66/qcp_skill/infra/dll_nodata_def.h"

struct list *iter(struct list *l)
/*@ With prev
    Require dlistrep_shape(l, prev)
    Ensure  dlistrep_shape(__return, prev)
 */
{
    struct list *p;
    p = l;
    /* INFILL */
    while (p) {
        p = p->next;
    }
    return l;
}