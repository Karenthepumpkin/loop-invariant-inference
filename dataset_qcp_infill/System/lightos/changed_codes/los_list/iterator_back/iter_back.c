#include "/home/tzh66/qcp_skill/infra/dll_nodata_def.h"

struct list *iter_back(struct list *l, struct list *head)
/*@ With l_prev
	  Require dllseg_shape(head, 0, l_prev, l) * dlistrep_shape(l, l_prev)
    Ensure  dlistrep_shape(__return, 0)
 */
{
    struct list *p;
    if (l == 0) {
      return head;
    }
  	else {
    	p = l;
     /* INFILL */
    	while (p != head) {
      	  p = p ->prev; 
      }
    }
    return p;
}