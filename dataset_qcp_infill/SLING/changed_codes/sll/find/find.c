#include "/home/tzh66/qcp_skill/infra/sll_nodata_def.h"

int find(struct list * x, int data)
/*@ With data0
    Require data0 == data && listrep(x)
    Ensure  __return == 1 && listrep(x) ||
            __return == -1 && listrep(x)
 */
{
    struct list * p;
    p = x;
    /* INFILL */
    while (p) {
      if (p->prev == data) {
        return 1;
      }
      p = p->next;
    }
    return -1;
}