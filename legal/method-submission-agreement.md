# Champollion Method Submission Agreement

> **Purpose.** This document defines the terms under which a developer submits a translation method for prize evaluation against a Champollion-built evaluation corpus with a cryptographically secured holdout. It is the legal position document that governs the relationship between the method developer, the Champollion platform, and the language community's governance organization.
>
> **Status:** DRAFT. No governance organization partner has been identified yet. This document establishes the intended terms so that they are transparent from the outset — before any developer invests effort building a method. When a governance body is identified and formalized, these terms will be reviewed by that body and revised as needed. Nothing in this document is binding until both a governance organization and a developer execute a signed instance.
>
> **This is not legal advice.** This document articulates a clear legal position grounded in Indigenous data sovereignty principles. It is not a substitute for legal counsel. All parties should seek independent legal review before execution.
>
> **Companion documents:**
> - [Ownership Transfer](/docs/sovereignty/ownership-transfer) — the five-stage transfer pipeline
> - [Economic Model](/docs/sovereignty/economic-model) — revenue flow and the 90/10 split
> - [Benchmark Specification](/docs/specifications/benchmark) §8 — sovereignty mechanisms and sandboxed execution
> - [Prize Specification](/docs/specifications/prizes) — threshold conditions and claim process
> - [Corpus Partnership Strategy](/docs/specifications/corpus-partnership) — how evaluation corpora are established
> - [Governance & OCAP Working Document](/docs/governance-and-ocap) — internal governance design (not public-facing)
>
> Last updated: 2026-06-09

---

## Preamble

This agreement exists because the Champollion evaluation model inverts the conventional relationship between researchers and language communities. In the conventional model, researchers extract linguistic data, build tools, publish papers, and retain all intellectual property. The community — whose linguistic knowledge made the tool possible — receives nothing of lasting value.

Champollion's model is different. The evaluation corpus is community-curated. The secret test set is community-held. The evaluation sandbox is community-controlled. And when a method proves itself capable — when it clears the acceptance threshold on the community's data and passes the community's human validation — the method itself becomes community property.

This is not a punitive arrangement. It is a structural implementation of the [OCAP® principles](https://fnigc.ca/ocap-training/) (Ownership, Control, Access, Possession) developed by the First Nations Information Governance Centre, and the [CARE Principles for Indigenous Data Governance](https://www.gida-global.org/care) (Collective Benefit, Authority to Control, Responsibility, Ethics) developed by the Global Indigenous Data Alliance. Every section of this agreement maps to a specific principle. The rationale is documented alongside each term so that any reader — developer, community member, funder, or legal reviewer — understands not just what each term requires, but why it exists.

The deal is simple: **you want the prize → you transfer the complete, self-hostable method to the language trust. Full OCAP.**

The developer keeps their ideas. They keep their academic freedom. They keep their attribution. What transfers is the artifact — the specific, runnable system that was trained on, tested against, and validated by the community's linguistic knowledge. The community gets a revenue-generating asset they can inspect, modify, deploy, or shelve. The developer gets a prize, a publication, and the credit for building something that actually works.

---

## §1 Definitions

**1.1 Method.** The complete, self-contained system submitted for evaluation. This includes all source code, trained model weights, configuration files, coaching data, prompts, dictionaries, finite-state transducer (FST) binaries, pre-processing and post-processing scripts, dependency manifests, installation instructions, and any other component required to produce translations from source text to target text. A Method is not a model — it is the full recipe. Two teams using the same underlying model with different methods produce different results. See [Benchmark Specification §1.2](/docs/specifications/benchmark).

**1.2 Governance Organization.** The language trust, tribal council, language commission, Métis organization, or other community body with legitimate relational authority over the Prize Corpus and the language it represents. The Governance Organization is identified and authorized by the language community — not appointed by Champollion. When no Governance Organization has been identified, this agreement cannot be executed. See [Governance & OCAP Working Document](/docs/governance-and-ocap) for the current status and candidate models.

**1.3 Prize Corpus.** The Champollion-built evaluation corpus associated with the prize, consisting of a public development segment (used freely by developers), a sealed gold-standard test segment (cryptographically secured, held by the Governance Organization), and an inactive held-out segment (never used until activated). The Prize Corpus is community-curated, human-authored, and domain-diverse. It is not synthetic data. See [Benchmark Specification §2](/docs/specifications/benchmark) for the corpus schema and [Corpus Partnership Strategy](/docs/specifications/corpus-partnership) for the construction process.

**1.4 Acceptance Threshold.** The score, metric criteria, and human validation requirements that together define when a Method has demonstrated sufficient capability to trigger transfer. The Acceptance Threshold is defined per prize pool — for example, the Founder's Prize requires composite ≥ 0.80, FST acceptance ≥ 0.99, chrF++ ≥ 55.0, and ≥ 70% "acceptable" or "excellent" ratings from bilingual speakers. See [Prize Specification §2](/docs/specifications/prizes) for active thresholds. The Governance Organization may adjust thresholds for future prize pools. The Acceptance Threshold is not met by automated metrics alone — community validation is a mandatory component.

**1.5 Self-Hostable Method.** A Method that runs on community-controlled infrastructure without any runtime dependency on external services, license servers, proprietary APIs, or network connectivity. Self-hostability means the Governance Organization can install, execute, inspect, modify, and redeploy the Method using only the submitted artifacts and commodity hardware. If the community cannot run it independently, it is not Self-Hostable. This definition is grounded in OCAP® Possession — the community must physically hold every byte needed to operate the Method.

One refinement, defined precisely in §2.6: a Method whose *only* runtime network dependency is substitutable LLM inference (Dependency Class A1) is Self-Hostable **if and only if** the model endpoint is pure configuration — the Method must run end-to-end against a community-hosted open-weight model, with no dependency on any particular provider or any provider-side state. The community must possess the complete recipe; the inference engine must be replaceable at will. A Method that only functions against one proprietary provider is not Self-Hostable.

**1.5a Dependency Class.** The classification (S, O, A1, A2, or X) derived from a Method's declared dependency manifest, as defined in the [Method Interface specification](/docs/specifications/methods#method-validity-and-dependency-classes). A Method's class is the most restrictive class among its dependencies. See §2.6.

**1.6 Sandbox.** The air-gapped evaluation environment operated by or on behalf of the Governance Organization, where submitted Methods are executed against the sealed gold-standard test segment. The Sandbox has no outbound network access. Methods run inside the Sandbox; only aggregate scores are returned to the developer. The developer never sees the source sentences, the reference translations, or any content from the sealed segments. See [Benchmark Specification §8.2](/docs/specifications/benchmark) for the technical design.

**1.7 Stewards.** The individuals chosen by the language community to authorize evaluation runs via Threshold Signature Scheme (TSS) push-button approval. Stewards are not Champollion employees or contractors. They are community-chosen representatives — elders, council members, education directors, or other trusted individuals. See [Governance & OCAP Working Document](/docs/governance-and-ocap) for the 3-of-5 Multi-Party Computation design.

**1.8 Developer.** The individual, team, or organization that builds and submits a Method for evaluation. If the Developer is a team, all team members must individually agree to these terms. See [Prize Specification §3.6](/docs/specifications/prizes).

---

## §2 Admissibility

### 2.1 Core Requirement

A Method submitted for prize evaluation must be Self-Hostable as defined in §1.5. The Method must be fully self-contained: given the submitted artifacts and a documented hardware specification, the Governance Organization must be able to install and run the Method on their own infrastructure without assistance from the Developer and without connectivity to any external service.

This is a technical constraint with a sovereignty rationale. The Sandbox is air-gapped — it has no network access. But the deeper reason is OCAP® Possession: **if the community cannot independently operate the Method, they do not possess it.** A Method that requires a monthly license check, an API key to a service the community does not control, or a model hosted on infrastructure the community cannot access is one that can be taken away. That is incompatible with Possession.

### 2.2 Explicitly Inadmissible

The following categories of Methods are not eligible for prize evaluation:

| Category | Example | Why Inadmissible |
|----------|---------|-----------------|
| **Coached API calls to proprietary LLMs** | "Send this text to Claude/GPT-4 with this prompt" | The community cannot own Anthropic's or OpenAI's model weights. When the API key expires or the provider changes terms, the Method dies. The community possesses a wrapper, not a capability. |
| **API wrappers around third-party services** | Calling Google Translate, DeepL, or any external translation API | Same problem — the Method is a thin client. The actual translation capability lives on infrastructure the community does not control. |
| **Methods that phone home** | License servers, telemetry endpoints, usage tracking, update checks | Any network dependency gives an external party a kill switch. OCAP® Possession requires that no third party can disable the Method. |
| **Time-bombed dependencies** | Libraries with expiring licenses, trial-period SDKs, models with usage caps | A Method that stops working on a calendar date is not a community asset — it is a loan. |
| **Methods requiring runtime access to models the community does not possess** | "Download the model from HuggingFace at inference time" | If the model is not included in the submission, the community does not possess it. Model availability on third-party platforms can change without notice. |
| **Methods with obfuscated components** | Compiled-only binaries without source, encrypted model weights, undocumented dependencies | OCAP® Ownership requires the ability to inspect and modify. If the community cannot read the code, they do not own it in any meaningful sense. |

> **Read with §2.6.** The first two rows target Methods whose *capability* lives in an external service — thin wrappers the community could never operate independently. They do not prohibit a Method from consuming LLM inference as a declared, substitutable component (Dependency Class A1), where the Method's actual engineering — prompts, coaching data, pipeline logic, validation — is fully contained in the submission and the model is interchangeable configuration. §2.6.3 defines the test that separates the two.

### 2.3 Explicitly Admissible

The following categories of Methods are eligible, provided they meet the Self-Hostable requirement:

| Category | Example | Why Admissible |
|----------|---------|---------------|
| **Fine-tuned open-weight models** | LoRA adapter on Llama 3, fine-tuned NLLB | The community owns the base model weights and the adapter weights. They can inspect, modify, and redeploy. Full Possession. |
| **FST/rule-based pipelines** | GiellaLT finite-state transducer with pre/post-processing | Deterministic, inspectable, modifiable. The community understands exactly what the system does. |
| **Custom-trained models** | Transformer trained from scratch on community-approved data | The community owns the architecture, the weights, and the training pipeline. |
| **Hybrid pipelines** | FST validation → open-weight LLM → dictionary lookup → retry | Multiple components, all Self-Hostable. The community possesses every stage. |
| **Any method runnable on community infrastructure** | If it runs on commodity hardware without external dependencies, it is admissible | The test is functional, not architectural. |

### 2.4 Edge Cases

**Methods that were developed using proprietary APIs but do not require them at runtime** — for example, a model distilled from GPT-4 outputs during training but deployable standalone — are admissible. The admissibility test applies to the submitted artifact, not to the development process. We evaluate the output, not the training process (see [Benchmark Specification §1.4](/docs/specifications/benchmark)).

**Methods that include open-weight models larger than the Governance Organization's current hardware** are admissible if the Method is self-contained. Hardware constraints are an operational concern, not an admissibility concern. The Governance Organization may decline to evaluate a Method that exceeds their compute capacity, but the Method is not inadmissible per se.

### 2.5 Non-Commercial Corpus Content

Some corpora available during method development carry non-commercial licenses — for example, the EdTeKLA Cree Language Textbook corpus is licensed **CC BY-NC-SA 4.0**. Such corpora are **research/development-lane only** within the Champollion ecosystem.

A Method submitted under this agreement **must not embed content from a non-commercially-licensed corpus** — whether as coaching data, embedded translation examples, lookup tables, fine-tuning data whose license prohibits commercial use of derivatives, or any other included artifact. The transfer in §4 conveys deployment and monetization rights to the Governance Organization (§6); a Method containing NC-licensed content could not lawfully be deployed commercially, defeating the purpose of the transfer. This is a specific instance of the license-compatibility representation in §9.1.

The Prize Corpus itself is unaffected by this concern: it is **community-commissioned, human-authored original material** (§1.3), with rights cleared for evaluation and commercial deployment from the outset. It does not incorporate NC-licensed corpus content.

Developers remain free to use NC-licensed corpora to develop, iterate, and self-evaluate before submission. The restriction applies to what is included in the submitted artifact, not to the development process (consistent with §2.4 — we evaluate the output, not the training process, except where included content carries license terms incompatible with §4 transfer).

### 2.6 Dependency Classes

The admissibility rules in §2.1–2.5 reduce to a single mechanical question: **what does the Method depend on, and who holds the rights to each dependency?** The [Method Interface specification](/docs/specifications/methods#method-validity-and-dependency-classes) defines five dependency classes and the dependency manifest every submission must declare. The Sandbox is being built around these classes: everything a Method needs must either exist inside the Sandbox or arrive through an explicitly authorized path — so to qualify for a prize, the Developer must hold (or have been granted) the rights to put every dependency there.

| Class | Definition | Prize admissibility |
|-------|-----------|---------------------|
| **S** — Self-contained | All code, data, and weights ship in the submission under licenses permitting redistribution and §4 transfer | **Admissible** |
| **O** — Open external | Externally hosted artifacts under open licenses permitting redistribution (including copyleft), pinned and mirrored into the submission | **Admissible**, subject to §2.6.2 |
| **A1** — Substitutable LLM inference | Runtime LLM calls where the model is interchangeable configuration | **Conditionally admissible**, subject to §2.6.3 |
| **A2** — Non-substitutable external API | Runtime calls to a data or service API whose content cannot be mirrored or substituted without a rights holder's permission | **Not admissible** until permissions exist — §2.6.4 |
| **X** — Closed | Bundles content the Developer has no right to include | **Inadmissible** in every lane |

A Method's class is the most restrictive class among its declared dependencies. An undeclared dependency discovered in code review (§3.2) is grounds for rejection regardless of its class — the manifest must be complete, not merely accurate.

#### 2.6.1 Class S and O — the default path

Class S Methods satisfy §2.1 directly. Class O Methods satisfy it by **vendoring**: at submission time, each open-licensed external artifact is pinned (version or content hash) and mirrored into the submitted artifact, so the Sandbox needs no network access and the Governance Organization physically possesses every component.

#### 2.6.2 Class O license-compatibility conditions

The §4 transfer conveys *ownership* of the Developer's original work. Third-party open-licensed components are different: the Developer cannot transfer ownership of what they do not own. For those components, the Governance Organization receives them **under their own license terms**, which must independently grant everything Possession requires — the right to use, inspect, modify, and redeploy without the Developer's involvement. Concretely:

- Copyleft terms are preserved through transfer. An AGPL component stays AGPL in the community's hands; the community receives the same rights the license grants everyone, including the complete corresponding source.
- The component's license must be compatible with the deployment and monetization rights conveyed in §4 and exercised under §6. Copyleft licenses qualify (they condition commercial use on source availability; they do not prohibit it). Non-commercial licenses do not (§2.5).
- This is the operational form of the license-compatibility representation in §9.1.

#### 2.6.3 Class A1 — substitutable LLM inference

Most contemporary methods call LLMs. The line this agreement draws is not "no API calls" — it is **"no capability the community cannot possess."** A Method is Class A1, and conditionally admissible, when *all* of the following hold:

1. **Declared and pinned.** The manifest declares the inference dependency with `access: gateway` and the specific model identifier(s) used for evaluation.
2. **Substitutable.** The Method runs end-to-end against any compatible inference endpoint, including a community-hosted open-weight model. The model is configuration, not architecture. The Method must not depend on provider-side state — a fine-tune hosted only at a provider, provider file stores, or provider-specific features cannot be slotted out and make the dependency A2 (unless the underlying weights are included in the submission, which makes it S/O).
3. **Evaluated through the gateway.** Gold-standard evaluation routes inference exclusively through the LLM gateway defined in [Benchmark Specification §8.6](/docs/specifications/benchmark) — allowlisted pinned models, every request and response logged and auditable. *The gateway is specified but not yet built. Until it is operational, Class A1 Methods are admissible in principle but cannot be evaluated against sealed segments — only Class S and O Methods can currently complete the prize pipeline.*
4. **Transfer scope is explicit.** Upon acceptance, §4 conveys the complete recipe: all prompts, coaching data, pipeline code, retry and validation logic, configuration, and documented model requirements. **The model itself does not and cannot transfer.** What the community actually receives is the recipe plus the demonstrated ability (condition 2) to point it at any provider they choose, or at open weights on their own hardware. Prize scores are tied to the pinned evaluation model; substituting a different engine may change output quality, and the run card records which model the thresholds were met with.

This is honestly a weaker form of Possession than Class S — the community owns the recipe, not the engine. Stewards may weigh that in authorization (§7.3), and a Governance Organization may decline Class A1 submissions for a given prize entirely. The substitutability requirement is what keeps Class A1 inside OCAP® bounds at all: the community can always run the Method independently at *some* quality level, and no provider holds a kill switch over the capability itself.

#### 2.6.4 Class A2 and X — rights the Developer does not hold

A Class A2 Method depends at runtime on an external service whose substance — typically proprietary or unlicensed data — cannot be mirrored into the Sandbox or conveyed under §4, because the rights belong to someone who has not granted them. Such a Method is **not prize-admissible**. It may appear on the open (development-segment) leaderboard with a visible "external dependency" flag, but it cannot produce gold-standard scores or claim a prize.

The path to admissibility is permission, not engineering: if the rights holder grants (i) permission to include the artifact in the Sandbox and (ii) transfer terms compatible with §4, the dependency reclassifies (to O or S) and the Method becomes admissible. Re-architecting the *access mode* — bundling the data versus calling an API for it — changes nothing if the rights question is unresolved.

A Class X Method bundles such content without permission. It is inadmissible everywhere, including the open leaderboard: redistribution without rights is a license violation wherever the method runs, and §9.1–9.2 would be breached at signature.[^itwewina]

[^itwewina]: **Worked example (no fault implied).** Consider a hypothetical eng→crk pipeline with three dependencies: (a) the GiellaLT `lang-crk` FST — AGPL-3.0-or-later, mirrorable into the submission: **Class O**; (b) LLM inference through the evaluation gateway with a pinned, substitutable model: **Class A1**; (c) runtime lookups against the itwêwina dictionary API, whose served content (Wolvengrey's *nêhiyawêwin: itwêwina* and the Maskwacîs Cree Dictionary) carries no public license — the morphodict *software* is Apache-2.0, but a software license does not license the data the software serves: **Class A2**. The effective class is A2, so the pipeline is not prize-admissible as it stands. That outcome reflects no wrongdoing by anyone — the dictionary's creators never offered those rights, and the prize cannot launder rights nobody granted. If the dictionary's rights holders granted sandbox-inclusion and transfer permissions (for instance, under community-governance terms like those in this agreement), dependency (c) would reclassify and the same pipeline would become admissible. This is the admissibility system working as designed.

---

## §3 Evaluation Process

### 3.1 Submission

The Developer submits their complete, runnable Method to the Governance Organization. The submission includes all components listed in §1.1: source code, model weights, configuration, coaching data, prompts, dependencies, installation instructions, and a README describing the approach.

The Developer also submits a development-set run card showing approximate scores against the public development segment. This run card is used for pre-screening — if the development-set scores are far below the Acceptance Threshold, the Governance Organization may advise the Developer to iterate further before consuming evaluation resources.

### 3.2 Code Review

Before execution, Stewards or their technical delegates review the submitted Method code. The review checks for:

- Compliance with §2 admissibility requirements
- Dependency manifest audit: every declared dependency checked against its stated license, source, and access mode, and the declared dependency class (§2.6) verified against what the code actually does
- Absence of malicious code (data exfiltration attempts, backdoors, obfuscated network calls)
- Absence of undeclared dependencies
- Correct documentation of all components

This review is a manual step. For high-stakes prize evaluations, manual code review is essential and non-negotiable. See [Governance & OCAP Working Document](/docs/governance-and-ocap) for anti-exfiltration considerations.

### 3.3 Steward Authorization

Each evaluation run requires authorization from the community Stewards via TSS threshold signature. The threshold is **3-of-5**: at least 3 of the 5 community-chosen Stewards must approve the evaluation before it proceeds.

Authorization is **per-submission** — there is no blanket approval for prize evaluations. Each Method submitted for evaluation requires a fresh authorization cycle. This ensures the community actively consents to each use of their data. See §7 for the full consent model.

### 3.4 Sandbox Execution

The approved Method is installed in the Sandbox and executed against the sealed gold-standard test segment. The Sandbox is air-gapped. The Method has no network access, with one specified exception: a Class A1 Method's inference calls route through the LLM gateway defined in [Benchmark Specification §8.6](/docs/specifications/benchmark) — allowlisted pinned models only, every request and response logged (the gateway is specified but not yet operational; see §2.6.3). All inputs and outputs are logged for audit purposes.

### 3.5 Score Return

Only aggregate scores are returned to the Developer: composite, chrF++, FST acceptance rate, and other metrics defined in the [Scoring Specification](/docs/specifications/scoring). The Developer does not receive per-entry results against the gold-standard segment. The Developer never sees the source sentences, the reference translations, or any content from the sealed segments.

### 3.6 Human Validation

If the Method's automated scores meet the Acceptance Threshold conditions, the Governance Organization proceeds to community review. A stratified sample of outputs (covering difficulty tiers 2–5) is reviewed by bilingual speakers. Speakers rate each translation on a scale: reject, gist, acceptable, excellent. The community validation threshold is defined per prize pool — for the Founder's Prize, ≥ 70% of reviewed entries must receive "acceptable" or "excellent" ratings from at least 2 independent reviewers.

If the community review passes, the Method has met the Acceptance Threshold. Transfer proceeds per §4.

If the community review fails, the Developer receives aggregate feedback (e.g., "57% acceptable — common issues: obviation errors, unnatural word order in formal register") but does not receive the specific sentences or translations reviewed.

### 3.7 Cross-Reference

The full evaluation protocol is defined in:
- [Benchmark Specification §8.2](/docs/specifications/benchmark) — sandboxed execution mechanics
- [Prize Specification §3](/docs/specifications/prizes) — claim process and multiple submission rules
- [Governance & OCAP Working Document](/docs/governance-and-ocap) — TSS key custody and anti-exfiltration design

---

## §4 Transfer of Rights

Upon acceptance — defined as the Method meeting or exceeding all components of the Acceptance Threshold (automated metrics AND human validation) — the following transfers occur:

### 4.1 Source Code

Full ownership of all source code comprising the Method transfers to the Governance Organization. This includes application code, scripts, configuration files, build systems, and documentation. The Governance Organization receives the right to use, inspect, modify, adapt, distribute, sublicense, and create derivative works from the source code.

### 4.2 Model Weights

All trained model weights, adapter weights, embeddings, and other learned parameters transfer to the Governance Organization. This includes base model weights (if open-weight models are used), fine-tuned layers, LoRA adapters, and any auxiliary models (e.g., reranking models, quality estimation models). The Governance Organization physically possesses the weight files and can deploy, retrain, or modify them.

### 4.3 Deployment Rights

Exclusive deployment rights for the transferred Method, as applied to the specific language pair evaluated, transfer to the Governance Organization. The Governance Organization controls:

- Where the Method is deployed (their infrastructure, Champollion API, other platforms)
- Who can access the Method (public, restricted, subscription-based)
- What pricing terms apply to commercial use
- Whether the Method can be sublicensed to third parties
- When and how the Method is updated or retired

"Exclusive" means the Developer may not independently deploy the transferred Method for the same language pair. The Developer retains rights per §5.

### 4.4 Rationale

This transfer implements two OCAP® principles simultaneously:

**Ownership:** The Governance Organization holds legal title to the Method. This is not a license — it is ownership. The community can modify the source code, retrain the model, adapt the Method for dialects, or replace components entirely. They are not dependent on the Developer for ongoing maintenance or permission.

**Possession:** The Governance Organization physically holds the code and the weights. The Method runs on their infrastructure or on infrastructure they authorize. No third party can revoke access, impose usage limits, or degrade the Method's functionality. The community possesses the capability, not merely a right to use it.

Together, Ownership and Possession ensure that the Method is a durable community asset — not a dependency on the developer's goodwill, a corporation's API pricing, or a model provider's terms of service.

---

## §5 Retained Rights

The Developer explicitly retains the following rights after transfer. These rights are not affected by the transfer in §4 and do not require permission from the Governance Organization to exercise.

### 5.1 Publication Rights

The Developer retains the unrestricted right to describe the Method's approach, architecture, techniques, and results in academic publications, conference presentations, technical reports, blog posts, and other forms of scholarly or public communication. The Developer may include quantitative results (scores, metrics, comparisons) from both development-set and gold-standard evaluations in publications.

The Developer may not publish the content of the sealed test segments (source sentences, reference translations, or per-entry gold-standard results), as they have never had access to this content.

### 5.2 Technique Reuse

The Developer retains the unrestricted right to apply the same architectural ideas, algorithmic approaches, training procedures, prompt engineering techniques, and pipeline designs in other work — including work on other languages, other language pairs, other tasks, and commercial products. The transfer in §4 applies to the specific artifact, not to the ideas embodied in it.

### 5.3 Attribution

The Developer retains permanent attribution credit as the Method's creator. The Developer's name (or team name) appears on the Champollion leaderboard, in any Governance Organization communications about the Method, and in any downstream deployment. Attribution persists regardless of subsequent modifications to the Method by the Governance Organization.

### 5.4 Rationale

These retained rights preserve standard academic freedom. The distinction is between the artifact (the specific trained system) and the ideas (the techniques used to build it). The artifact transfers because it was built on and validated against the community's linguistic knowledge — the community's data made it work for their language. The ideas remain with the Developer because ideas are not possessable in the OCAP® sense and because restricting them would be contrary to the open exchange of knowledge that makes research possible.

This separation follows established precedent. Open-source contributor license agreements (Apache ICLA, FSF Copyright Assignment) similarly distinguish between the contributed work and the contributor's right to reuse their own techniques. The Developer gives up the artifact; the Developer keeps the ideas.

---

## §6 Revenue

### 6.1 Revenue Split

Revenue generated from commercial deployment of the transferred Method is split as follows:

| Recipient | Share | Rationale |
|-----------|-------|-----------|
| **Governance Organization** | **90%** | The community owns the Method and the linguistic knowledge that makes it work. This share funds language programs, further research, speaker compensation, community resources — whatever the Governance Organization decides. |
| **Champollion platform** | **10%** | Covers infrastructure costs: API hosting, metering, leaderboard operations, sandbox maintenance, ongoing engineering support. |

The 10% Champollion share is an infrastructure margin, not a royalty. It covers the cost of maintaining the deployment pipeline that makes the Method accessible to developers and generates the revenue in the first place. See [Economic Model](/docs/sovereignty/economic-model) for the full flywheel.

### 6.2 Reporting

Champollion provides quarterly revenue reports to the Governance Organization. Each report includes:

- Total API calls to the Method during the quarter
- Revenue generated (gross and net of infrastructure costs)
- Governance Organization share (90%) and payment confirmation
- Per-language-pair breakdown (if the Governance Organization controls methods for multiple pairs)

Reports are delivered within 30 days of quarter end. The Governance Organization has the right to audit Champollion's API metering records upon reasonable request.

### 6.3 Scope

The revenue split in §6.1 applies to commercial deployment of the transferred Method through the Champollion API or any deployment infrastructure that Champollion operates. It applies to direct API revenue (per-call metering) and to subscription revenue attributed to the Method.

If the Governance Organization deploys the Method independently — on their own infrastructure, through their own channels, without using Champollion's platform — the Governance Organization retains 100% of revenue from that deployment. Champollion has no claim to revenue from independent deployments.

If the Governance Organization sublicenses the Method to a third party, the terms of that sublicense are the Governance Organization's prerogative. Champollion has no claim to sublicense revenue unless the sublicensee uses Champollion's deployment infrastructure, in which case the 90/10 split applies to the infrastructure-mediated portion.

### 6.4 Rationale

The revenue model implements the [CARE Principle of Collective Benefit](https://www.gida-global.org/care): data governance structures should lead to equitable outcomes for Indigenous communities. The 90% share ensures that commercial value created using the community's linguistic knowledge flows primarily to the community. The 10% infrastructure share ensures the platform that enables this value creation remains sustainable.

The Developer does not receive a revenue share from the transferred Method. The prize money (§1.4, [Prize Specification §2](/docs/specifications/prizes)) is the Developer's compensation. The community receives the ongoing asset. This is the core economic proposition: prize money is a one-time payment for creating a durable community asset.

---

## §7 Consent and Authorization

### 7.1 Per-Submission Authorization

Each evaluation run of a submitted Method against the sealed gold-standard test segment requires fresh authorization from the community Stewards via TSS threshold signature. The threshold is **3-of-5**: at least 3 of the 5 Stewards must approve before the evaluation proceeds.

There is no blanket pre-authorization for prize evaluations. Each submission — including resubmissions of improved Methods by the same Developer — triggers a new authorization cycle. The Stewards receive a notification describing the submission (developer identity, method description, estimated evaluation time) and approve or reject.

### 7.2 Authorization Scope

An authorization covers a single evaluation run: one Method, one execution against the sealed test segment. Authorization does not extend to:

- Subsequent resubmissions of the same Method
- Modified versions of the Method
- Other Methods by the same Developer
- Any other use of the sealed data

### 7.3 Refusal

Stewards may refuse authorization for any reason. Refusal does not require justification. The Developer has no right to evaluation against the sealed data — evaluation is a privilege granted by the community, not an entitlement of submission.

Common reasons for refusal might include: the Method uses data sources the community has concerns about, the Developer has not established a relationship with the community, the Governance Organization's evaluation resources are currently allocated elsewhere, or the community has decided to pause evaluations.

### 7.4 Rationale

Per-submission authorization implements OCAP® Control: the community controls access to their data. Each authorization is an active, affirmative act of consent — not a passive default. The TSS mechanism ensures that no single individual (including Champollion personnel) can authorize evaluation unilaterally. The community's authority over their data is cryptographically enforced.

This design follows the consent model articulated in the [NBDC Human Data Sharing Guidelines](https://nativebio.org/) for biodata: consent must be dynamic, ongoing, and community-controlled — not a one-time checkbox at the start of a project. Linguistic data, like biodata, is a "mercurial resource with unknowable potential" (Dhein, 2024) whose future uses cannot be fully anticipated at the time of consent.

---

## §8 Revocation

### 8.1 Deployment Revocation

The Governance Organization may revoke deployment authorization for a transferred Method at any time, for any reason. Revocation means the Method is removed from the Champollion API and any other Champollion-operated deployment infrastructure. The Governance Organization is not required to justify revocation.

### 8.2 Notice Period

Revocation takes effect 30 days after written notice to Champollion. During the 30-day period, Champollion will:

- Notify active API consumers that the Method is being retired
- Provide consumers with guidance on alternative methods (if available)
- Complete any in-flight API requests
- Cease all new API access to the Method after the 30-day period

### 8.3 Retained Rights After Revocation

Revocation of deployment authorization does not affect:

- The Developer's retained rights under §5 (publication, technique reuse, attribution)
- The Governance Organization's ownership of the Method under §4
- Any revenue owed to the Governance Organization for usage prior to revocation

The Governance Organization retains ownership of the Method after revoking deployment authorization. They may re-authorize deployment at any time, deploy independently, modify the Method, or shelve it indefinitely.

### 8.4 Rationale

Revocation implements OCAP® Control: the community maintains ongoing authority over how their linguistic assets are used. Ownership without the ability to revoke is not meaningful control — it is a label on an irrevocable license.

Circumstances that might motivate revocation include: the community determines the Method produces culturally inappropriate output, the Method is being used by consumers in ways the community objects to, the Governance Organization develops or acquires a better Method and wants to consolidate, or the community decides that commercial API access to their language's translations is no longer appropriate.

The 30-day notice period balances community authority with practical consideration for API consumers who have integrated the Method into their systems. It is not a constraint on the community's right to revoke — it is an operational grace period.

---

## §9 Representations and Warranties

### 9.1 Originality

The Developer represents that the Method is the Developer's original work, or that the Developer has obtained all necessary licenses, permissions, and rights to submit the Method under these terms. If the Method incorporates open-source components, the Developer represents that all such components are used in compliance with their respective licenses and that those licenses are compatible with the transfer in §4.

### 9.2 No Third-Party IP Claims

The Developer represents that, to the best of their knowledge, the Method does not infringe any third-party patent, copyright, trademark, trade secret, or other intellectual property right. If the Developer becomes aware of any potential infringement claim after submission, the Developer will promptly notify the Governance Organization and Champollion.

### 9.3 No Malicious Code

The Developer represents that the Method does not contain malicious code, including but not limited to: code designed to exfiltrate data from the Sandbox, backdoors, logic bombs, cryptocurrency miners, code that transmits data to external parties, or code that degrades or disables the Method after transfer.

### 9.4 Self-Hostability

The Developer represents that the Method is Self-Hostable as defined in §1.5 — that it runs on community infrastructure without any runtime dependency on external services, license servers, proprietary APIs, or network connectivity, subject only to the Class A1 refinement in §1.5 and §2.6.3. The Developer represents that all components necessary to operate the Method are included in the submission, and that the dependency manifest (§2.6) is complete and accurate.

### 9.5 Training Data Disclosure

The Developer represents that the Method was not trained on, fine-tuned on, or otherwise exposed to any entries from the `gold_standard` or `held_out` segments of the Prize Corpus. (This is architecturally enforced by the sealed corpus design — the Developer has never had access to these segments. This representation is a redundant safeguard.)

---

## §10 Limitation of Liability

### 10.1 Voluntary Participation

This agreement governs a voluntary prize competition. The Developer chooses to submit a Method. The Governance Organization chooses whether to evaluate it. No party is obligated to participate, and no party is entitled to any specific outcome.

### 10.2 No Guarantee of Evaluation

Champollion does not guarantee that any submitted Method will be evaluated. Evaluation depends on Steward authorization (§7), Governance Organization capacity, and Sandbox availability. Submission does not create an obligation to evaluate.

### 10.3 No Guarantee of Results

Champollion and the Governance Organization make no representations about the expected scores, rankings, or outcomes of any evaluation. Automated metrics are proxies for translation quality (see [Benchmark Specification §1.1](/docs/specifications/benchmark)), not quality guarantees.

### 10.4 Limitation

To the maximum extent permitted by applicable law, neither Champollion nor the Governance Organization shall be liable to the Developer for any indirect, incidental, consequential, special, or exemplary damages arising out of or in connection with this agreement, including but not limited to loss of profits, loss of data, or loss of business opportunity, regardless of whether such damages were foreseeable.

The aggregate liability of Champollion and the Governance Organization to the Developer under this agreement shall not exceed the amount of any prize money actually paid to the Developer.

### 10.5 Developer's Liability

The Developer shall indemnify and hold harmless Champollion and the Governance Organization from any claims, damages, or liabilities arising from: (a) breach of the Developer's representations and warranties in §9, (b) infringement of third-party intellectual property rights by the Method, or (c) malicious or harmful code included in the Method.

---

## §11 OCAP® Alignment Table

Every substantive section of this agreement implements a specific principle from OCAP® or CARE. This table maps the connection explicitly.

| Section | OCAP® / CARE Principle | How This Section Implements It |
|---------|----------------------|-------------------------------|
| **§2 Admissibility** | **Possession** (OCAP) | By requiring Self-Hostability, the agreement ensures the community can physically hold and independently operate any Method that enters the prize pipeline. Methods the community cannot run independently are excluded at the gate. |
| **§3 Evaluation Process** | **Control** (OCAP) | The evaluation process is community-controlled at every step: code review, Steward authorization, Sandbox execution, and human validation are all conducted by or on behalf of the Governance Organization. The Developer's role is to submit and wait. |
| **§4 Transfer of Rights** | **Ownership + Possession** (OCAP) | Legal ownership of the artifact transfers. Physical possession of the code and weights transfers. The community can inspect, modify, deploy, retrain, sublicense, or shelve the Method. No third party retains a claim. |
| **§5 Retained Rights** | *(Academic freedom — no OCAP mapping)* | Retained rights preserve the Developer's academic freedom. This section has no OCAP mapping because it protects the Developer's interests, not the community's. OCAP does not require restricting academic freedom — it requires community ownership of community assets. |
| **§6 Revenue** | **Collective Benefit** (CARE) | 90% of commercial revenue flows to the community. The transferred Method becomes a revenue-generating asset. The CARE Principle of Collective Benefit requires that data governance structures lead to equitable outcomes — this revenue model is the structural implementation. |
| **§7 Consent and Authorization** | **Control** (OCAP) | Per-submission TSS authorization ensures the community actively, affirmatively consents to each use of their data. Consent is dynamic and ongoing — not a one-time checkbox. Cryptographic enforcement ensures no single party can bypass community authority. |
| **§8 Revocation** | **Control** (OCAP) | The community can revoke deployment authorization at any time. Ownership without revocation power is not meaningful control. This section ensures the community's authority is ongoing, not frozen at the moment of transfer. |
| **§9 Representations** | **Responsibility** (CARE) | The Developer accepts responsibility for the integrity of their submission. The CARE Principle of Responsibility requires that those who work with Indigenous data are accountable for their actions. |
| **§10 Limitation of Liability** | *(Standard legal practice — no OCAP mapping)* | Standard limitation provisions for a voluntary prize competition. |

---

## Appendix A: Comparable Precedents

This agreement draws on several established models for governing the transfer of intellectual property in contexts where data sovereignty, community benefit, and open research intersect.

### A.1 NBDC Human Data Sharing Guidelines

The [Native BioData Consortium](https://nativebio.org/) (NBDC) developed governance protocols for biodata (genomic, phenotypic, and health data) that address many of the same structural challenges Champollion faces with linguistic data. Key parallels:

- **Data as a mercurial resource.** NBDC recognizes that biodata has unknowable future uses — consent given for one purpose may be insufficient when the data is repurposed. Champollion's sealed corpus model and per-submission authorization (§7) implement the same principle for linguistic data: consent is dynamic, not static.
- **Tribal infrastructure hosting.** NBDC requires that data be hosted on Tribal infrastructure, not university or corporate servers. Champollion's Self-Hostability requirement (§2) and Sandbox architecture (§3) implement the same principle: the community physically possesses the data and the tools.
- **Governance by community representatives.** NBDC's governance board consists of Tribal representatives, not academics or corporations. Champollion's Steward model (§7) follows the same design.

### A.2 Creative Commons Contributor License Agreements

The Creative Commons Contributor License Agreement (CC CLA) provides a precedent for the separation of artifact transfer and retained rights. Under the CC CLA:

- Contributors assign copyright in their contributions to Creative Commons
- Contributors retain the right to use their contributions in other work
- Attribution is preserved

This mirrors Champollion's §4 (artifact transfers) and §5 (ideas and academic freedom are retained). The structural insight is that assigning ownership of a specific contribution does not require surrendering the ability to do similar work elsewhere.

### A.3 Open-Source IP Assignment Agreements

Two widely-used models for contributor IP assignment:

**Apache Individual Contributor License Agreement (ICLA).** The Apache ICLA grants the Apache Software Foundation a perpetual, irrevocable, non-exclusive license to contributed work. The contributor retains ownership. Champollion goes further — we transfer ownership, not just a license — because OCAP® Possession requires that the community hold the asset, not merely a permission to use it.

**Free Software Foundation Copyright Assignment.** The FSF requires contributors to assign copyright to the FSF, which then licenses the work under the GPL. The contributor receives a non-exclusive license back. This is closer to Champollion's model: full ownership transfers to the custodial organization, and the contributor retains the right to use their own techniques. The difference is that Champollion's transfer is to a language community governance body, not a software foundation.

### A.4 The Dhein Framework for Biodata Sovereignty

Kelle Dhein's framework for biodata sovereignty in genomics (Dhein, 2024) articulates the theoretical foundation for treating community-generated data as a "mercurial resource with unknowable potential." Key concepts applied in this agreement:

- **Pragmatic sovereignty.** Sovereignty is not just legal — it requires physical control of infrastructure and the ability to revoke access dynamically. Champollion implements this through the Sandbox (§3), TSS authorization (§7), and revocation (§8).
- **Relational governance.** The governing body must have a relational connection to the community, not just a contractual one. This is why §1.2 requires the Governance Organization to have "legitimate relational authority" — a legal entity without community relationships is insufficient.
- **Dynamic consent.** Static consent at the point of data creation is insufficient for resources whose future uses cannot be fully anticipated. Champollion's per-submission authorization (§7) implements dynamic consent for each evaluation run.

### A.5 Summary of Precedent Mapping

| Precedent | What Champollion Borrows | What Champollion Does Differently |
|-----------|-------------------------|----------------------------------|
| **NBDC** | Community-controlled infrastructure, dynamic consent, Tribal governance | Applied to linguistic data and MT methods rather than biodata |
| **CC CLA** | Separation of artifact transfer and retained rights | Full ownership transfer rather than license grant |
| **Apache ICLA** | Contributor license structure, attribution preservation | Ownership transfer rather than non-exclusive license |
| **FSF Assignment** | Full copyright assignment with retained use rights | Transfer to community governance body rather than software foundation |
| **Dhein Framework** | Mercurial resource theory, pragmatic sovereignty, dynamic consent | Applied to machine translation prize competition rather than genomics research |

---

## References

- First Nations Information Governance Centre (FNIGC). OCAP®: Ownership, Control, Access and Possession. https://fnigc.ca/ocap-training/
- Global Indigenous Data Alliance (GIDA). CARE Principles for Indigenous Data Governance. https://www.gida-global.org/care
- Local Contexts. Traditional Knowledge and Biocultural Labels. https://localcontexts.org/
- Te Mana Raraunga — Māori Data Sovereignty Network. https://www.temanararaunga.maori.nz/
- Native BioData Consortium. https://nativebio.org/
- Dhein, K. (2024). *Biodata Sovereignty.*
- Apache Software Foundation. Individual Contributor License Agreement (ICLA). https://www.apache.org/licenses/icla.pdf
- Free Software Foundation. Copyright Assignment. https://www.gnu.org/licenses/why-assign.html
- Creative Commons. Contributor License Agreement. https://creativecommons.org/licenses/
