#include "/home/tzh66/qcp_skill/infra/dll_nodata_def.h"

struct list *iter_back(struct list *l, struct list *front)
/*@ With l_head
	  Require dllseg_shape(front, 0, l_head, l) * dlistrep_shape(l, l_head)
    Ensure  dlistrep_shape(__return, 0)
 */
{
    struct list *p;
    if (l == 0) {
      return front;
    }
  	else {
    	p = l;
     /* INFILL */
    	while (p != front) {
      	  p = p ->prev; 
      }
    }
    return p;
}