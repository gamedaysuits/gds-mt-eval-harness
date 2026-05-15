# Vision: Crowdsourced Machine Translation via Attested Methods

> **Status**: Future plan — design notes captured May 14, 2026  
> **Scope**: i18n-rosetta + mt-eval-harness ecosystem  
> **Author**: Curtis Forbes  

---

## The Big Idea

There are ~7,000 living languages. Fewer than 200 have any MT support. Google and DeepL will never solve the other 6,800 — there's no commercial incentive.

**The thesis**: We solve this by making it trivially easy for any developer who speaks both languages to conceive, build, test, publish, and monetize a translation method — with cryptographic integrity guarantees and community verification.

The full loop, dead simple:

```
 DREAM IT          BUILD IT           TEST IT           HASH IT          SHIP IT
    │                  │                  │                 │                │
    ▼                  ▼                  ▼                 ▼                ▼
"I could solve    Write a custom     Plug it into      Get a method      Stand up an
 Cree MT using    TranslationProcess  mt-eval-harness   attestation      i18n-rosetta
 decomposition    plugin (or just    → run against a    fingerprint      compatible API
 + FST gates"     iterate on a       reference corpus   that binds       → publish your
                  prompt)            → get scores       your scores      method with
                                                        to your exact    hash guarantee
                                                        method
```

**What the developer gets**: A published, hash-guaranteed translation API that anyone can call, with publicly verifiable benchmark scores.

**What the language community gets**: Translation technology that didn't exist before.

**What consumers get**: Cryptographic proof that the method serving their translations is the exact method that produced the published benchmarks. No bait-and-switch.

---

## Progressive Depth: Three Tiers of Engagement

The system must be approachable at every skill level. Not everyone who speaks Cree is an ML engineer. Not every ML engineer speaks Cree. The architecture supports three tiers:

### Tier 1: Prompt Engineer (Zero Code)

**Who**: Anyone who speaks both languages and can write a good prompt.

**What they do**:
1. Write a system prompt that instructs an LLM how to translate their language pair
2. Point the harness at their prompt + a reference corpus
3. Run `mt-eval run --prompt my_prompt.txt --corpus my_corpus.json`
4. Iterate on the prompt until scores improve
5. Export: `mt-eval export --report results.json --name my-method-v1`

**What the harness gives them**: Attestation hash, benchmark scores, a ready-to-deploy rosetta plugin.

**Fine-tuning angle**: The harness can programmatically iterate on prompt variants. "Try 50 structural variations of this prompt, report which one scores highest." The developer doesn't write code — they write prompts and the harness finds the best one.

### Tier 2: Pipeline Builder (Some Code)

**Who**: A developer who understands their language's structure well enough to decompose the translation problem.

**What they do**:
1. Write a `TranslationProcess` plugin that implements a multi-step pipeline
2. Use deterministic components where possible (dictionaries, FSTs, grammar rules)
3. Use LLMs only for the judgment calls (semantic parsing, lexical selection, assembly)
4. Gate each step with formal verification (FST validity, dictionary membership, grammar checks)

**Example** (the CRK pipeline pattern):
```
English → [spaCy clause parse] → [LLM: semantic enrichment]
  → [LLM: lexical selection + dictionary lookup]
  → [LLM: morphological tagging]
  → [FST: deterministic generation — HARD GATE]
  → [LLM: word-order assembly]
  → [Deterministic grammar check]
  → Plains Cree
```

**Fine-tuning angle**: Each LLM step is independently evaluable. Fine-tune a small open-weight model (Mistral 7B, Llama) for JUST that step. The harness evaluates each step's contribution independently. The FST gates ensure the fine-tuned model can't hallucinate — it either produces valid morphology or it doesn't.

### Tier 3: Researcher (Full Stack)

**Who**: Computational linguists, ML researchers, language revitalization teams.

**What they do**:
1. Everything in Tier 2, plus:
2. Build custom evaluation metrics (MetricPlugin) for language-specific quality
3. Build custom corpora with difficulty grading and segment annotation
4. Run automated fine-tuning loops: train model → harness eval → check scores → retrain
5. Publish methods with full provenance (training data sources, model lineage, licensing)
6. Apply for community verification badges (see below)

**Fine-tuning angle**: Use the harness as the evaluation harness in an automated research loop. Generate SFT training data from successful harness runs. Use FST rejection rates as training signal. Iterate until convergence.

---

## The Attestation Layer: No Bait-and-Switch

### What Gets Hashed

The **method attestation fingerprint** is a SHA-256 hash of everything that defines a translation method's behavior:

- Model identity (exact model ID, not just "some LLM")
- System prompt content (full text, every character)
- Coaching data (every file in the coaching directory, content-hashed)
- Post-translation hooks (names + versions)
- Tool configurations (which tools, what settings)
- Pipeline process identity (plugin name + version)
- Temperature, batch size, and all config knobs that affect output

**If anything changes, the hash changes.** Add one coaching example? New hash. Swap the model? New hash. Edit one word in the prompt? New hash.

### The Trust Chain

```
Developer builds method
        │
        ▼
Harness evaluates method against reference corpus
        │
        ▼
Harness computes attestation fingerprint
   fingerprint = SHA-256(model + prompt + coaching + hooks + config)
        │
        ▼
TestReport binds fingerprint to benchmark scores
   "Fingerprint a3f8c2 scored 40.2 chrF, 31% exact match, 87% FST validity"
        │
        ▼
Exported plugin manifest embeds fingerprint + scores
        │
        ▼
Published API includes fingerprint in every response
        │
        ▼
Consumer can verify: "Is this the method that got those scores?"
   → Request includes expected fingerprint
   → Server confirms match or rejects with ATTESTATION_MISMATCH
```

### What This Prevents

1. **Bait-and-switch**: Test with a good model, serve with a cheap one
2. **Silent degradation**: Method changes without re-benchmarking
3. **Unverifiable claims**: "Our method scores 85 chrF" — prove it
4. **Version confusion**: Which version of the method am I actually getting?

### Hashing vs. Signing: Two Different Jobs

These are distinct mechanisms that solve different problems:

- **Hash (SHA-256)**: Proves the method *hasn't changed* since benchmarking. This is **integrity**. If the hash matches, the method is the same one that produced the published scores. This is the attestation fingerprint.
- **Signature (asymmetric keypair)**: Proves *who published it*. This is **identity**. The developer generates a keypair, signs their method manifest with their private key, and anyone can verify with their public key that this specific person published this specific method.

**Why signing matters**: Without it, someone could clone an open-source method, re-register it under their own name, and take credit. The original developer signed their manifest first — the timestamp + signature is the provenance proof.

**Why signing can wait**: The hash is the immediate priority. It catches the most dangerous scenario (method drift/swap). Signing is a "when the registry has enough methods to make impersonation worth doing" problem. Build the hash now, add signing when the registry has real traffic.

---

## The Benchmark Gaming Problem

> "Won't people just train to the benchmark?"

**Yes. This is the single biggest risk.** If the reference corpus is public and the evaluation is automated, a motivated developer could overfit their method to the benchmark corpus without actually solving translation.

### Solution 1: Private Holdout Sets

The reference corpus used for published benchmarks is public. But method publishers can (and should) maintain **private holdout corpora** for internal validation. The harness supports this natively — just point it at a different corpus file.

**Problem**: This only prevents self-deception. A developer who trains to the public benchmark and publishes great scores is still gaming the system even if they know their private scores are lower.

### Solution 2: Independent Test Corpora

A trusted third party (a language authority, a university department, a revitalization program) maintains a **sealed test corpus** that method developers never see. Methods are submitted for evaluation against the sealed corpus.

**Problem**: Requires institutional infrastructure. Who maintains it? Who pays for it?

### Solution 3: Community Verification Badges ← THIS IS THE ONE

**This is the real answer.**

Automated metrics (chrF, BLEU, exact match, FST validity) measure statistical similarity. They cannot measure:
- Whether the translation sounds natural to a native speaker
- Whether the register is appropriate
- Whether cultural connotations are preserved
- Whether the translation is correct in ways the reference corpus doesn't capture (multiple valid translations)

**Community Verification** solves this by adding human judgment from the people who actually matter: speakers of the language.

#### How It Works

1. **Developer submits method** for community review
2. **Native speakers** of both languages evaluate a sample of translations
3. Evaluation is structured:
   - **Fluency**: Does this sound like natural [language]? (1-5 scale)
   - **Adequacy**: Does this correctly convey the English meaning? (1-5 scale)
   - **Cultural appropriateness**: Is the register/tone correct? (yes/no/flag)
   - **Correctness**: Are there grammatical errors? (list specific issues)
4. **Verification badge** is issued when a method meets threshold scores from a minimum number of verified speakers
5. Badge is **bound to the attestation fingerprint** — if the method changes, the badge expires

#### Badge Tiers

| Badge | Requirement | What It Means |
|---|---|---|
| 🟢 **Automated Pass** | chrF > threshold, FST validity > threshold | Machine metrics pass. No human review yet. |
| 🔵 **Community Reviewed** | 3+ native speakers reviewed, avg fluency > 3.0 | Real humans looked at this and it's decent. |
| 🟣 **Community Verified** | 5+ native speakers, avg fluency > 4.0, avg adequacy > 4.0 | Native speakers confirm this is good. |
| 🟡 **Language Authority Endorsed** | Verified + endorsed by a recognized language body | Institutional stamp of approval. |

#### Why This Drives Engagement

This is the ecosystem flywheel:

```
Developer builds method for their language
        │
        ▼
Method gets automated scores (harness)
        │
        ▼
Developer seeks community verification
        │
        ▼
Native speakers engage with the platform to verify ← THEY GET PAID
        │
        ▼
Verified method gets published → consumers use it
        │
        ▼
Revenue from API usage funds more verification ← SUSTAINABLE
        │
        ▼
More developers see that solving [Language X] MT is possible
        │
        ▼
More methods submitted → more competition → better translation
        │
        ▼
The language gets real MT support for the first time
```

**The key insight**: You don't need to solve every language yourself. You need to make it possible for ANYONE to solve ONE language, verify it, publish it, and get paid. The platform is the infrastructure. The community is the solution.

#### Employing Verifiers

Native speakers who participate in community verification are **paid reviewers**, not volunteers. This is critical:

- Low-resource languages often correspond to economically marginalized communities
- Asking speakers to volunteer their linguistic expertise for free perpetuates extraction
- Paying verifiers creates economic incentive for language engagement
- Verification work can be done remotely, flexibly, on the verifier's schedule
- This is a job that literally cannot be automated — it requires native fluency

**Funding model**: A percentage of API revenue from verified methods flows back to the verification pool for that language. The more a method is used, the more its verifiers earn.

---

## The Marketplace Model

### What This Is (and Isn't)

This is NOT "OpenRouter for translation." OpenRouter is a dumb pipe — it routes API calls to model providers and takes a margin. It doesn't know or care what the model produces. It can't tell you "this model scores 42 chrF on Cree." It doesn't attest that a model hasn't changed. It doesn't run sealed benchmarks. It's a dumb pipe.

This IS a **public quality registry for translation methods**, backed by reproducible evaluation and cryptographic attestation. Think **Consumer Reports, not the App Store.** The registry is the directory. The harness is the trust layer. Developers host their own methods and handle their own billing.

**The platform's value is the quality stamp, not the billing rail.** The moat isn't the platform infrastructure — it's the eval harness. Nobody else has a pluggable translation method evaluation framework with FST-gated verification and content-addressable attestation. The harness is the thing.

### Rejected Architectural Models

These models were considered and explicitly rejected during the design process:

**Billing intermediary ("take 10% of every transaction")**:
- Requires the platform to be in the payment path for every API call
- Forces developers to route billing through the platform
- Creates infrastructure/liability/regulatory burden disproportionate to value
- The question "why not just call the developer's server directly?" has no good answer under this model
- **Rejected because**: the platform's value is trust, not transaction processing. Developers handle their own billing.

**Blockchain / tokenomics ("LanguageCoin")**:
- Token-based revenue sharing for algorithm discovery
- Smart contracts for automatic royalty distribution
- On-chain method registration for immutability
- **Rejected because**: blockchain adds complexity without adding trust. The attestation hash already proves what method was used. The registry already tracks who registered it. Git is already an immutable append-only log. Every successful "blockchain for X" project eventually realizes the value was in X, not in the blockchain. The value here is in the MT marketplace.
- **One exception**: writing attestation hashes to a public chain as a timestamp/integrity proof (costs pennies, adds auditability) remains a viable Phase 5 feature, but as a feature of the registry, not the foundation of the platform.

**Encrypted algorithm execution (homomorphic encryption / secure enclaves)**:
- Running a method without anyone seeing the algorithm
- **Rejected because**: homomorphic encryption is 10,000-1,000,000x slower than normal computation for LLM workloads. Secure enclaves (SGX/TDX) are hardware-dependent and vendor-locked. Both are far beyond what's needed. The simpler version (developer runs on their own server, harness proves quality, hash proves consistency) solves the same problem without exotic infrastructure.

### Registry Architecture (Ultralight)

The registry is a published artifact — a JSON file, a static site, or a single database table. The platform operator maintains nothing actively; developers register, the registry is a directory.

```json
{
  "methods": [
    {
      "name": "crk-coached-v2",
      "publisher": "Curtis Forbes",
      "server_url": "https://crk-translate.example.com",
      "attestation": {
        "method_hash": "a3f8c2d1...full-64-char-SHA-256",
        "corpus_hash": "7b2e9f4a...full-64-char-SHA-256",
        "corpus_name": "crk-standard-v1",
        "corpus_size": 278
      },
      "scores": {
        "chrf": 40.2,
        "exact_match": 0.31,
        "fst_validity": 0.87
      },
      "cost_per_million_chars": 25.00,
      "verification_badge": "community_reviewed",
      "hosting_model": "self_hosted",
      "evaluated_at": "2026-05-14T21:00:00Z"
    }
  ]
}
```

### Why Full 64-Char SHA-256

At 16 hex characters (64 bits), birthday attack collision probability hits 50% at ~2³² methods. Full 64-char SHA-256 eliminates this entirely. Truncate only for display (`a3f8c2d1…` in logs and UI), never for verification.

### The Attestation Endpoint

Every method server must implement:

```
GET /v1/attest
→ { "attestation": "a3f8c2d1...64chars", "computed_at": "2026-05-14T..." }
```

This endpoint **computes the hash live** from the running method's actual state — reads the prompts, coaching data, model config, hashes them, returns the result. The computation code is open-source (it's in the harness). The server isn't declaring a hash, it's computing one from its live state.

### The Consumer Handshake

When i18n-rosetta calls a method server:

```
POST /v1/translate
Headers:
  X-Expected-Attestation: a3f8c2d1...64chars   ← from the registry

Response Headers:
  X-Method-Attestation: a3f8c2d1...64chars      ← computed live by server
```

If the server's live-computed hash doesn't match the consumer's expected hash → `400 ATTESTATION_MISMATCH`. The consumer knows the method has changed since benchmarking.

### What the Consumer Sees

The i18n-rosetta client queries the registry, presents available methods, and lets the consumer choose based on transparent tradeoff data:

- **Quality** (chrF, exact match, FST validity)
- **Cost** (per million characters)
- **Speed** (average response latency)
- **Trust level** (automated pass / community reviewed / authority endorsed)
- **Hosting model** (self-hosted / registry-hosted)

---

## The Verification Trilemma

> **This is the hardest problem in the system and it has no complete solution.**

Three parties exist: the **consumer** (wants verified translations), the **developer** (wants IP protection and revenue), and the **platform** (wants ecosystem integrity). Any trust architecture can satisfy at most two of the three:

| Model | Consumer trusts output? | Developer IP safe? | Platform can't cheat? |
|---|---|---|---|
| **Developer self-hosts** | ❌ Cannot verify remotely | ✅ Full control | ✅ Platform not involved |
| **Platform hosts method** | ✅ Platform executes known code | ❌ Must trust platform | ✅ Consumer sees execution |
| **Full zero-trust (E2E)** | ✅ | ✅ | ✅ — **Does not exist** |

### Why True Zero-Trust Is Impossible

You cannot remotely verify what code a server is running. This is a fundamental computer science limitation, not a solvable engineering problem. If someone controls the hardware, they control the output. Every endpoint they expose can lie. Every response header can be fabricated.

The only technologies that can prove remote execution are:

1. **Hardware attestation** (Intel SGX / AMD SEV) — the CPU itself signs what code is running. Requires specific hardware. Impractical for an indie platform.
2. **Verifiable computation** (zero-knowledge proofs) — mathematically proves a computation was performed correctly. Active research area (zkML). Completely impractical for LLM-scale workloads as of 2026.
3. **Platform-controlled execution** — the platform holds the method components and executes them. Works, but requires developer trust in the platform.

**There is no option 4.** Anyone who claims otherwise is selling blockchain tokens.

### The Practical Compromise: Two Hosting Models

Accept the trilemma. Be transparent about it. Let the developer choose their trust model:

#### Model A: Self-Hosted (Developer Controls Execution)

```
Consumer → Developer's Server (developer runs everything)
```

- ✅ Developer IP is fully protected
- ✅ No platform dependency for execution
- ❌ Consumer cannot verify the method hasn't been swapped
- **Trust mechanism**: Attestation handshake (catches honest drift), community verification badges (catches deliberate fraud over time), reputation

**Best for**: Proprietary methods, methods requiring custom infrastructure (local models, FST tools, heavy compute), developers who want full autonomy.

#### Model B: Registry-Hosted (Platform Controls Execution)

```
Consumer → Registry → OpenRouter/Mistral/etc. (registry calls model with developer's prompt)
```

For methods that are "prompt + coaching data + model API call" (which is MOST Tier 1 and basic Tier 2 methods), the registry can execute them directly. The method components are small files — the heavy compute is outsourced to the model provider.

- ✅ Consumer gets verified execution (registry assembled the prompt)
- ✅ Developer IP is protected from consumers (prompt/coaching never exposed to end users)
- ❌ Developer must trust the platform operator won't steal/modify their work
- **Trust mechanism**: Platform is open-source, operator is a known identity, method components are versioned — theft is visible and reputationally fatal

**Best for**: Prompt-engineering methods (Tier 1), coaching-based methods, developers who prioritize verified execution over infrastructure control.

The registry labels each method's hosting model clearly. Consumers choose their risk tolerance.

### Mystery Shopping (Probabilistic Enforcement for Self-Hosted Methods)

For self-hosted methods, the registry can perform periodic spot-checks:

1. At registration, capture a set of input→output **probe pairs** from the known-good method
2. Periodically send probe inputs as normal-looking translation requests
3. Compare outputs to the known-good baseline using chrF
4. If outputs diverge beyond a threshold → flag the method, suspend badge

**Limitations (honest assessment)**:
- A determined scammer could cache the first N outputs and serve those for recognized inputs
- Probe requests may be identifiable if the registry doesn't have sufficient cover traffic
- LLM non-determinism creates noise in output comparison (statistical, not exact-match)
- This catches lazy cheaters, not determined ones

**Cost**: ~10-20 translation requests per method per week. Fully automated cron job.

**Verdict**: Useful as a probabilistic deterrent, but NOT a guarantee. The real guarantee for self-hosted methods is community verification + reputation. Mystery shopping catches the 80%, community verification catches the next 15%, and the remaining 5% is accepted risk.

---

## The Full Ecosystem Map

```
┌──────────────────────────────────────────────────────────────────┐
│                     i18n-rosetta ECOSYSTEM                       │
│                                                                  │
│  ┌────────────┐     ┌──────────────┐     ┌───────────────┐      │
│  │  Developer  │────▶│ mt-eval-     │────▶│  Attestation  │      │
│  │  (builds    │     │ harness      │     │  Fingerprint  │      │
│  │   method)   │     │ (benchmarks) │     │  + Scores     │      │
│  └────────────┘     └──────────────┘     └───────┬───────┘      │
│                                                   │              │
│                               ┌───────────────────┤              │
│                               │                   │              │
│                               ▼                   ▼              │
│  ┌────────────┐     ┌──────────────┐     ┌───────────────┐      │
│  │  Community  │────▶│ Verification │     │  Registry     │      │
│  │  Verifiers  │     │ Badges       │     │  (directory)  │      │
│  │  (native    │     │ (human       │     │               │      │
│  │   speakers) │     │  judgment)   │     │  Stores:      │      │
│  └────────────┘     └──────┬───────┘     │  - hash        │      │
│                            │              │  - scores      │      │
│  ┌────────────┐            │              │  - URL         │      │
│  │  Sealed     │            │              │  - badge       │      │
│  │  Corpus     │────────────┘              │  - cost        │      │
│  │  (language  │  (secret evaluation      │  - corpus ID   │      │
│  │  authority) │   defeats benchmark      └───────┬───────┘      │
│  └────────────┘   gaming)                         │              │
│                                                   ▼              │
│                                          ┌───────────────┐      │
│                                          │  i18n-rosetta  │      │
│                                          │  Consumer      │      │
│                                          │  (calls API,   │      │
│                                          │   verifies     │      │
│                                          │   hash)        │      │
│                                          └───────────────┘      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Economic Model

### Revenue Is Not the Platform's Job

The platform does NOT intermediate billing. Developers charge whatever they want, however they want. The platform's value is discovery, trust, and verification — not payment processing.

### Developer Incentives

The economic thesis: if solving a translation problem = recurring revenue, people will invest real effort in solving it. Nobody solves Cree MT today because there's no mechanism to monetize the solution. This ecosystem creates that mechanism.

A developer who publishes a working, verified Cree→English method and charges $25/million characters creates a visible success story. Other bilingual developers see this and think: "I could do Ojibwe→English. I speak both languages." That's the flywheel.

### Language Community Revenue Share

A percentage of every translation for a given language should flow back to language revitalization programs. This is voluntary but encouraged at the platform level:

- Method developer earns from API usage
- Developer pledges X% to a language community fund (tracked in registry metadata)
- Community funds flow to: sealed corpus creation, verifier compensation, language programs
- Every API call becomes a micro-contribution to language preservation

### Working With Institutions

Language authorities, universities, and revitalization programs are natural partners:

- **They provide**: sealed test corpora, qualified verifiers, cultural authority for endorsement badges
- **They receive**: verification revenue, improved MT tools for their language, institutional recognition
- **Use case**: National or institutional pushes to translate documents and serve websites in indigenous/minority languages. The platform removes the friction; the institution provides the mandate.

---

## Why This Matters

The traditional approach to low-resource MT is:
1. Wait for Google to care (they won't)
2. Get a research grant, train a model, publish a paper, move on
3. The language community gets nothing usable

The rosetta approach is:
1. Anyone who speaks both languages can build a method
2. The method is publicly benchmarked with cryptographic integrity
3. Native speakers verify quality and get paid for it
4. The method is immediately deployable as a production API
5. Revenue sustains both the developer and the verification community
6. The problem gets solved incrementally, by the people who care most

**This is how we solve MT for 6,800 languages.** Not with a single frontier model. With a platform that makes it possible for thousands of developers and communities to solve it one language at a time.

---

## Technical Prerequisites (What We Need to Build)

### Already Built ✅
- [x] mt-eval-harness: plugin architecture, corpus evaluation, metric plugins
- [x] i18n-rosetta: method plugin system, API method type, CLI
- [x] TranslationProcess protocol: pluggable translation methods
- [x] CRK pipeline: proof-of-concept decomposed architecture with FST gates
- [x] Export pipeline: harness TestReport → rosetta plugin manifest

### Phase 1: Attestation Layer 🔧
- [ ] `attestation.py` — SHA-256 fingerprint computation (model + prompt + coaching + hooks + config)
- [ ] Corpus identity hashing — SHA-256 of evaluation corpus for score anchoring
- [ ] RunConfig / TestReport integration — fingerprint propagated through pipeline
- [ ] Exported plugin manifest — attestation hash + corpus hash + scores embedded
- [ ] method.json — full attestation record in export artifacts

### Phase 2: Registry Infrastructure 🔮
- [ ] **Registry schema** — JSON specification for method listings (hash, scores, URL, badge, cost, corpus ID)
- [ ] **Attestation endpoint spec** — `/v1/attest` contract for method servers
- [ ] **Consumer handshake** — `X-Expected-Attestation` / `X-Method-Attestation` header protocol
- [ ] **i18n-rosetta client** — registry query, method discovery, attestation verification on response
- [ ] **Registry-hosted execution** — proxy mode for prompt-based methods (Tier 1)
- [ ] **Method registration CLI** — `mt-eval register --registry <url>` for submitting methods

### Phase 3: Verification & Quality 🔮
- [ ] **Sealed Corpus Protocol** — third-party holdout evaluation for benchmark gaming prevention
- [ ] **Community Verification Platform** — structured human evaluation workflow (fluency, adequacy, cultural appropriateness)
- [ ] **Verifier Compensation** — revenue-share model for paid native speaker reviewers
- [ ] **Mystery Shopping** — automated probe-based drift detection for self-hosted methods
- [ ] **Badge System** — automated pass → community reviewed → community verified → authority endorsed

### Phase 4: Developer Tooling 🔮
- [ ] **LocalModelProcess** — TranslationProcess wrapper for local model inference (vllm, ollama, llama.cpp)
- [ ] **Prompt Iteration Mode** — automated prompt variant testing with comparison reporting
- [ ] **Per-Step Evaluation** — independent harness evaluation of each pipeline step for decomposed methods
- [ ] **Fine-Tuning Data Export** — generate SFT training data from successful harness runs
- [ ] **Method Version History** — track attestation fingerprints over time with associated scores

### Phase 5: Ecosystem Growth 🔮
- [ ] **Language community partnerships** — institutional relationships for sealed corpora and verifier pools
- [ ] **Public registry site** — browsable directory with tradeoff visualization (quality vs cost vs speed)
- [ ] **Immutable attestation log** — optional on-chain timestamp of attestation records for public auditability

---

## Notes on Existing CRK Pipeline as Template

The Plains Cree decomposed pipeline is the proof-of-concept for the Tier 2 pattern. Key architectural insights that should be documented as a replicable pattern:

1. **Decomposition is the key**: Don't ask an LLM to translate. Ask it to do ONE specific linguistic task at each step.
2. **Deterministic gates between LLM steps**: The FST is a formal verifier. If your language has a morphological analyzer, use it as a gate. If not, use dictionary membership, grammar rules, or any formal constraint.
3. **Each LLM step has a small, focused prompt** (~4-7KB). This makes fine-tuning viable — the task is narrow enough for a small model.
4. **The dictionary is a lookup table, not a crutch**: Step 2 uses dictionary lookup to constrain lexical selection. The LLM picks from known-good lemmas rather than hallucinating.
5. **Retry with error feedback**: When Step 3 produces an FST-rejected tag string, the pipeline retries with the specific error message. This self-correction loop is the model learning from the gate.
6. **Assembly is the last mile**: After all words are generated deterministically, the LLM's only job is word order. This is the lowest-risk LLM step because all the words are guaranteed valid.

Any language with a morphological analyzer (and many have them — Arapaho, Blackfoot, Inuktitut, Ojibwe, many Bantu languages, Finnish, Turkish, etc.) could use this exact pattern.

---

## Open Questions

> These are documented design tensions that remain unresolved. They should be revisited as the ecosystem matures.

1. **Business model viability**: If the platform doesn't intermediate billing, what's the sustainable revenue model? Listing fees? Premium verification tiers? Grants?

2. **Sealed corpus maintenance**: Who creates and maintains sealed test corpora for languages with no institutional support? Who pays for it before there's API revenue?

3. **Registry-hosted IP risk**: In Model B, the platform holds developer prompts and coaching data. What legal/contractual framework protects the developer? Is open-sourcing the platform code sufficient assurance?

4. **Verification at scale**: Community verification works for 10 methods. What happens with 10,000? How do you maintain verifier quality without bureaucratic overhead?

5. **Benchmark corpus standards**: Should there be a minimum corpus size/quality requirement for registry listing? Who enforces it?

6. **The determined scammer**: Mystery shopping catches lazy cheaters. Community verification catches bad quality over time. But a sophisticated actor serving good translations for probes and bad ones for real traffic remains an unsolved problem without platform-controlled execution or trusted hardware. Is the residual risk acceptable?

---

*Last updated: May 15, 2026*
