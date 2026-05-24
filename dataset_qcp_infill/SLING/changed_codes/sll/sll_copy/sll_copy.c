#include "/home/tzh66/qcp_skill/infra/sll_nodata_def.h"

struct list* malloc_SNnode(int data)
/*@ With data0 
    Require data == data0 && emp
    Ensure data_at(field_addr(__return, prev), data0) * 
           data_at(field_addr(__return, next), 0)
*/;

struct list * sll_copy(struct list * x)
/*@ Require listrep(x)
    Ensure  listrep(__return) * listrep(x)
 */
{
    struct list *y, *p, *t;
    y = malloc_SNnode(0);
    t = y;
    p = x;
    /* INFILL */
    while (p) {
      t ->prev = p ->prev;
      t ->next = malloc_SNnode(0);
      p = p ->next;
      t = t ->next;
    }
    return y;
}