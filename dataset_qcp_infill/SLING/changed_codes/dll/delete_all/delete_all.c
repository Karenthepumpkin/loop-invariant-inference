#include "/home/tzh66/qcp_skill/infra/dll_nodata_def.h"

void free_DLNode(struct list *l)
/*@ With v n p
    Require data_at(field_addr(l, prev), v) * 
            data_at(field_addr(l, next), n) *
            data_at(field_addr(l, prev), p)
    Ensure emp
*/;

void deleta_all(struct list * l)
/*@ Require dlistrep_shape(l, 0)
    Ensure  emp
 */
{
    struct list *p;
    p = l;
    /* INFILL */
    while (l) {
      p = l->next;
      free_DLNode(l);
      if (p) {
        p->prev = 0;
      }
      l = p;
    }
}