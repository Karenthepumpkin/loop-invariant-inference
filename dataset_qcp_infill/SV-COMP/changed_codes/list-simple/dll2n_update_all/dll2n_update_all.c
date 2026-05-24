#include "/home/tzh66/qcp_skill/infra/dll_nodata_def.h"


struct list * update_all(struct list *l, int data) 
/*@ With data0
    Require data == data0 && dlistrep_shape(l, 0)
    Ensure  dlistrep_shape(__return, 0)
 */
{
  struct list *p;
  p = l;
  /* INFILL */
  while (p) {
    if (p->data != data) {
      p -> data = data;
    }
    p = p->next;
  }
  return l;
}
