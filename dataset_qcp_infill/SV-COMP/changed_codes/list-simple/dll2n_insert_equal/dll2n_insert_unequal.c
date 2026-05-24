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

struct list * insert_unequal(struct list *l, int v) 
/*@ With v0
    Require v == v0 && dlistrep_shape(l, 0)
    Ensure  dlistrep_shape(__return, 0)
 */
{
  struct list *p;
  struct list *new_node;
  new_node = 0;
  p = l;
  /* INFILL */
  while (p) {
    if (p->data != v) {
      new_node = malloc_DLL(v);
      new_node->next = p->next;
      new_node->prev = p->prev;
      if (p -> prev) {
        p->prev->next = new_node;
      }
      if (p -> next) {
        p->next->prev = new_node;
      }
      free_DLL(p);
      p = new_node;
      new_node = 0;
    }
    p = p->next;
  }
  return l;
}
