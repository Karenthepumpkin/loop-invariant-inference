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
From SimpleC.EE.infra Require Export sll_nodata_lib.

Definition listrep (x : addr) : Assertion :=
  EX l: list Z, sll_nodata x l.

Definition lseg (x y: addr): Assertion :=
  EX l: list Z, sllseg_nodata x y l.

Definition sll_tag (x : addr) : Prop := True.

Lemma listrep_zero : forall (x : Z), x = NULL -> listrep x |-- emp.
Proof.
  intros x Hx. subst x.
  unfold listrep.
  intros l H.
  destruct H as [l0 H].
  destruct l0.
  - simpl in H. destruct H as [H1 H2]. exact H2.
  - simpl in H. destruct H as [H1 H2]. exfalso. apply H1. reflexivity.
Qed.

Lemma listrep_nonzero : forall (x : Z), x <> NULL ->
  listrep x |-- EX y, &(x # "list" ->ₛ "next") # Ptr |-> y ** listrep y.
Proof.
  intros x Hneq.
  unfold listrep.
  intros u H. destruct H as [l H]. destruct l.
  - simpl in H. destruct H as [Hnull Hemp]. destruct Hnull. exfalso. apply Hneq. reflexivity.
  - simpl in H. destruct H as [Hne Hexy]. destruct Hexy as [y Hy].
    destruct Hy as [m1 [m2 [Hjoin [Hnext Hsll]]]].
    exists y, m1, m2.
    split; [exact Hjoin | split; [exact Hnext | exists l; exact Hsll]].
Qed.

Lemma listrep_fold : forall (x y : Z), x <> NULL ->

  &(x # "list" ->ₛ "next") # Ptr |-> y ** listrep y |-- listrep x.

Proof.

  intros x y Hneq. unfold listrep at 2. intros u H.

  destruct H as [m1 [m2 [Hjoin [Hnext Hlist]]]].

  destruct Hlist as [l Hsll]. exists (0::l). simpl.

  split.

  - apply Hneq.

  - exists y, m1, m2. split; [exact Hjoin | split; [exact Hnext | exact Hsll]].

Qed.


Lemma lseg_len1: forall x y,
  x <> NULL ->
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
