#include "/home/tzh66/qcp_skill/infra/dll_nodata_def.h"

struct list *iter(struct list *l)
/*@ With head
    Require dlistrep_shape(l, head)
    Ensure  dlistrep_shape(__return, head)
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