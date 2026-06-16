---
sidebar_position: 1
title: "Enviar um Método"
related:
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
    note: "The contract your method implements"
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
    note: "What every published run must disclose"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Cookbook: Few-Shot Prompting"
    to: /docs/tutorials/few-shot-prompting
    kind: cookbook
    note: "The fastest first method to submit"
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
---
# Enviar um Método

> **Resumo Executivo.** Um guia passo a passo para enviar sua primeira execução de benchmark para o leaderboard. Clone o harness, execute-o contra um dataset, revise seu run card e envie. Leva 10 minutos se você tiver uma chave de API.

Este guia o orienta através do envio de sua primeira execução de benchmark para o leaderboard do MT Eval Arena.

---

## Pré-requisitos

- **Python 3.10+**
- **Uma chave de API OpenRouter** (ou equivalente para seu provedor de modelo)
- **Um método de tradução** — qualquer coisa que produza traduções a partir de um texto de origem

```bash
# Clone the eval harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install sacrebleu aiohttp
```

---

## Etapa 1: Execute o Harness

O harness avalia seu método contra um dataset padronizado:

```bash
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model gemini-pro \
  --condition your-method-name \
  --temperature 0.2
```

| Flag | O que faz |
|---|---|
| `--corpus` | Caminho para o corpus de avaliação (`.json`, `.jsonl`, `.tsv`) |
| `--model` | Slug do modelo — alias curto (ex. `gemini-pro`) ou ID OpenRouter completo |
| `--condition` | Rótulo para seu método (aparece no leaderboard) |
| `--temperature` | Temperatura de amostragem (menor = mais determinístico) |
| `--fst-retries` | Opcional: número de tentativas de retry FST |
| `--submit` | Enviar automaticamente o run card para o leaderboard |

O harness produz um **run card** — um arquivo JSON autossuficiente com suas pontuações, o hash do dataset, o slug do modelo e uma impressão digital criptográfica vinculando resultados à configuração exata do experimento.

---

## Etapa 2: Revise Seu Run Card

Run cards são salvos em `results/`. Inspecione o seu antes de enviar:

```bash
cat results/your-run-card.json | python -m json.tool
```

Campos-chave para verificar:
- `scores.chrf_plus_plus` — sua métrica de qualidade primária
- `scores.exact_match_rate` — proporção de traduções perfeitas
- `scores.fst_acceptance_rate` — validade morfológica (se FST foi usado)
- `totals.total_cost_usd` — o que a execução custou
- `fingerprint` — o hash de reprodutibilidade do experimento

Veja a [Especificação do Run Card](/docs/specifications/run-card) para o schema completo.

---

## Etapa 3: Envie

### Envio automático

Se você passou `--submit` ao executar o harness, seu run card já foi enviado.

### Envio manual

Envie qualquer run card via API:

```bash
curl -X POST https://mtevalarena.org/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @results/your-run-card.json
```

Ou faça upload através da [Interface do Leaderboard](https://champollion.dev/leaderboard).

---

## O que Acontece Depois

1. Seu envio é validado (hash do dataset, integridade do run card)
2. Os resultados aparecem no leaderboard como **Self-benchmarked** (nível de confiança 1)
3. Para obter status **GDS Verified**, envie seu método como um plugin instalável para que os mantenedores possam reproduzir seus resultados
4. Para métodos de línguas indígenas: se seu método chegar ao topo, o processo de [transferência de propriedade](/docs/sovereignty/ownership-transfer) começa

---

## Veja Também

- [Uso do Harness](/docs/specifications/harness) — referência CLI completa
- [Regras do Leaderboard](/docs/leaderboard/rules) — critérios de envio e políticas anti-gaming
- [Construindo um Método](/docs/specifications/methods) — o protocolo TranslationMethod
- [Datasets](/docs/leaderboard/datasets) — datasets de avaliação disponíveis