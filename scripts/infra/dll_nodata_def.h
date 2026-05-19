// 双链表（无数据域）的 QCP 定义文件
// 结构体 list 仅包含 struct list *next 和 struct list *prev 两个指针字段（无数据域）。
// 提供谓词: dlistrep_shape(链表头, 前驱), dllseg_shape(段起点, 起点prev, 段内最后节点, 终点)
// 对应 Coq 库: SimpleC.EE.infra.dll_nodata_shape_lib
// 策略文件: dll_nodata.strategies
// 注意: dllseg_shape 第3参数是段内最后节点，第4参数是终点标记，详见 doc/dllseg_semantics.md

struct list {
   struct list *next;
   struct list *prev;
};

/*@ Extern Coq (dlistrep_shape : Z -> Z -> Assertion)
               (dllseg_shape: Z -> Z -> Z -> Z -> Assertion)
               (dll_tag : Z -> Z -> Prop)
 */

/*@ Import Coq Require Import SimpleC.EE.infra.dll_nodata_shape_lib */

/*@ include strategies "dll_nodata.strategies" */
