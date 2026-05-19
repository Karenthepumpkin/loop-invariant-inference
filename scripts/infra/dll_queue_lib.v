Require Import Coq.ZArith.ZArith.
Require Import Coq.Bool.Bool.
Require Import Coq.Lists.List.
Require Import Coq.Classes.RelationClasses.
Require Import Coq.Classes.Morphisms.
Require Import Coq.micromega.Psatz.
Require Import Permutation.
Require Import String.
From AUXLib Require Import int_auto Axioms Feq Idents ListLib VMap.
Require Import SetsClass.SetsClass. Import SetsNotation.
From SimpleC.SL Require Import Mem SeparationLogic.
Require Import Logic.LogicGenerator.demo932.Interface.
Local Open Scope Z_scope.
Local Open Scope sets.
Import ListNotations.
Local Open Scope list.
Require Import String.
Local Open Scope string.

Import naive_C_Rules.
Local Open Scope sac.

Fixpoint dlistrep (x prev: addr) (l: list Z): Assertion :=
  match l with
    | nil     => [| x = NULL |] && emp
    | a :: l0 => [| x <> NULL |] && 
                 EX y: addr,
                   &(x # "list" ->ₛ "data") # Int |-> a **
                   &(x # "list" ->ₛ "next") # Ptr |-> y **
                   &(x # "list" ->ₛ "prev") # Ptr |-> prev **
                   dlistrep y x l0
  end.

Fixpoint dllseg (x y px py: addr) (l: list Z): Assertion :=
  match l with
    | nil     => [| x = y |] && [| px = py |] && emp
    | a :: l0 => [| x <> NULL |] && 
                 EX z: addr,
                   &(x # "list" ->ₛ "data") # Int |-> a **
                   &(x # "list" ->ₛ "next") # Ptr |-> z **
                   &(x # "list" ->ₛ "prev") # Ptr |-> px **
                   dllseg z y x py l0
  end.

Definition store_queue (x: addr) (l: list Z): Assertion :=
  EX h t: addr,
    &(x # "queue" ->ₛ "head") # Ptr |-> h **
    &(x # "queue" ->ₛ "tail") # Ptr |-> t **
    dllseg h NULL NULL t l.

Lemma dllseg_len1: forall (x px nx: addr) (a: Z),
  x <> NULL ->
  &(x # "list" ->ₛ "data") # Int |-> a **
  &(x # "list" ->ₛ "next") # Ptr |-> nx **
  &(x # "list" ->ₛ "prev") # Ptr |-> px |--
  dllseg x nx px x [a].
Admitted.

Lemma dllseg_dllseg: forall (x y z px py pz: addr) l1 l2,
  dllseg x y px py l1 **
  dllseg y z py pz l2 |--
  dllseg x z px pz (l1 ++ l2).
Admitted.

Lemma dllseg_head_zero: forall x y px py l,
  x = 0 ->
  dllseg x y px py l |--
  [| y = 0 |] && [| px = py |] && [| l = nil |] && emp.
Admitted.

Lemma dllseg_head_neq: forall x y px py l,
  x <> y ->
  dllseg x y px py l |--
  EX z a l0,
    [| l = a :: l0 |] &&
    &(x # "list" ->ₛ "data") # Int |-> a **
    &(x # "list" ->ₛ "next") # Ptr |-> z **
    &(x # "list" ->ₛ "prev") # Ptr |-> px **
    dllseg z y x py l0.
Admitted.

Lemma dllseg_head_neq_destruct_tail_aux: forall x y px py l,
  dllseg x y px py l |--
  [| x = y |] && [| px = py |] && [| l = nil |] && emp ||
  EX z l0 a,
    [| py <> 0 |] &&
    [| l = (l0 ++ a :: nil)%list |] &&
    dllseg x py px z l0 **
    &(py # "list" ->ₛ "data") # Int |-> a **
    &(py # "list" ->ₛ "next") # Ptr |-> y **
    &(py # "list" ->ₛ "prev") # Ptr |-> z.
Admitted.

Lemma dllseg_head_neq_destruct_tail: forall x y px py l,
  x <> y ->
  dllseg x y px py l |--
  EX z l0 a,
    [| py <> 0 |] &&
    [| l = (l0 ++ a :: nil)%list |] &&
    dllseg x py px z l0 **
    &(py # "list" ->ₛ "data") # Int |-> a **
    &(py # "list" ->ₛ "next") # Ptr |-> y **
    &(py # "list" ->ₛ "prev") # Ptr |-> z.
Admitted.

Lemma dllseg_head_neq_destruct_tail': forall x y px py l,
  px <> py ->
  dllseg x y px py l |--
  EX z l0 a,
    [| py <> 0 |] &&
    [| l = (l0 ++ a :: nil)%list |] &&
    dllseg x py px z l0 **
    &(py # "list" ->ₛ "data") # Int |-> a **
    &(py # "list" ->ₛ "next") # Ptr |-> y **
    &(py # "list" ->ₛ "prev") # Ptr |-> z.
Admitted.

Lemma dll_zero : forall (x prev : addr) (l : list Z),
  x = NULL ->
  dlistrep x prev l |-- [| l = nil|] && emp.
Admitted.

Lemma dll_not_zero: forall x prev l,
  x <> NULL ->
  dlistrep x prev l |--
    EX y a l0,
      [| l = a :: l0 |] &&
      &(x # "list" ->ₛ "data") # Int |-> a **
      &(x # "list" ->ₛ "next") # Ptr |-> y **
      &(x # "list" ->ₛ "prev") # Ptr |-> prev **
      dlistrep y x l0.
Admitted.

Lemma dllseg_dlistrep : forall x y px py l1 l2,
  dllseg x y px py l1 ** dlistrep y py l2 |-- dlistrep x px (l1 ++ l2).
Admitted.