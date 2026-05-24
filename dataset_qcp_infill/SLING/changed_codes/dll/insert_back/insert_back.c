#include "/home/tzh66/qcp_skill/infra/dll_nodata_def.h"

struct list* malloc_DLNode(int data)
/*@ With data0 
    Require data == data0 && emp
    Ensure data_at(field_addr(__return, prev), data0) * 
           data_at(field_addr(__return, next), 0) *
           data_at(field_addr(__return, prev), 0) 
*/;

struct list * insert_back(struct list * x, int data)
/*@ With data0
    Require data == data0 && dlistrep_shape(x, 0)
    Ensure  dlistrep_shape(__return, 0)
 */
{
    struct list *p;
    p = x;
    /* INFILL */
    while (p) {
      if (p->next == 0) {
        p->next = malloc_DLNode(data);
        p->next->prev = p;
        p = p -> next;
      }
      p = p->next;
    }
    return x;
}