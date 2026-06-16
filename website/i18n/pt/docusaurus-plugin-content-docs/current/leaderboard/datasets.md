---
sidebar_position: 3
title: "Conjuntos de Dados de Avaliação"
related:
  - label: "Corpus Design Framework"
    to: /docs/specifications/corpus-design
    kind: spec
    note: "How evaluation corpora are constructed"
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "Build a corpus for your language"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
---
# Conjuntos de Dados de Avaliação

> **Resumo Executivo.** Esta página descreve os conjuntos de dados de avaliação disponíveis para benchmarking, incluindo o esquema de entrada do corpus, níveis de dificuldade (1–5) e requisitos de proveniência. Atualmente disponíveis: EDTeKLA Dev v1 (Cree das Planícies, 548 entradas totais: 486 de livro didático + 62 padrão ouro) e FLORES+ Devtest (39 idiomas, 1.012 entradas cada).

Conjuntos de dados são os alvos fixos contra os quais o harness é executado. Cada conjunto de dados é um arquivo JSON contendo pares origem→alvo com referências padrão ouro. O harness pontua as saídas do modelo contra essas referências — nunca as modifica.

:::danger NÃO TREINE com dados de avaliação

⚠️ **Estes conjuntos de dados são apenas para avaliação.** Métodos treinados, ajustados, com prompts de poucos exemplos ou de outra forma expostos a dados de avaliação produzirão pontuações artificialmente inflacionadas e serão **desqualificados do leaderboard.**

Use corpora separados para treinamento. Conjuntos de avaliação devem permanecer invisíveis para seu modelo durante o desenvolvimento.
:::

---

## Formato do Conjunto de Dados

Todo conjunto de dados segue o mesmo esquema JSON:

```json
{
  "dataset": {
    "id": "dataset-slug",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "description": "Human-readable description of the dataset",
    "source_language": "en",
    "target_language": "crk",
    "created": "2025-05-01",
    "license": "CC-BY-NC-4.0",
    "provenance": ["gold_standard", "textbook"]
  },
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "tânisi",
      "difficulty": 1,
      "provenance": "gold_standard",
      "register": "conversational",
      "context": "greeting",
      "notes": "Common greeting, SRO orthography"
    }
  ]
}
```

:::info Esquema Canônico
A [Especificação de Benchmark](/docs/specifications/benchmark) define o corpus canônico e o esquema de entrada. Esta página documenta os conjuntos de dados disponíveis e como criar novos.
:::

### Bloco `dataset` de Nível Superior

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | `string` | Identificador único do conjunto de dados (usado em cartões de execução e leaderboard) |
| `version` | `string` | Versão semântica. Incrementar isso invalida comparações de cartões de execução anteriores |
| `language_pair` | `string` | Rótulo de exibição (ex: `EN→CRK`) |
| `description` | `string` | Opcional. Resumo legível por humanos |
| `source_language` | `string` | Código de idioma de origem BCP 47 |
| `target_language` | `string` | Código de idioma de destino BCP 47 |
| `created` | `string` | Data de criação ISO 8601 |
| `license` | `string` | Identificador de licença SPDX |
| `provenance` | `string[]` | Lista de tags de proveniência usadas em todas as entradas |

### Campos de Entrada

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|------------|-----------|
| `id` | `integer` | ✅ | Identificador único de entrada dentro do corpus |
| `source` | `string` | ✅ | O texto de origem a traduzir |
| `reference` | `string` | ✅ | A tradução de referência padrão ouro |
| `difficulty` | `integer` | ✅ | Nível de dificuldade 1–5 (veja abaixo) |
| `provenance` | `string` | ✅ | Origem desta entrada (ex: `gold_standard`, `textbook`, `elicited`) |
| `register` | `string` | ✅ | Nível de registro/formalidade (ex: `conversational`, `formal`, `ceremonial`) |
| `context` | `string` | ✅ | Função comunicativa (ex: `greeting`, `declaration`, `instruction`) |
| `notes` | `string` | ❌ | Contexto opcional para revisores humanos |
| `morphological_analysis` | `string` | ❌ | Análise morfológica padrão ouro |
| `variant_class` | `string` | ❌ | Rótulo de classe agrupando variantes de tradução aceitáveis |

---

## Conjuntos de Dados Disponíveis

### Conjunto de Desenvolvimento EDTeKLA v1

O primeiro conjunto de dados de avaliação, construído para tradução de Inglês→Cree das Planícies (SRO). Criado pelo [grupo de pesquisa EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) da Universidade de Alberta.

| Propriedade | Valor |
|-------------|-------|
| **ID** | `edtekla-dev-v1` |
| **Versão** | `1.0` |
| **Par de idiomas** | EN → CRK (Cree das Planícies, ortografia SRO) |
| **Contagem de entradas** | 548 total (486 de livro didático + 62 padrão ouro). O corpus dev canônico é `textbook_dev.json` (436 entradas — a divisão dev completa do livro didático de 486 total: 436 dev + 50 teste retido) |
| **Distribuição de dificuldade** | Fácil, Médio, Difícil |
| **Proveniência** | `gold_standard` (verificado por falantes), `textbook` (materiais educacionais publicados) |
| **Licença** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |

**O que testa:**

- Saudações básicas e frases comuns
- Animacidade de nomes e obviação
- Conjugação verbal entre pessoas e tempos
- Construções locativas
- Paradigmas possessivos
- Estruturas de sentenças complexas

:::tip Estrutura do corpus
A coleção completa EdTeKLA tem 548 entradas curadas: 486 do corpus de livro didático (436 dev + 50 retido) e 62 do padrão ouro itwêwina. O corpus dev canônico é `textbook_dev.json` com 436 entradas — a divisão dev completa do livro didático. Cada entrada foi verificada por falantes fluentes ou obtida de livros didáticos de idioma Cree publicados. Um conjunto de dados menor e de alta qualidade com padrões ouro verificados é mais útil do que um grande e ruidoso — especialmente para um idioma de poucos recursos onde traduções "aproximadas" são frequentemente morfologicamente inválidas.
:::

---

## Criando um Novo Conjunto de Dados

Para criar um conjunto de dados para um novo par de idiomas ou domínio:

### 1. Estruture o JSON

Siga o esquema [Formato do Conjunto de Dados](#formato-do-conjunto-de-dados). Cada entrada deve ter `source`, `reference`, `difficulty`, `provenance`, `register` e `context`.

### 2. Atribua um ID único

Use um slug descritivo: `{project}-{split}-v{version}` (ex: `edtekla-dev-v1`, `quechua-test-v1`).

### 3. Verifique padrões ouro

Todo valor `reference` deve ser verificado por um falante fluente ou obtido de um recurso publicado e revisado por pares. Referências geradas por máquina derrotam o propósito da avaliação.

### 4. Defina níveis de dificuldade

Atribua a cada entrada um nível de dificuldade inteiro:

| Nível | Descrição | Exemplos |
|-------|-----------|----------|
| 1 — Vocabulário básico | Palavras isoladas, saudações comuns, números | "hello" → "tânisi" |
| 2 — Sentenças simples | Sujeito-verbo ou SVO, tempo presente | "I see the dog" |
| 3 — Complexidade moderada | Tempo passado/futuro, possessivos, animacidade | "I saw his dog yesterday" |
| 4 — Morfologia complexa | Obviação, voz passiva, ordem conjunta | "the woman whose son went to the store" |
| 5 — Avançado | Multi-cláusula, registro formal, cerimonial, idiomático | Parágrafo completo com tom apropriado ao registro |

### 5. Marque proveniência

Cada entrada deve indicar de onde veio. Tags comuns:

- `gold_standard` — Verificado por falantes fluentes
- `textbook` — De materiais educacionais publicados
- `elicited` — Produzido através de sessões de elicitação estruturada
- `corpus` — Extraído de um corpus paralelo

### 6. Valide o arquivo

Execute o harness contra seu conjunto de dados com qualquer modelo para verificar se o JSON está bem formado e todos os campos obrigatórios estão presentes:

```bash
python eval/baseline_experiment.py --dataset path/to/your-dataset.json
```

O harness gerará erro em campos ausentes, índices duplicados ou violações de esquema.

### 7. Envie para inclusão

Abra um pull request contra o [repositório do harness de avaliação](https://github.com/gamedaysuits/arena) com seu arquivo de conjunto de dados no diretório `data/`. Inclua documentação de sua metodologia de verificação e fontes de proveniência.

---

## FLORES+ Devtest

Um benchmark multilíngue de cobertura ampla mantido pela [Open Language Data Initiative (OLDI)](https://huggingface.co/datasets/openlanguagedata/flores_plus). Usado para o benchmark de fronteira multi-modelo do champollion.

| Propriedade | Valor |
|-------------|-------|
| **ID** | `flores-plus-devtest` |
| **Pares de idiomas** | EN → 39 idiomas (todos os idiomas naturais registrados do champollion) |
| **Contagem de entradas** | 1.012 sentenças por idioma |
| **Licença** | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| **Fonte** | Originalmente Meta FLORES-200, agora mantido por OLDI |
| **Localização** | Fixtures pré-extraídos em `test/benchmark/fixtures/` no repositório principal do champollion |

:::danger Apenas para avaliação
FLORES+ é destinado exclusivamente para avaliação. Os curadores explicitamente solicitam que **não seja usado como dados de treinamento**. Garanta que seu conteúdo seja excluído de qualquer corpus de treinamento.
:::

---

## Veja Também

- [Avaliação de TA](/docs/leaderboard/rules) — visão geral do framework de avaliação e leaderboard
- [Eval Harness](/docs/specifications/harness) — como executar avaliações contra estes conjuntos de dados
- [Especificação de Cartão de Execução](/docs/specifications/run-card) — o esquema JSON para registrar resultados
- [Leaderboard de Métodos](https://champollion.dev/leaderboard) — pontuações de benchmark ao vivo
- [Projeto EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) — o grupo de pesquisa da Universidade de Alberta por trás do conjunto de dados Cree