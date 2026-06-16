---
sidebar_position: 4
title: "Rechenleistung beitragen"
description: "Spenden Sie Ihre Tokens: Führen Sie offene Benchmark-Durchläufe aus der öffentlichen Warteschlange mit Ihrem eigenen API-Schlüssel aus und veröffentlichen Sie die Ergebnisse."
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
# Rechenleistung beitragen

> **Die Idee:** Das Leaderboard hat leere Felder — Kombinationen aus (Sprachpaar, Modell, Bedingung), die noch niemand gemessen hat. Wir pflegen eine öffentliche Warteschlange dafür. Sie führen Einträge mit Ihrem eigenen API-Schlüssel aus, veröffentlichen die Berichte, und die Karte füllt sich. „Tokens spenden" ist ein echter, zitierfähiger Beitrag zur Evaluierung von MT für ressourcenarme Sprachen.

## Die Warteschlange

Die aktuelle Warteschlange wird unter [champollion.dev/queue.json](https://champollion.dev/queue.json) veröffentlicht, und es gibt einen Terminal-Viewer ohne Installation:

```bash
curl -fsSL champollion.dev/queue | bash
```

Der Viewer *zeigt* lediglich offene Einträge und ihre exakten `mt-eval run`-Befehle an — er führt niemals etwas aus und verbraucht keine Ihrer Tokens. Jeder Eintrag enthält:

- `run_command` — bereit zum Kopieren und Einfügen (ruft den Korpus ab, führt das Harness aus)
- `est_cost_usd` und `est_basis` — entweder die **beobachteten** Kosten unseres eigenen Baseline-Laufs desselben (Korpus, Modell) oder eine **Hochrechnung** aus den durchschnittlichen Sweep-Kosten dieses Modells pro Eintrag × der Anzahl der Korpus-Einträge. Die Grundlage wird je Eintrag angegeben; Ihre tatsächlichen Kosten hängen von der Anbieter-Preisgestaltung zur Laufzeit ab.
- `priority` — zuerst nicht abgedeckte Sprachpaare, zuerst die ressourcenärmsten Paare (die Korpusgröße dient als Näherungswert), naive vor coached, günstigstes Modell zuerst.

**Keine Claim-Sperre — wählen Sie einen beliebigen offenen Eintrag.** Dass zwei Personen denselben Eintrag ausführen, ist konstruktionsbedingt unschädlich: Jede Run-Card erhält einen Fingerabdruck (SHA-256 über Datensatz-Hash + Modell + Bedingung + System-Prompt, [Benchmark Spec §3.8](/docs/specifications/benchmark)), sodass identische Läufe bei der Veröffentlichung dedupliziert werden und unabhängige Replikationen derselben Konfiguration nützliche Belege darstellen, keine Verschwendung.

Die Korpora in der Warteschlange stammen aus dem Dev-Split, gehören zur CC-BY-Familie (Tatoeba-abgeleitet) und sind als `do_not_train` gekennzeichnet — es handelt sich um Evaluierungssätze, nicht um Trainingsdaten. Nicht kommerziell lizenzierte und unter Quarantäne gestellte Korpora sind von der offenen Warteschlange ausgeschlossen.

## Einrichtung (einmalig)

```bash
# 1. Install the harness (python3 + pipx, no sudo — read it first if you like)
curl -fsSL champollion.dev/harness | bash

# 2. Set your API key
export OPENROUTER_API_KEY="sk-or-..."     # or put it in a local .env file
```

### Welcher Anbieter-Schlüssel?

Das Harness leitet **alle** Modellaufrufe über [OpenRouter](https://openrouter.ai/keys). Ein `OPENROUTER_API_KEY` erreicht jedes Modell im Lineup der Warteschlange — Anthropic Claude, OpenAI GPT und Google Gemini gleichermaßen — und die Kostenverfolgung sowie die Preis-Snapshots des Harness stammen aus denselben OpenRouter-Metadaten, sodass die berichteten Laufkosten dem entsprechen, was Ihrem Schlüssel in Rechnung gestellt wurde.

Falls Ihre Credits direkt bei Anthropic, OpenAI oder Google liegen: Das Harness akzeptiert derzeit **keine** direkten Anbieter-Schlüssel. Das Run-Card-Schema reserviert ein `api_provider`-Feld für den Tag, an dem dies möglich sein wird, doch heute ist jeder Harness-Lauf ein OpenRouter-Lauf. Ein OpenRouter-Konto zu erstellen und aufzuladen (oder Ihr eigenes Anbieter-Konto anzubinden, sofern OpenRouter dies unterstützt) ist der unterstützte Weg.

### Der schnelle Weg über den Agenten

Wenn Sie mit Claude Code oder einem anderen Coding-Agenten arbeiten, besteht der gesamte Beitrag aus einem einzigen Prompt:

```text
Install the Champollion mt-eval harness (curl -fsSL champollion.dev/harness | bash).
Fetch https://champollion.dev/queue.json and show me the top 3 open items.
Using my OpenRouter key (OPENROUTER_API_KEY), execute the run_command of the
item I pick, then run `mt-eval publish` on the generated report JSON and
show me the published run card.
```

## Stufe 1 — Einen Benchmark ausführen

Der `run_command` jedes Warteschlangen-Eintrags ist eigenständig. Ein typisches Beispiel:

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/eng-yor-dev-v1.json
mt-eval run --corpus eng-yor-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Yoruba"
```

Der Lauf gibt seine Gesamtkosten aus und schreibt ein Run-Log sowie einen bewerteten Bericht nach `eval/logs/`. Anschließend veröffentlichen Sie:

```bash
mt-eval publish eval/logs/harness/run_..._report.json
```

Beim Veröffentlichen werden Sie per OAuth angemeldet (Ihr Name wird zur Leaderboard-Zuordnung) und die Run-Card wird per Upsert eingefügt. Community-Einreichungen landen auf der Vertrauensstufe **self-benchmarked** — klar gekennzeichnet als „eingereicht von der Person, die den Lauf durchgeführt hat". Das ist keine Herabstufung; es ist das funktionierende Vertrauensmodell. Die Run-Card enthält alles, was nötig ist, damit jede Person Ihre exakte Konfiguration erneut ausführen kann: Datensatz-Hash, Modell, Bedingung, den vollständigen System-Prompt und die Kosten. Höhere Stufen (Verifizierung, Community-Validierung) werden durch Prüfung vergeben — siehe [Leaderboard Rules](/docs/leaderboard/rules).

## Stufe 2 — Coached Prompts erstellen

Das Harness unterstützt **Coaching** als erstklassige Funktion: Ersetzen Sie den naiven System-Prompt durch einen, der echtes linguistisches Wissen trägt. Übergeben Sie `--coaching-file` (oder `--coaching "inline text"` für kurze Prompts), und das Harness verwendet Ihren Text als System-Prompt, hält den **vollständigen Text samt SHA-256** im Provenienz-Block des Run-Logs fest und kennzeichnet die Bedingung des Laufs als **`coached`** (sofern Sie nicht explizit `--prompt` setzen) — sodass die Prompt-Gestaltung ein reproduzierbares, zuordenbares Experiment ist, zwei verschiedene Coaching-Dateien niemals miteinander verwechselt werden können und coached Läufe auf dem Leaderboard niemals mit naiven Baselines verwechselt werden.

Ein durchgearbeitetes Beispiel für Färöisch unter Verwendung von Typologie-Fakten und Glossar-Einträgen aus der [öffentlichen Language Card](https://champollion.dev/languages) der Sprache:

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

(Verfassen Sie Ihre eigenen Coaching-Inhalte — die obigen Fakten veranschaulichen die *Form*: einige wirkungsstarke Grammatikregeln, ein kleines Glossar mit Begriffen, die das Modell falsch übersetzt, eine Registeranweisung. Die Language Cards unter [champollion.dev/languages](https://champollion.dev/languages) zitieren Typologie-Quellen, aus denen Sie schöpfen können.)

Vergleichen Sie mit der naiven Baseline über `mt-eval compare <naive_log> <coached_log>`, iterieren Sie und veröffentlichen Sie Ihren besten Lauf. Der Lauf wird automatisch mit der Bedingung `coached` veröffentlicht; falls das Leaderboard statt der generischen Bezeichnung eine benannte Methode anzeigen soll, hängen Sie beim Veröffentlichen eine Method Card an (der Veröffentlichungs-Workflow bietet einen Assistenten dafür). Die naive Baseline bei einem ressourcenarmen Paar allein durch Prompt-Engineering zu schlagen, ist ein echter, veröffentlichungswürdiger Befund — siehe das vollständige [Coached LLM Prompting cookbook](/docs/tutorials/coached-llm-prompting) für Gestaltungshinweise.

## Stufe 3 — Eine Methode entwickeln

Der ehrgeizigste Beitrag: Implementieren Sie das `TranslationMethod`-Protokoll (`translate(entries, config)`) und benchmarken Sie ein tatsächliches System, keinen Prompt. Das Harness führt es über `--method <plugin-dir>` aus und bettet Ihre Method Card in die Run-Card ein. Muster mit durchgearbeiteten Cookbooks:

- **[FST-gated pipelines](/docs/tutorials/fst-gated-pipeline)** — jedes Kandidatenwort wird von einem morphologischen Analysator geprüft; das LLM generiert so lange neu, bis das Gate passiert wird. Semi-deterministische, morphologisch garantierte Ausgabe.
- **[Dictionary-augmented generation](/docs/tutorials/dictionary-augmented-llm)** — schlagen Sie Quellbegriffe zur Übersetzungszeit in einem zweisprachigen Lexikon nach und beschränken Sie die Ausgabe.
- [Chained models](/docs/tutorials/chained-models), [few-shot retrieval](/docs/tutorials/few-shot-prompting), [back-translation](/docs/tutorials/back-translation), [rule-based hybrids](/docs/tutorials/rule-based-hybrid)…

Methoden deklarieren eine **Abhängigkeitsklasse** (S/O/A1/A2/X — siehe [the methods spec](/docs/specifications/methods#method-validity-and-dependency-classes)), die beschreibt, was sie zur Ausführung und Übertragung benötigen: Eine eigenständige Pipeline ist Klasse S; eine, die zur Laufzeit eine lizenzierte Wörterbuch-API aufruft, ist A2. Deklarieren Sie ehrlich — die Klasse bestimmt, wo Ihre Methode antreten kann, und die Manifeste werden geprüft.

## Warum dies über das Leaderboard hinaus von Bedeutung ist

Jeder veröffentlichte Lauf ist ein unabhängiger Beleg für die MT-Qualität eines Sprachpaars, das kommerzielle Anbieter nicht messen. Die Warteschlange dient zugleich als öffentlicher Nachweis der *Nachfrage*: welche Paare die Community für messenswert hält, was Abdeckung zu aktuellen API-Preisen kostet und wie weit gespendete Rechenleistung reicht. Wenn wir Förderinstitutionen darum bitten, systematische Sweeps zu finanzieren, sind diese Warteschlange und ihre Erfüllungsrate der Nachweis der Nachfrage.