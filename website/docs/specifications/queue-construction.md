---
sidebar_position: 8
title: 'Queue Construction Specification'
slug: '/specifications/queue-construction'
description: 'The transparent formula behind the community-compute queue: expected-chain-value ranking, every component published, every rank re-derivable by hand.'
related:
  - label: "Why the Queue Is Built This Way"
    to: /docs/perspectives/why-the-queue
    kind: position
    note: "The philosophy behind this formula"
  - label: "Contributing Compute"
    to: /docs/getting-started/contributing-compute
    kind: guide
    note: "How to actually run queue items"
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
  - label: "Corpus Design Framework"
    to: /docs/specifications/corpus-design
    kind: spec
    note: "Small-corpus floors and noise thresholds the formula inherits"
---

# Queue Construction Specification

**Formula version: `ecv-v2` (expected chain value).** This document is
the normative definition of how
[champollion.dev/queue.json](https://champollion.dev/queue.json) is
ordered. The implementation
(`arena/scripts/generate_sweep_queue.py` in the public harness repo)
mirrors this page section by section; the queue's metadata echoes the
exact parameter values used at generation time, and **every item
carries its full formula breakdown**, so any rank can be re-derived by
hand from the published JSON alone. If this page and the queue ever
disagree, that is a bug — please report it.

## 1. The objective: a quality-weighted mesh

The mission is *every language into every language by measured
individual pair chains*. A translation between two languages with no
direct benchmark is served by **chaining** benchmarked pairs
(X→pivot→Y), so what the benchmark is worth is not its number of
corpora but the **chain capacity of its graph**.

**Definitions.** Let the *benchmark graph* have one node per language
and, for every language pair with at least one published, non-disqualified
run, an **edge strength**

```
s(e) = (best published corpus-level chrF++ on that pair) / 100   ∈ [0, 1]
```

Corpus-level chrF++ is the canonical published number (see the
[Scoring Specification](/docs/specifications/scoring)); *best* because
a chain would route through the best demonstrated system per hop.
Pairs with no published runs have s(e) = 0.

The **estimated chain strength** of a path P between two languages is

```
strength(P) = λ^(|P|−1) · Π_{e ∈ P} s(e)
```

— edge qualities compose multiplicatively, and each *junction* (each
intermediate pivot) costs an additional fidelity factor **λ < 1**.
Both choices are grounded in the pivot-translation literature:
translation through a pivot reliably loses quality relative to direct
translation, beyond what naive composition suggests (Utiyama & Isahara
2007; Wu & Wang 2007), the size of the loss depends on the pivot
chosen (Paul et al. 2009), and building *direct* non-English-centric
pairs measurably beats English-pivoting at scale — by ~10 BLEU in
M2M-100's many-to-many setting (Fan et al. 2021). λ is the formula's
standing reminder that an estimated chain is not a measurement: only a
direct run removes the discount.

The **best-chain matrix** and the **mesh objective** are then

```
Q(u,v) = max over paths P from u to v of strength(P)      (1 if u = v, 0 if disconnected)

Φ = mean over ordered language pairs (u ≠ v) of Q(u,v)    ∈ [0, 1]
```

Q is computed exactly as a shortest-path problem under the standard
log transform (edge weight −ln(λ·s(e)) ≥ 0, Dijkstra, then
Q = exp(−d)/λ). Φ is the [Latora & Marchiori
(2001)](https://arxiv.org/abs/cond-mat/0101396) *global efficiency*
construction with the 1/distance kernel replaced by multiplicative
chain fidelity — the natural kernel when edges carry per-hop quality
retention rather than unit lengths. (Queue v1 ranked by unweighted
global efficiency gain — the special case of this family where all
you know about an edge is whether it exists.)

**What Φ is not.** Φ is the queue's internal prioritization currency,
not a capability claim. Its inputs are development-set scores with all
the caveats of the [Corpus Design
Framework](/docs/specifications/corpus-design): possible training-data
contamination makes each score an upper bound, chrF++ values are not
strictly comparable across languages, and small corpora carry wide
confidence intervals. The formula only needs Φ to *order runs by
usefulness*; it is never published as a quality guarantee.

## 2. The decision problem

The queue's open items are every (corpus, model, condition)
combination that is eligible (development split, redistributable
license, not quarantined) and not yet on the leaderboard. Identical
re-runs of covered combinations are excluded — run-card fingerprints
dedupe them on publish — but new models or conditions on an
already-measured pair remain open items.

Donated compute is a budget. Choosing which open item to run next so
that the mesh improves fastest is a budgeted coverage-style
maximization, and the canonical approach is greedy selection by
**marginal value per unit cost**: for monotone submodular objectives
the greedy rule carries the classic (1 − 1/e) guarantee (Nemhauser,
Wolsey & Fisher 1978), and its benefit/cost-ratio form is the standard
algorithm under budgets (Khuller, Moss & Naor 1999). We use the
ratio rule as our ranking principle. (Honesty note: our objective has
coverage-like diminishing returns in its deterministic core, but the
stochastic prediction layer means we cite the greedy guarantee as
*motivation*, not as a theorem about this exact system.)

```
ECV(item) = ΔΦ(item) / max(est_cost_usd, COST_FLOOR)
```

Items are ranked by ECV descending. Ties break: naive before coached,
cheaper first, then item id.

## 3. The value of one run

### 3.1 Predicting the score before running

The expected score of an unrun (pair, model, condition) is a
deliberately simple, fully-inspectable sum — a two-way main-effects
prediction plus structured optimism, every term published on the item:

```
ŝ = clip( pair_prior + model_offset + condition_offset + exploration_bonus,  0, S_CAP )
```

- **`pair_prior`** — hierarchical back-off over published strengths:
  mean on this pair → mean on this target language → mean on this
  source language → global mean → `S0_FALLBACK`. The level used is
  published as `prior_basis`.
- **`model_offset`** — how this model does relative to the *other*
  models on the same pair, averaged over all pairs where a comparison
  exists. Zero for never-seen models.
- **`condition_offset`** — the observed coached-minus-naive delta on
  the same pair (falling back to the same target language), and **zero
  otherwise**: coaching gains are real where measured but are not
  assumed to transfer across languages, so on unevidenced pairs the
  baseline-first convention holds.
- **`exploration_bonus`** — optimism in the face of uncertainty, with
  the UCB1 schedule (Auer, Cesa-Bianchi & Fischer 2002):
  `κ·sqrt(2·ln(1+N)/(1+n))`, where N is the total number of published
  scored runs and n the number on this (pair, model). Never-tried
  cells get the largest bonus; well-measured cells decay toward zero.
  We borrow the schedule — the shape that makes under-explored arms
  resurface at the right rate — not the regret theorem, which assumes
  a stationary bandit this system is not.

### 3.2 The mesh gain, in closed form

A run can only improve the mesh by raising its pair's edge to
`s' = max(s(e), ŝ)`. For a single-edge change, the new best chain
between any two languages either ignores the new edge or uses it
exactly once, so the upgraded matrix — and therefore ΔΦ — has an exact
one-line form (no re-solving the whole graph):

```
Q'(u,v) = max( Q(u,v),  E(u,a)·s'·E(b,v),  E(u,b)·s'·E(a,v) )

E(x,y) = λ·Q(x,y) for x ≠ y;  E(x,x) = 1        (edge e = {a, b})

ΔΦ = mean over ordered pairs of (Q'(u,v) − Q(u,v))
```

E is "the best chain to the new edge's endpoint, paying the junction
to splice onto it"; the two terms are the two directions of crossing
the edge. This is tested in the harness suite against brute-force
recomputation of Φ.

A prediction that cannot beat the current edge strength yields
ΔΦ = 0: the formula spends donors' money confirming the unknown, not
re-measuring the demonstrated. (The exploration bonus keeps weak or
under-sampled cells from being starved forever.)

### 3.3 What counts as evidence vs. what can be queued

Two different gates, deliberately asymmetric:

- **Evidence** comes from *every* published, non-disqualified run —
  including runs on corpora that cannot be publicly queued (e.g.
  non-commercially licensed sets). A published measurement of a pair
  is knowledge regardless of whether you could re-run it.
- **Actions** (queue items) come only from openly runnable corpora:
  development split, CC-BY-family license, fetchable by anyone.

Languages reachable only through non-queueable corpora still sit in
the graph: improving edges *around* them changes their chain values,
and the formula accounts for it.

## 4. Parameters

| Parameter | Default | Meaning and justification |
|---|---|---|
| `λ` (`lambda_junction_discount`) | **0.9** | Per-junction fidelity retention of an *estimated* chain. Encodes "direct measurement beats product-equal chaining" (Utiyama & Isahara 2007; Wu & Wang 2007; Fan et al. 2021). The ~10% haircut is a calibration choice, revisited as measured chain triangles accumulate (§6). |
| `κ` (`kappa_exploration_scale`) | **0.05** | Exploration bonus scale, in strength units. 0.05 ≡ 5 chrF++ points — the noise floor below which score differences are indistinguishable on sub-100-entry corpora ([Corpus Design §6.3](/docs/specifications/corpus-design)). Optimism is capped at the resolution of the instrument. |
| `S_CAP` | **0.95** | Prediction ceiling — no estimated edge may claim near-perfect fidelity it hasn't demonstrated. |
| `S0_FALLBACK` | **0.5** | Pair prior of last resort, used only when there are no published results at all (the observed global mean — ≈ 0.54 over the first 429 runs — is preferred whenever any result exists). |
| `COST_FLOOR` | **$0.01** | Floor for the ECV denominator, so near-free runs can't claim unbounded value per dollar. |

**Versioning.** Parameter or formula changes bump `formula_version`
(metadata) and this page's version line. The queue always echoes the
exact values used under `metadata.priority_parameters`, including the
current Φ, so historical queues remain interpretable. Sensitivity
runs are one flag away: `generate_sweep_queue.py --lam 0.8 --kappa 0.1`.

## 5. Worked example (live values, 2026-06-12)

Generation against 424 scored runs, 59 measured edges, 60 languages;
**Φ = 0.272**. The top item:

```
eng>fao · claude-haiku-4.5 · naive
  edge_strength        0.0      (no published eng→fao runs)
  pair_prior           0.613    basis: target-language (Faroese runs exist via dan→fao)
  model_offset        −0.114    (haiku trails other models on shared pairs)
  condition_offset     0.0      (no coaching evidence for fao)
  exploration_bonus   +0.174    (never-run cell: κ·√(2·ln 425 / 1))
  predicted_strength   0.673
  expected_mesh_gain   0.0181   (eng→fao is a near-component join)
  est_cost_usd         0.0101
  ecv_per_usd          1.79     ← rank #1
```

Read it back: Faroese is connected to the mesh only through Danish, so
a measured eng→fao edge shortcuts a huge family of chains (the large
ΔΦ); the model is predicted mid-pack on a pair like this (prior +
offset), nobody has ever tried this cell (large bonus), and the run
costs a cent. Nothing else in the queue buys more mesh per dollar.
The same arithmetic, with every input published, produces every other
rank.

## 6. Known limitations (and what would fix them)

1. **chrF++ is not comparable across languages.** Morphology moves the
   scale; an 0.5 edge into Basque is not the same achievement as into
   Dutch. Mitigation: priorities are dominated by *structure* (s = 0 →
   s > 0 transitions) where scale effects are second-order. Fix:
   per-language score normalization, or metrics with better
   cross-lingual calibration as they become available for these
   languages.
2. **The product-λ chain model is a prior, not a measurement.** It is
   directionally supported by the pivot literature but uncalibrated
   for LLM translation. Fix (planned): the mesh now contains measured
   triangles (e.g. deu→fra direct alongside deu→eng→fra), so chained
   output can be scored directly and λ fit to data instead of chosen.
3. **Contamination and dev-set status.** Edge strengths inherit every
   caveat of public development sets — treat Φ as an upper-bound
   planning signal, never a capability claim
   ([Corpus Design](/docs/specifications/corpus-design)).
4. **Domain blindness.** An edge measured on conversational text is
   treated as one number; chains crossing domains will degrade more
   than λ predicts.
5. **Directionality.** Edges are currently undirected (X→Y evidence
   lights X↔Y). When chain composition becomes direction-sensitive in
   practice, strengths split by direction — the formula is unchanged,
   the graph just doubles.

## 7. References

- Latora, V. & Marchiori, M. (2001). *Efficient Behavior of
  Small-World Networks.* Physical Review Letters 87, 198701.
  [arXiv:cond-mat/0101396](https://arxiv.org/abs/cond-mat/0101396)
- Auer, P., Cesa-Bianchi, N. & Fischer, P. (2002). *Finite-time
  Analysis of the Multiarmed Bandit Problem.* Machine Learning 47,
  235–256. [doi:10.1023/A:1013689704352](https://link.springer.com/article/10.1023/A:1013689704352)
- Nemhauser, G., Wolsey, L. & Fisher, M. (1978). *An Analysis of
  Approximations for Maximizing Submodular Set Functions—I.*
  Mathematical Programming 14, 265–294.
  [doi:10.1007/BF01588971](https://link.springer.com/article/10.1007/BF01588971)
- Khuller, S., Moss, A. & Naor, J. (1999). *The Budgeted Maximum
  Coverage Problem.* Information Processing Letters 70(1), 39–45.
  [doi:10.1016/S0020-0190(99)00031-9](https://dl.acm.org/doi/10.1016/S0020-0190(99)00031-9)
- Utiyama, M. & Isahara, H. (2007). *A Comparison of Pivot Methods for
  Phrase-Based Statistical Machine Translation.* HLT-NAACL 2007,
  484–491. [ACL Anthology N07-1061](https://aclanthology.org/N07-1061/)
- Wu, H. & Wang, H. (2007). *Pivot Language Approach for Phrase-Based
  Statistical Machine Translation.* ACL 2007; journal version Machine
  Translation 21(3), 165–181.
  [doi:10.1007/s10590-008-9041-6](https://link.springer.com/article/10.1007/s10590-008-9041-6)
- Paul, M., Yamamoto, H., Sumita, E. & Nakamura, S. (2009). *On the
  Importance of Pivot Language Selection for Statistical Machine
  Translation.* NAACL-HLT 2009 Short Papers, 221–224.
  [ACL Anthology N09-2056](https://aclanthology.org/N09-2056/)
- Haffari, G., Roy, M. & Sarkar, A. (2009). *Active Learning for
  Statistical Phrase-Based Machine Translation.* NAACL-HLT 2009,
  415–423. [ACL Anthology N09-1047](https://aclanthology.org/N09-1047/)
- Fan, A. et al. (2021). *Beyond English-Centric Multilingual Machine
  Translation.* Journal of Machine Learning Research 22(107), 1–48.
  [arXiv:2010.11125](https://arxiv.org/abs/2010.11125)
