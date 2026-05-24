#include "/home/tzh66/qcp_skill/infra/sll_nodata_def.h"

struct list *merge(struct list *x , struct list *y)
/*@ Require listrep(x) * listrep(y)
    Ensure  listrep(__return)
 */;

struct list *multi_merge(struct list *x , struct list *y, struct list *z)
/*@ Require listrep(x) * listrep(y) * listrep(z)
    Ensure  listrep(__return)
 */
{
    struct list *t,*u;
    if (x == 0) {
      t = merge(y,z);
      return t; 
    }
    else {
      t = x;
      u = t->next;
      /* INFILL */
      while (u) {
        if (y) {
          t -> next = y;
          t = y;
          y = y -> next;
        }
        else {
          u = merge(u , z);
          t -> next = u;
          return x;   
        }
        if (z) {
          t -> next = z;
          t = z;
          z = z -> next;
        }
        else {
          u = merge(u , y);
          t -> next = u;
          return x;
        }
        t -> next = u;
        t = u;
        u = u -> next;
      }
  }
  t->next = merge(y,z);
  return x;
}