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
From SimpleC.EE.infra Require Export sll_lib.

Definition listrep (x : addr) : Assertion :=
  EX l: list Z, sll x l.

Definition lseg (x y: addr): Assertion :=
  EX l: list Z, sllseg x y l.

Definition listboxseg (x y: addr): Assertion :=
  EX l: list Z, sllbseg x y l.

Definition sll_tag (x : addr) : Prop := True.

Lemma listrep_zero : forall (x : Z), x = NULL -> listrep x |-- emp.
Admitted.

Lemma listrep_nonzero : forall (x : Z), x <> NULL -> listrep x |-- EX y a, &(x # "list" ->ₛ "data") # Int |-> a ** &(x # "list" ->ₛ "next") # Ptr |-> y ** listrep y.
Admitted.

Lemma lseg_len1: forall x a y,
  x <> NULL ->
  &(x # "list" ->ₛ "data") # Int |-> a **
  &(x # "list" ->ₛ "next") # Ptr |-> y |--
  lseg x y.
Admitted.

Lemma lseg_lseg: forall x y z,
  lseg x y ** lseg y z |--
  lseg x z.
Admitted.

Lemma lseg_listrep : forall (x y : addr), 
  lseg x y ** listrep y |-- listrep x.
Admitted.