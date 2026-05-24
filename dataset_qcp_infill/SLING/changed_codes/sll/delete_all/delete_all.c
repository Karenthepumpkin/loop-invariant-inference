#include "/home/tzh66/qcp_skill/infra/sll_nodata_def.h"

struct list* malloc_SNnode(int data)
/*@ With data0 
    Require data == data0 && emp
    Ensure data_at(field_addr(__return, prev), data0) * 
           data_at(field_addr(__return, next), 0)
*/;

void free_SNnode(struct list *l)
/*@ With v n
    Require data_at(field_addr(l, prev), v) * 
            data_at(field_addr(l, next), n)
    Ensure emp
*/;

struct list * delete_all(struct list * l)
/*@ Require listrep(l)
    Ensure  emp
 */
{
    struct list *p;
    p = l;
    /* INFILL */
    while (l) {
      p = l->next;
      free_SNnode(l);
      l = p;
    } 
}