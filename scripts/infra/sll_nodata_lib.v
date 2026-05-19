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
From compcert.lib Require Import Integers.
Local Open Scope Z_scope.
Local Open Scope sets.
Import ListNotations.
Local Open Scope list.
Require Import String.
Local Open Scope string.

Import naive_C_Rules.
Local Open Scope sac.

Fixpoint sll_nodata (x: addr) (l: list Z): Assertion :=
  match l with
    | nil     => [| x = NULL |] && emp
    | _ :: l0 => [| x <> NULL |] &&
                 EX y: addr,
                   &(x # "list" ->ₛ "next") # Ptr |-> y **
                   sll_nodata y l0
  end.

Fixpoint sllseg_nodata (x y: addr) (l: list Z): Assertion :=
  match l with
    | nil     => [| x = y |] && emp
    | _ :: l0 => [| x <> NULL |] &&
                 EX z: addr,
                   &(x # "list" ->ₛ "next") # Ptr |-> z **
                   sllseg_nodata z y l0
  end.

Lemma sll_nodata_zero: forall x l,
  x = NULL ->
  sll_nodata x l |-- [| l = nil |] && emp.
Admitted.

Lemma sll_nodata_not_zero: forall x l,
  x <> NULL ->
  sll_nodata x l |--
    EX y l0,
      [| l <> nil |] &&
      &(x # "list" ->ₛ "next") # Ptr |-> y **
      sll_nodata y l0.
Admitted.

Lemma sllseg_nodata_len1: forall x y,
  x <> NULL ->
  &(x # "list" ->ₛ "next") # Ptr |-> y |--
  sllseg_nodata x y [0].
Admitted.

Lemma sllseg_nodata_sllseg: forall x y z l1 l2,
  sllseg_nodata x y l1 ** sllseg_nodata y z l2 |--
  sllseg_nodata x z (l1 ++ l2).
Admitted.

Lemma sllseg_nodata_0_sll: forall x l,
  sllseg_nodata x 0 l |-- sll_nodata x l.
Admitted.
