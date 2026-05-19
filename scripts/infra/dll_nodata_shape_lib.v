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
From SimpleC.EE.infra Require Export dll_nodata_lib.

Definition dlistrep_shape (x prev: addr) : Assertion :=
  EX l: list Z, dlistrep_nodata x prev l.

Definition dllseg_shape (x px py y: addr) : Assertion :=
  EX l: list Z, dllseg_nodata x y px py l.

Definition dll_tag (x : Z) : Prop := True.

Lemma dlistrep_zero : forall (x prev: Z), x = NULL -> dlistrep_shape x prev |-- emp.
Proof.
  intros x prev Hx. subst x.
  unfold dlistrep_shape.
  intros l H.
  destruct H as [l0 H].
  destruct l0.
  - simpl in H. destruct H as [H1 H2]. exact H2.
  - simpl in H. destruct H as [H1 H2]. exfalso. apply H1. reflexivity.
Qed.

Lemma dlistrep_not_zero : forall (x prev: Z), x <> NULL ->
  dlistrep_shape x prev |-- EX y,
    &(x # "list" ->ₛ "next") # Ptr |-> y **
    &(x # "list" ->ₛ "prev") # Ptr |-> prev **
    dlistrep_shape y x.
Proof.
  intros x prev Hneq. unfold dlistrep_shape.
  intros u H. destruct H as [l H]. destruct l.
  - simpl in H. destruct H as [Hnull Hemp]. destruct Hnull. exfalso. apply Hneq. reflexivity.
  - simpl in H. destruct H as [Hne Hexy]. destruct Hexy as [y Hy].
    exists y.
    destruct Hy as [m1 [m2 [Hjoin12 [Hnext Hrest]]]].
    destruct Hnext as [m11 [m12 [Hjoin1 [Hnext2 Hprev]]]].
    exists m1, m2. split. exact Hjoin12. split.
    + exists m11, m12. split; [exact Hjoin1 | split; [exact Hnext2 | exact Hprev]].
    + exists l. exact Hrest.
Qed.

Lemma dllseg_dlistrep_shape : forall x y px py,
  dllseg_shape x px py y ** dlistrep_shape y py |-- dlistrep_shape x px.
Admitted.
