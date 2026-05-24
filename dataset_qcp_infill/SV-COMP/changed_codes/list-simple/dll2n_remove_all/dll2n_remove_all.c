#include "/home/tzh66/qcp_skill/infra/dll_nodata_def.h"


struct list* malloc_DLL(int v)
/*@ With v0 
    Require v == v0 && emp
    Ensure data_at(field_addr(__return, data), v0) * 
           data_at(field_addr(__return, next), 0) *
           data_at(field_addr(__return, prev), 0) 
*/;

void free_DLL(struct list *l)
/*@ With v n p
    Require data_at(field_addr(l, data), v) * 
            data_at(field_addr(l, next), n) *
            data_at(field_addr(l, prev), p)
    Ensure emp
*/;


void remove_all(struct list *l) 
/*@ Require dlistrep_shape(l, 0)
    Ensure  emp
 */
{
  struct list *p;
  p = l;
  /* INFILL */
  while (l) {
    p = l->next;
    free_DLL(l);
    if (p) {
      p->prev = 0;
    }
    l = p;
  }
}
