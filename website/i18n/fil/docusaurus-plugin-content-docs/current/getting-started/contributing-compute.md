---
sidebar_position: 4
title: "Pag-aambag ng Compute"
description: "I-donate ang inyong mga token: magpatakbo ng open benchmark sweeps mula sa public queue gamit ang sarili ninyong API key at i-publish ang mga resulta."
related:
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
  - label: "Cookbook: Coached LLM Prompting"
    to: /docs/tutorials/coached-llm-prompting
    kind: cookbook
  - label: "Cookbook: FST-Gated Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "Method Interface & Dependency Classes"
    to: /docs/specifications/methods
    kind: spec
  - label: "Leaderboard Rules & Trust Tiers"
    to: /docs/leaderboard/rules
    kind: guide
---
# Pag-aambag ng Compute

> **Ang ideya:** may mga bakanteng parisukat ang leaderboard — mga kombinasyong (language pair, model, condition) na wala pang nakasusukat. Nagpapanatili kami ng pampublikong queue para sa mga ito. Pinapatakbo ninyo ang mga item gamit ang sarili ninyong API key, inilalathala ang mga report, at napupunan ang mapa. Ang "pagdo-donate ng tokens" ay tunay at nasisipi na ambag sa low-resource MT evaluation.

## Ang queue

Ang live queue ay inilalathala sa [champollion.dev/queue.json](https://champollion.dev/queue.json), at may zero-install terminal viewer:

```bash
curl -fsSL champollion.dev/queue | bash
```

Ang viewer ay *nagpapakita* lamang ng mga bukas na item at ng eksaktong mga command na `mt-eval run` ng mga ito — hindi ito kailanman nagpapatakbo ng anuman o gumagastos ng inyong tokens. Bawat item ay may:

- `run_command` — handa nang i-copy-paste (kinukuha ang corpus, pinapatakbo ang harness)
- `est_cost_usd` at `est_basis` — alinman sa **naobserbahang** gastos ng sarili naming baseline run ng parehong (corpus, model), o isang **extrapolation** mula sa sweep-average cost per entry ng model na iyon × bilang ng entry sa corpus. Isinasaad ang batayan sa bawat item; nakadepende ang aktuwal ninyong gastos sa provider pricing sa oras ng run.
- `priority` — unang inuuna ang mga hindi pa nasasaklaw na language pair, unang inuuna ang lowest-resource pairs (ang corpus size ang proxy), naive bago coached, pinakamurang model muna.

**Walang claim-locking — pumili ng anumang bukas na item.** Hindi nakasasama kung dalawang tao ang magpatakbo ng parehong item ayon sa disenyo: bawat run card ay may fingerprint (SHA-256 sa dataset hash + model + condition + system prompt, [Espesipikasyon ng Benchmark §3.8](/docs/specifications/benchmark)), kaya ang magkaparehong run ay nade-deduplicate sa pag-publish, at ang mga independent replication ng parehong configuration ay kapaki-pakinabang na ebidensiya, hindi sayang.

Ang mga queued corpora ay dev-split, CC-BY-family (Tatoeba-derived), at naka-flag bilang `do_not_train` — mga evaluation set ang mga ito, hindi training data. Hindi isinasama sa open queue ang mga corpus na may non-commercial license at naka-quarantine.

## Setup (isang beses)

```bash
# 1. Install the harness (python3 + pipx, no sudo — read it first if you like)
curl -fsSL champollion.dev/harness | bash

# 2. Set your API key
export OPENROUTER_API_KEY="sk-or-..."     # or put it in a local .env file
```

### Aling provider key?

Irinu-route ng harness ang **lahat** ng model call sa pamamagitan ng [OpenRouter](https://openrouter.ai/keys). Isang `OPENROUTER_API_KEY` ang umaabot sa bawat model sa lineup ng queue — Anthropic Claude, OpenAI GPT, at Google Gemini models — at ang cost tracking at pricing snapshots ng harness ay nagmumula sa parehong OpenRouter metadata, kaya tumutugma ang iniulat na run cost sa siningil sa inyong key.

Kung nasa Anthropic, OpenAI, o Google mismo ang inyong credits: kasalukuyang **hindi** tumatanggap ang harness ng direct provider keys. Naglalaan ang run-card schema ng field na `api_provider` para sa araw na gagawin nito iyon, ngunit sa ngayon ang bawat harness run ay OpenRouter run. Ang paggawa ng OpenRouter account at paglalagay ng pondo rito (o pag-attach ng sarili ninyong provider account kung sinusuportahan iyon ng OpenRouter) ang suportadong landas.

### Ang mabilis na landas ng agent

Kung nagtatrabaho kayo gamit ang Claude Code o ibang coding agent, isang prompt lang ang buong kontribusyon:

```text
Install the Champollion mt-eval harness (curl -fsSL champollion.dev/harness | bash).
Fetch https://champollion.dev/queue.json and show me the top 3 open items.
Using my OpenRouter key (OPENROUTER_API_KEY), execute the run_command of the
item I pick, then run `mt-eval publish` on the generated report JSON and
show me the published run card.
```

## Tier 1 — Magpatakbo ng benchmark

Self-contained ang `run_command` ng bawat queue item. Isang karaniwan:

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/eng-yor-dev-v1.json
mt-eval run --corpus eng-yor-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Yoruba"
```

Ini-print ng run ang kabuuang gastos nito at nagsusulat ng run log kasama ang scored report sa `eval/logs/`. Pagkatapos ay i-publish:

```bash
mt-eval publish eval/logs/harness/run_..._report.json
```

Kapag nag-publish kayo, magsa-sign in kayo sa pamamagitan ng OAuth (ang inyong pangalan ang magiging attribution sa leaderboard) at ina-upsert ang run card. Ang mga community submission ay napupunta sa **self-benchmarked** trust tier — malinaw na nilalagyan ng label bilang "submitted by the person who ran it." Hindi ito demotion; ito ang trust model na gumagana. Taglay ng run card ang lahat ng kailangan upang muling mapatakbo ng sinuman ang eksakto ninyong configuration: dataset hash, model, condition, ang buong system prompt, at cost. Ibinibigay sa pamamagitan ng review ang mga mas mataas na tier (verification, community validation) — tingnan ang [Mga Panuntunan ng Leaderboard](/docs/leaderboard/rules).

## Tier 2 — Gumawa ng coached prompts

May first-class support ang harness para sa **coaching**: palitan ang naive system prompt ng isang prompt na naglalaman ng tunay na kaalamang lingguwistiko. Ipasa ang `--coaching-file` (o `--coaching "inline text"` para sa maiikling prompt) at gagamitin ng harness ang inyong text bilang system prompt, itatala ang **buong text kasama ang SHA-256 nito** sa provenance block ng run log, at lalagyan ng label na **`coached`** ang condition ng run (maliban kung tahasan ninyong itatakda ang `--prompt`) — kaya ang prompt craft ay isang reproducible at attributable na eksperimento, hindi kailanman mapagkakamalang pareho ang dalawang magkaibang coaching file, at hindi kailanman mapagkakamalang naive baselines ang coached runs sa leaderboard.

Isang worked example para sa Faroese, gamit ang typology facts at glossary entries mula sa [pampublikong language card](https://champollion.dev/languages) ng wika:

```text title="coaching-fao.txt"
You are translating Danish into Faroese (føroyskt).

Grammar notes:
- Faroese is a North Germanic V2 language: the finite verb is the second
  constituent of a main clause.
- Nouns inflect for case (nominative, accusative, dative, genitive),
  gender (masculine, feminine, neuter), and number. Make adjectives and
  determiners agree.
- The skerping pattern applies before -gv/-ggj sequences; preserve
  standard orthography including ð (which is silent).

Glossary (use these exact equivalents):
- language -> mál
- island -> oyggj
- weather -> veður

Style: plain register, modern standard orthography. Output only the
Faroese translation, no commentary.
```

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/dan-fao-dev-v1.json
mt-eval run --corpus dan-fao-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Faroese" \
  --coaching-file coaching-fao.txt
```

(Sumulat kayo ng sarili ninyong coaching content — ipinapakita ng mga fact sa itaas ang *hugis*: ilang high-impact grammar rules, maliit na glossary ng mga terminong madalas pagkakamalian ng model, isang register instruction. Ang mga language card sa [champollion.dev/languages](https://champollion.dev/languages) ay nagbabanggit ng typology sources na maaari ninyong pagkuhanan.)

Ihambing laban sa naive baseline gamit ang `mt-eval compare <naive_log> <coached_log>`, mag-iterate, at i-publish ang pinakamahusay ninyong run. Awtomatikong nailalathala ang run na may condition na `coached`; kung nais ninyong magpakita ang leaderboard ng pinangalanang method sa halip na generic na label, mag-attach ng method card kapag nag-publish kayo (nag-aalok ang publish flow ng wizard). Ang pagtalo sa naive baseline sa isang low-resource pair gamit lamang ang prompt engineering ay tunay at publishable na finding — tingnan ang buong [Coached LLM Prompting cookbook](/docs/tutorials/coached-llm-prompting) para sa gabay sa disenyo.

## Tier 3 — Bumuo ng method

Ang pinakaambisyosong kontribusyon: i-implement ang protocol na `TranslationMethod` (`translate(entries, config)`) at i-benchmark ang isang aktuwal na system, hindi prompt. Pinapatakbo ito ng harness sa pamamagitan ng `--method <plugin-dir>` at ini-embed ang inyong method card sa run card. Mga pattern na may worked cookbooks:

- **[FST-gated pipelines](/docs/tutorials/fst-gated-pipeline)** — sinusuri ng morphological analyzer ang bawat candidate word; nagre-regenerate ang LLM hanggang pumasa ang gate. Semi-deterministic, morphology-guaranteed na output.
- **[Dictionary-augmented generation](/docs/tutorials/dictionary-augmented-llm)** — naghahanap ng source terms sa isang bilingual lexicon sa oras ng translation at nililimitahan ang output.
- [Chained models](/docs/tutorials/chained-models), [few-shot retrieval](/docs/tutorials/few-shot-prompting), [back-translation](/docs/tutorials/back-translation), [rule-based hybrids](/docs/tutorials/rule-based-hybrid)…

Nagdedeklara ang methods ng **dependency class** (S/O/A1/A2/X — tingnan ang [methods spec](/docs/specifications/methods#method-validity-and-dependency-classes)) na naglalarawan kung ano ang kailangan ng mga ito upang tumakbo at ma-transfer: ang self-contained pipeline ay Class S; ang tumatawag sa licensed dictionary API sa runtime ay A2. Magdeklara nang tapat — tinutukoy ng class kung saan maaaring makipagkompetensiya ang inyong method, at ina-audit ang manifests.

## Bakit mahalaga ito lampas sa leaderboard

Bawat published run ay independent evidence tungkol sa kalidad ng MT para sa isang language pair na hindi sinusukat ng commercial providers. Ang queue ay nagsisilbi ring pampublikong tala ng *demand*: aling pairs ang itinuturing ng komunidad na karapat-dapat sukatin, magkano ang coverage sa kasalukuyang API prices, at gaano kalayo ang nararating ng donated compute. Kapag humihiling kami sa funding agencies na pondohan ang systematic sweeps, ang queue na ito at ang fill-rate nito ang ebidensiya ng demand.