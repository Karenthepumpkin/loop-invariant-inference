#include "/home/tzh66/qcp_skill/infra/dll_nodata_def.h"

struct list *iter_twice(struct list *l)
/*@ With pstPrev
    Require dlistrep_shape(l, pstPrev)
    Ensure  dlistrep_shape(__return, pstPrev)
 */
{
    struct list *p;
    p = l;
    /* INFILL */
    while (p) {
        p = p->next;
        if (p) {
          p = p ->next;
        }
      	else {
          return l;
        }
    }
    return l;
}