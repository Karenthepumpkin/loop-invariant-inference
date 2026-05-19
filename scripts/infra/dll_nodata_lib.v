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

Fixpoint dlistrep_nodata (x prev: addr) (l: list Z): Assertion :=
  match l with
    | nil     => [| x = NULL |] && emp
    | _ :: l0 => [| x <> NULL |] &&
                 EX y: addr,
                   &(x # "list" ->ₛ "next") # Ptr |-> y **
                   &(x # "list" ->ₛ "prev") # Ptr |-> prev **
                   dlistrep_nodata y x l0
  end.

Fixpoint dllseg_nodata (x y px py: addr) (l: list Z): Assertion :=
  match l with
    | nil     => [| x = y |] && [| px = py |] && emp
    | _ :: l0 => [| x <> NULL |] &&
                 EX z: addr,
                   &(x # "list" ->ₛ "next") # Ptr |-> z **
                   &(x # "list" ->ₛ "prev") # Ptr |-> px **
                   dllseg_nodata z y x py l0
  end.

Lemma dlistrep_nodata_zero : forall x prev l,
  x = NULL ->
  dlistrep_nodata x prev l |-- [| l = nil |] && emp.
Admitted.

Lemma dlistrep_nodata_not_zero : forall x prev l,
  x <> NULL ->
  dlistrep_nodata x prev l |--
    EX y l0,
      [| l <> nil |] &&
      &(x # "list" ->ₛ "next") # Ptr |-> y **
      &(x # "list" ->ₛ "prev") # Ptr |-> prev **
      dlistrep_nodata y x l0.
Admitted.

Lemma dllseg_nodata_len1: forall (x px nx: addr),
  x <> NULL ->
  &(x # "list" ->ₛ "next") # Ptr |-> nx **
  &(x # "list" ->ₛ "prev") # Ptr |-> px |--
  dllseg_nodata x nx px x [0].
Admitted.

Lemma dllseg_nodata_dllseg: forall (x y z px py pz: addr) l1 l2,
  dllseg_nodata x y px py l1 **
  dllseg_nodata y z py pz l2 |--
  dllseg_nodata x z px pz (l1 ++ l2).
Admitted.

Lemma dllseg_nodata_head_zero: forall x y px py l,
  x = 0 ->
  dllseg_nodata x y px py l |--
  [| y = 0 |] && [| px = py |] && [| l = nil |] && emp.
Admitted.

Lemma dllseg_nodata_head_neq: forall x y px py l,
  x <> y ->
  dllseg_nodata x y px py l |--
  EX z l0,
    [| l <> nil |] &&
    &(x # "list" ->ₛ "next") # Ptr |-> z **
    &(x # "list" ->ₛ "prev") # Ptr |-> px **
    dllseg_nodata z y x py l0.
Admitted.
