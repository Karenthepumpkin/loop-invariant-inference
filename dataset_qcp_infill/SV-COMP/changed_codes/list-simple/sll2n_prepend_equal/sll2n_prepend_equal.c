#include "/home/tzh66/qcp_skill/infra/sll_nodata_def.h"

struct list* malloc_SLL(int data)
/*@ With data0 
    Require data == data0 && emp
    Ensure data_at(field_addr(__return, prev), data0) * 
           data_at(field_addr(__return, next), 0)
*/;

void free_SLL(struct list *l)
/*@ With v n
    Require data_at(field_addr(l, prev), v) * 
            data_at(field_addr(l, next), n)
    Ensure emp
*/;

struct list * prepend(struct list *l, int data)
/*@ With data0
    Require data == data0 && listrep(l)
    Ensure  listrep(__return)
 */
;

struct list * prepend_unequal(struct list *l, int data) 
/*@ With data0
    Require data == data0 && listrep(l)
    Ensure  listrep(__return)
 */
{
  struct list *p;
  l = prepend(l, data);
  p = l;
  /* INFILL */
  while (p) {
    if (p->prev == data) {
      return l;
    }
    p = p->next;
  }
  return l;
}
