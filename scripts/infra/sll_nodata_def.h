// 单链表（无数据域）的 QCP 定义文件
// 结构体 list 仅包含 struct list *next 一个指针字段（无数据域）。
// 提供谓词: listrep(链表头), lseg(段起点, 段终点), listboxseg(box段起点, box段终点)
// 对应 Coq 库: SimpleC.EE.infra.sll_nodata_shape_lib
// 策略文件: sll_nodata.strategies

struct list {
   struct list *next;
};

/*@ Extern Coq (listrep : Z -> Assertion)
               (lseg: Z -> Z -> Assertion)
               (listboxseg: Z -> Z -> Assertion)
               (sll_tag : Z -> Prop)
 */

/*@ Import Coq Require Import SimpleC.EE.infra.sll_nodata_shape_lib */

/*@ include strategies "sll_nodata.strategies" */
