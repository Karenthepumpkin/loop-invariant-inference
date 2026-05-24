#include "/home/tzh66/qcp_skill/infra/dll_nodata_def.h"

struct list *merge(struct list * x, struct list * y)
/*@ Require dlistrep_shape(x, 0) * dlistrep_shape(y, 0)
    Ensure  dlistrep_shape(__return, 0)
 */
{
    struct list *z, *t;
    if (x == 0) {
      return y; 
    }
    else {
      z = x;
      t = y;
      /* INFILL */
      while (y) {
        t = y -> next;
        y -> next = x -> next;
        y -> prev = x;
        x -> next = y;
        if (y -> next == 0) {
          y -> next = t;
          return z;
        }
        else {
          x = y -> next;
          x -> prev = y;
          y = t;
          if (t) {
          	t -> prev = 0;
          }
        }
      }
    }
    
    return z;
}