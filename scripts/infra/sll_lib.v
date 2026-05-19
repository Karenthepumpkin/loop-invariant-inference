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

Fixpoint sll (x: addr) (l: list Z): Assertion :=
  match l with
    | nil     => [| x = NULL |] && emp
    | a :: l0 => [| x <> NULL |] && 
                 EX y: addr,
                   &(x # "list" ->ₛ "data") # Int |-> a **
                   &(x # "list" ->ₛ "next") # Ptr |-> y **
                   sll y l0
  end.

Fixpoint sllseg (x y: addr) (l: list Z): Assertion :=
  match l with
    | nil     => [| x = y |] && emp
    | a :: l0 => [| x <> NULL |] && 
                 EX z: addr,
                   &(x # "list" ->ₛ "data") # Int |-> a **
                   &(x # "list" ->ₛ "next") # Ptr |-> z **
                   sllseg z y l0
  end.

Fixpoint sllbseg (x y: addr) (l: list Z): Assertion :=
  match l with
    | nil     => [| x = y |] && emp
    | a :: l0 => EX z: addr,
                   [| z <> NULL |] && 
                   x # Ptr |-> z **
                   &(z # "list" ->ₛ "data") # Int |-> a **
                   sllbseg (&(z # "list" ->ₛ "next")) y l0
  end.

Lemma sll_zero: forall x l,
  x = NULL ->
  sll x l |-- [| l = nil |] && emp.
Admitted.

Lemma sll_not_zero: forall x l,
  x <> NULL ->
  sll x l |--
    EX y a l0,
      [| l = a :: l0 |] &&
      &(x # "list" ->ₛ "data") # Int |-> a **
      &(x # "list" ->ₛ "next") # Ptr |-> y **
      sll y l0.
Admitted.

Lemma sll_not_zero': forall x l,
  x <> NULL ->
  sll x l |-- [| l <> nil |].
Admitted.

Lemma sllseg_len1: forall x a y,
  x <> NULL ->
  &(x # "list" ->ₛ "data") # Int |-> a **
  &(x # "list" ->ₛ "next") # Ptr |-> y |--
  sllseg x y [a].
Admitted.

Lemma sllseg_sllseg: forall x y z l1 l2,
  sllseg x y l1 ** sllseg y z l2 |--
  sllseg x z (l1 ++ l2).
Admitted.

Lemma sllseg_sll: forall x y l1 l2,
  sllseg x y l1 ** sll y l2 |--
  sll x (l1 ++ l2).
Admitted.

Lemma sllbseg_2_sllseg: forall x y z l,
  sllbseg x y l ** y # Ptr |-> z |--
  EX y': addr, x # Ptr |-> y' ** sllseg y' z l.
Admitted.

Lemma sllbseg_len1: forall (x y: addr) (a: Z),
  y <> 0 ->
  x # Ptr |-> y **
  &( y # "list" ->ₛ "data") # Int |-> a |--
  sllbseg x (&( y # "list" ->ₛ "next")) [a].
Admitted.

Lemma sllbseg_sllbseg: forall x y z l1 l2,
  sllbseg x y l1 ** sllbseg y z l2 |--
  sllbseg x z (l1 ++ l2).
Admitted.

Lemma sllseg_0_sll: forall x l,
  sllseg x 0 l |-- sll x l.
Admitted. 


Lemma sll_length : forall x l, 
  sll x l |-- store_align4_n (Zlength l * 2).
Admitted.
   
Lemma sll_length_max : forall x l, 
  sll x l |-- [| Zlength l * 2 <= Int.max_unsigned / 4 + 1|].
Admitted. 


