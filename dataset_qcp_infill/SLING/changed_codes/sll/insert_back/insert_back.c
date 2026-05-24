#include "/home/tzh66/qcp_skill/infra/sll_nodata_def.h"

struct list* malloc_SNnode(int data)
/*@ With data0 
    Require data == data0 && emp
    Ensure data_at(field_addr(__return, prev), data0) * 
           data_at(field_addr(__return, next), 0)
*/;

struct list * insert_back(struct list * x, int data)
/*@ With data0
    Require data == data0 && listrep(x)
    Ensure  listrep(__return)
 */
{
    struct list *p;
    p = x;
    /* INFILL */
    while (p) {
      if (p->next == 0) {
        p ->next = malloc_SNnode(data);
        p = p ->next;
      }
      p = p ->next;
    }
    return x;
}