#include "/home/tzh66/qcp_skill/infra/dll_nodata_def.h"

struct list *iter_back_2(struct list **front, struct list **end)
/*@ With front_node end_node end_prev
	Require *front == front_node && *end == end_node && front_node != 0 && end_node != 0 && dllseg_shape(front_node,0,end_prev,end_node) * dlistrep_shape(end_node, end_prev)
    Ensure *front == front_node && *end == end_node && dlistrep_shape(__return, 0)
 */
{
    struct list *p;
    p = *end;
    if (*front == *end) {
      return p;
    }
    else {
    /* INFILL */
    while (p != *front) {
      p = p ->prev;
    }
    return p;
  }
}