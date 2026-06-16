---
sidebar_position: 4
title: "Contribuindo com Computação"
description: "Doe seus tokens: execute sweeps de benchmark abertos da fila pública com sua própria chave de API e publique os resultados."
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
# Contribuindo Computação

> **A ideia:** o leaderboard tem quadrados vazios — combinações (par de idiomas, modelo, condição) que ninguém mediu ainda. Mantemos uma fila pública delas. Você executa itens com sua própria chave de API, publica os relatórios, e o mapa se preenche. "Doando tokens" é uma contribuição real e citável para avaliação de MT em idiomas de baixos recursos.

## A fila

A fila ao vivo é publicada em [champollion.dev/queue.json](https://champollion.dev/queue.json), e há um visualizador de terminal sem instalação:

```bash
curl -fsSL champollion.dev/queue | bash
```

O visualizador apenas *exibe* itens abertos e seus comandos `mt-eval run` exatos — nunca executa nada ou gasta seus tokens. Cada item carrega:

- `run_command` — pronto para copiar e colar (busca o corpus, executa o harness)
- `est_cost_usd` e `est_basis` — seja o custo **observado** de nossa própria execução de baseline da mesma (corpus, modelo), ou uma **extrapolação** do custo médio por entrada do sweep desse modelo × a contagem de entradas do corpus. A base é informada por item; seu custo real depende do preço do provedor no momento da execução.
- `priority` — pares de idiomas não cobertos primeiro, pares de baixos recursos primeiro (tamanho do corpus é o proxy), naive antes de coached, modelo mais barato primeiro.

**Sem bloqueio de reivindicação — escolha qualquer item aberto.** Duas pessoas executando o mesmo item é inofensivo por design: cada cartão de execução é fingerprinted (SHA-256 sobre hash do dataset + modelo + condição + system prompt, [Benchmark Spec §3.8](/docs/specifications/benchmark)), então execuções idênticas se deduplicam na publicação, e replicações independentes da mesma configuração são evidência útil, não desperdício.

Os corpora enfileirados são dev-split, CC-BY-family (derivados de Tatoeba), e sinalizados `do_not_train` — são conjuntos de avaliação, não dados de treinamento. Corpora com licenças não comerciais e em quarentena são excluídos da fila aberta.

## Configuração (uma vez)

```bash
# 1. Install the harness (python3 + pipx, no sudo — read it first if you like)
curl -fsSL champollion.dev/harness | bash

# 2. Set your API key
export OPENROUTER_API_KEY="sk-or-..."     # or put it in a local .env file
```

### Qual chave de provedor?

O harness roteia **todas** as chamadas de modelo através do [OpenRouter](https://openrouter.ai/keys). Uma `OPENROUTER_API_KEY` alcança cada modelo no lineup da fila — modelos Anthropic Claude, OpenAI GPT e Google Gemini — e o rastreamento de custo do harness e snapshots de preços vêm dos mesmos metadados do OpenRouter, então o custo de execução relatado corresponde ao que sua chave foi cobrada.

Se seus créditos estão com Anthropic, OpenAI ou Google diretamente: o harness **não** aceita atualmente chaves de provedor direto. O schema do cartão de execução reserva um campo `api_provider` para o dia em que aceitar, mas hoje toda execução do harness é uma execução do OpenRouter. Criar uma conta OpenRouter e financiá-la (ou anexar sua própria conta de provedor onde o OpenRouter suporta) é o caminho suportado.

### O caminho rápido do agente

Se você trabalha com Claude Code ou outro agente de codificação, toda a contribuição é um prompt:

```text
Install the Champollion mt-eval harness (curl -fsSL champollion.dev/harness | bash).
Fetch https://champollion.dev/queue.json and show me the top 3 open items.
Using my OpenRouter key (OPENROUTER_API_KEY), execute the run_command of the
item I pick, then run `mt-eval publish` on the generated report JSON and
show me the published run card.
```

## Tier 1 — Executar um benchmark

O `run_command` de cada item da fila é autossuficiente. Um típico:

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/eng-yor-dev-v1.json
mt-eval run --corpus eng-yor-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Yoruba"
```

A execução imprime seu custo total e escreve um log de execução mais um relatório pontuado em `eval/logs/`. Depois publique:

```bash
mt-eval publish eval/logs/harness/run_..._report.json
```

Publicar o assina via OAuth (seu nome se torna a atribuição do leaderboard) e faz upsert do cartão de execução. Submissões da comunidade chegam no nível de confiança **self-benchmarked** — claramente rotulado como "enviado pela pessoa que o executou." Isso não é uma degradação; é o modelo de confiança funcionando. O cartão de execução carrega tudo o que é necessário para qualquer um re-executar sua configuração exata: hash do dataset, modelo, condição, o system prompt completo e custo. Tiers elevados (verificação, validação da comunidade) são concedidos por revisão — veja [Leaderboard Rules](/docs/leaderboard/rules).

## Tier 2 — Criar prompts coached

O harness tem suporte de primeira classe para **coaching**: substitua o system prompt naive por um que carregue conhecimento linguístico real. Passe `--coaching-file` (ou `--coaching "inline text"` para prompts curtos) e o harness usa seu texto como system prompt, registra o **texto completo mais seu SHA-256** no bloco de provenance do log de execução, e rotula a condição da execução como **`coached`** (a menos que você defina `--prompt` explicitamente) — então o craft de prompt é um experimento reproduzível e atribuível, dois arquivos de coaching diferentes nunca podem ser confundidos um com o outro, e execuções coached nunca são confundidas com baselines naive no leaderboard.

Um exemplo prático para Faroês, usando fatos de tipologia e entradas de glossário do [cartão de idioma público](https://champollion.dev/languages) do idioma:

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

(Escreva seu próprio conteúdo de coaching — os fatos acima ilustram a *forma*: algumas regras gramaticais de alto impacto, um pequeno glossário de termos que o modelo erra, uma instrução de registro. Cartões de idioma em [champollion.dev/languages](https://champollion.dev/languages) citam fontes de tipologia das quais você pode extrair.)

Compare contra o baseline naive com `mt-eval compare <naive_log> <coached_log>`, itere e publique sua melhor execução. A execução publica com condição `coached` automaticamente; se você quer que o leaderboard mostre um método nomeado em vez do rótulo genérico, anexe um cartão de método quando publicar (o fluxo de publicação oferece um assistente). Vencer o baseline naive em um par de baixos recursos com nada além de engenharia de prompt é uma descoberta genuína e publicável — veja o [cookbook completo de Coached LLM Prompting](/docs/tutorials/coached-llm-prompting) para orientação de design.

## Tier 3 — Construir um método

A contribuição mais ambiciosa: implemente o protocolo `TranslationMethod` (`translate(entries, config)`) e faça benchmark de um sistema real, não apenas um prompt. O harness o executa via `--method <plugin-dir>` e incorpora seu cartão de método no cartão de execução. Padrões com cookbooks práticos:

- **[FST-gated pipelines](/docs/tutorials/fst-gated-pipeline)** — cada palavra candidata é verificada por um analisador morfológico; o LLM regenera até que o gate passe. Saída semi-determinística, com morfologia garantida.
- **[Dictionary-augmented generation](/docs/tutorials/dictionary-augmented-llm)** — procure termos de origem em um léxico bilíngue no momento da tradução e restrinja a saída.
- [Chained models](/docs/tutorials/chained-models), [few-shot retrieval](/docs/tutorials/few-shot-prompting), [back-translation](/docs/tutorials/back-translation), [rule-based hybrids](/docs/tutorials/rule-based-hybrid)…

Métodos declaram uma **dependency class** (S/O/A1/A2/X — veja [the methods spec](/docs/specifications/methods#method-validity-and-dependency-classes)) descrevendo o que precisam para executar e transferir: um pipeline autossuficiente é Class S; um que chama uma API de dicionário licenciado em tempo de execução é A2. Declare honestamente — a classe determina onde seu método pode competir, e manifestos são auditados.

## Por que isso importa além do leaderboard

Cada execução publicada é evidência independente sobre qualidade de MT para um par de idiomas que provedores comerciais não medem. A fila funciona também como um registro público de *demanda*: quais pares a comunidade considera digno de medir, qual cobertura custa aos preços atuais de API, e até onde a computação doada se estende. Quando pedimos a agências de financiamento para subsidiar sweeps sistemáticos, essa fila e sua taxa de preenchimento são a evidência de demanda.