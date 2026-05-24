#include "/home/tzh66/qcp_skill/infra/sll_nodata_def.h"

struct list* malloc_SNnode(int data)
/*@ With data0 
    Require data == data0 && emp
    Ensure data_at(field_addr(__return, prev), data0) * 
           data_at(field_addr(__return, next), 0)
*/;

struct list * insert(struct list * x, int data)
/*@ With data0
    Require data == data0 && listrep(x)
    Ensure  listrep(__return)
 */
{
    struct list *p, *new_node;
    new_node = 0;
    p = x;
    /* INFILL */
    while (p) {
      if (p->prev < data) {
        new_node = malloc_SNnode(data);
        new_node ->next = p ->next;
        p ->next = new_node;
        return x;
      }
      p = p ->next;
    }
    return x;
}