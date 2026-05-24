#include "/home/tzh66/qcp_skill/infra/dll_nodata_def.h"

struct list *iter_back_2(struct list **head, struct list **tail)
/*@ With head_node tail_node tail_node_prev
	Require *head == head_node && *tail == tail_node && head_node != 0 && tail_node != 0 && dllseg_shape(head_node,0,tail_node_prev,tail_node) * dlistrep_shape(tail_node, tail_node_prev)
    Ensure *head == head_node && *tail == tail_node && dlistrep_shape(__return, 0)
 */
{
    struct list *p;
    p = *tail;
    if (*head == *tail) {
      return p;
    }
    else {
    /* INFILL */
    while (p != *head) {
      p = p -> prev;
    }
    return p;
  }
}