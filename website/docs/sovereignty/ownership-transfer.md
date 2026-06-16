---
sidebar_position: 2
title: Ownership Transfer
---

# Ownership Transfer

> **Executive Summary.** When a translation method reaches Deployable tier (composite ≥ 0.70) and passes community review, code ownership transfers from the researcher to the Indigenous governance organization. This page documents the five-stage transfer pipeline, OCAP® alignment, and guidance for researchers building methods for Indigenous languages.

When a translation method wins on the Arena leaderboard, what happens to the code? For Indigenous and low-resource languages, the answer is not "the researcher keeps it." The answer is: **the community owns it.**

---

## How It Works

The Arena enforces a clear pipeline from research to community ownership:

### 1. Method Development
A researcher, student, or developer builds a translation method — an FST-gated pipeline, a coached LLM, a fine-tuned model, or any other approach. They develop it using their own resources.

### 2. Arena Evaluation
The method is benchmarked through the [eval harness](/docs/specifications/harness). Every submission is fingerprinted to a specific Git commit and dataset version. Scores are reproducible.

### 3. Community Review
For Indigenous language methods, results are reviewed by community language workers and governance organizations. A high leaderboard score proves the method *works*; it does not prove it is *appropriate*.

### 4. Code Transfer
When a method achieves **Deployable** tier (composite score ≥ 0.70 against the gold-standard evaluation) **and** passes community review (human validation):
- The researcher hands over the source code
- Legal ownership transfers to the Indigenous governance organization (e.g., a tribal council, language authority, or Métis organization)
- The governance org holds the encryption keys for evaluation datasets
- The method becomes a community-controlled asset

See the [Scoring Specification](/docs/specifications/scoring), §5 for quality tier definitions and the [Benchmark Specification](/docs/specifications/benchmark), §8.3 for the full transfer conditions and §7 for the human validation gate.

### 5. Production Deployment
The method is exported as an [champollion](https://champollion.dev) plugin and deployed to the production API. The community controls:
- Who can access the method
- What pricing terms apply
- Whether the method can be used commercially
- When and how the method is updated

---

## Why This Matters

Traditional ML research follows an extractive pattern:
1. Researcher collects data from a community
2. Researcher trains a model
3. Researcher publishes a paper
4. Community receives nothing

This pattern now operates at industrial scale. Meta's OMT-1600 (March 2026) trained translation models for 1,600 languages — including Indigenous languages like Plains Cree — using web-scraped data and Bible translations. The models were trained without community consent protocols, the weights are not currently available for download, and the communities whose languages were modeled have no ownership stake, no governance role, and no revenue. The paper is the product. The community is the data source.

The Arena inverts this:
1. Researcher builds a method
2. Arena validates it against community-curated corpora with morphological metrics
3. Community receives ownership of the working code
4. Community earns revenue from API usage

**This is the fundamental difference between Champollion and every other LRL MT effort, including OMT-1600:** we don't just produce methods for communities — we transfer ownership of methods *to* communities. The code, the weights, the deployment infrastructure — it all becomes community property. This is not a theoretical framework — it is the operational pipeline for every Indigenous language method on the platform.

---

## OCAP® Alignment

The ownership transfer process directly implements the [OCAP® principles](/docs/sovereignty/data-sovereignty):

| Principle | Implementation |
|---|---|
| **Ownership** | The governance org holds title to the method code and model weights |
| **Control** | The governance org controls deployment terms, access, and pricing |
| **Access** | Community members access the method through the champollion API or direct download |
| **Possession** | Linguistic resources (coaching data, dictionaries, FST rules) remain on community-controlled infrastructure via the `api` method |

---

## For Researchers

If you are developing a method for an Indigenous language:

1. **Establish a relationship** with the language community before you start
2. **Use openly licensed data** for development (not community-restricted resources)
3. **Document provenance** in your [run card](/docs/specifications/run-card) — list every resource, its license, and origin
4. **Be prepared to transfer** — if your method succeeds, the code belongs to the community, not to you
5. **This is a feature, not a limitation** — your contribution is the architecture and technique, which you can publish and reuse. The community's contribution is the linguistic knowledge that makes it work for their language.

---

## See Also

- [Data Sovereignty](/docs/sovereignty/data-sovereignty) — OCAP, CARE, and Te Mana Raraunga principles
- [The Economic Model](/docs/sovereignty/economic-model) — how ownership becomes revenue
- [Support a Low-Resource Language](/docs/community/low-resource-languages) — the research context
