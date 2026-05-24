#include "/home/tzh66/qcp_skill/infra/sll_nodata_def.h"

struct list * append(struct list * x, struct list * y)
/*@ Require listrep(x) * listrep(y)
    Ensure  listrep(__return)
 */;

struct list *multi_append(struct list *x, struct list *y, struct list *z)
/*@ Require listrep(x) * listrep(y) * listrep(z)
    Ensure  listrep(__return)
 */
{
    struct list *t, *u;
    if (x == 0) {
        t = append(y , z);
        return t;
    } else {
        t = x;
        u = t->next;
        /* INFILL */
        while (u) {
            if (y) {
              t -> next = y;
              t = y;
              y = y -> next;
              t -> next = u;
              t = u;
              u = u -> next;
            }
            else {
              u = append(u , z);
              t -> next = u;
              return x;   
            }
        }
        t->next = append(y,z);
        return x;
    }
}