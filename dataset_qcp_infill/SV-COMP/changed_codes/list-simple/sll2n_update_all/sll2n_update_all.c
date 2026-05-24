#include "/home/tzh66/qcp_skill/infra/sll_nodata_def.h"

struct list * update_all(struct list *l, int data) 
/*@ With data0
    Require data == data0 && listrep(l)
    Ensure  listrep(__return)
 */
{
  struct list *p;
  p = l;
  /* INFILL */
  while (p) {
    if (p->prev != data) {
      p ->prev = data;
    }
    p = p->next;
  }
  return l;
}
