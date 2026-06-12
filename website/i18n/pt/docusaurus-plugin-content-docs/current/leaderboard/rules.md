---
sidebar_position: 1
title: "Avaliação de Tradução Automática"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "How the composite score is computed"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Evaluation Datasets"
    to: /docs/leaderboard/datasets
    kind: doc
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "The rules, applied"
---
# Avaliação de MT

> **Resumo Executivo.** Esta página define os critérios de submissão do leaderboard, métricas de pontuação (chrF++, aceitação FST, correspondência exata, correspondência equivalente, pontuação semântica), políticas anti-gaming, níveis de verificação e o fluxo de submissão. Métodos que foram expostos a dados de avaliação são desqualificados.

champollion inclui um framework de avaliação de tradução automática projetado para **benchmarking reproduzível** de métodos de tradução — especialmente para idiomas de baixo recurso e indígenas onde benchmarks padrão de MT não existem e reivindicações de qualidade são difíceis de verificar.

---

## O Leaderboard

A peça central é o **[Method Leaderboard](https://champollion.dev/leaderboard)** — um placar ao vivo, apoiado por Supabase, onde pesquisadores e membros da comunidade submetem e comparam métodos de tradução com avaliação reproduzível e com impressão digital.

Cada submissão inclui:

- **Pipeline com impressão digital** — vinculado a um commit Git específico e hash de configuração, para que os resultados rastreiem até o código exato que os produziu
- **Dataset versionado** — com hash de conteúdo e versionado; pontuações são comparáveis apenas dentro da mesma versão do dataset
- **Métricas padronizadas** — toda pontuação é computada pelo harness de avaliação compartilhado, eliminando diferenças de implementação
- **Níveis de confiança** — auto-avaliado, GDS Verificado ou Validado pela Comunidade
- **Rastreamento de custos** — custo de API por submissão, para que trade-offs custo–qualidade sejam transparentes

O leaderboard atualmente rastreia cinco métricas. Três funcionam para qualquer idioma; duas estão disponíveis para Plains Cree e serão generalizadas conforme expandimos:

| Métrica | Tipo | O Que Mede |
|---------|------|-----------|
| **chrF++** | F-score de n-gramas de caracteres | Métrica de qualidade primária — correlaciona bem com julgamento humano, especialmente para idiomas morfologicamente ricos |
| **Exact Match** | Proporção de correspondências perfeitas | Precisão rigorosa — com que frequência a tradução é exatamente o padrão ouro? |
| **FST Acceptance** | Taxa de aprovação do portão morfológico | Para métodos com verificação de transdutor de estado finito — qual proporção de saídas é morfologicamente válida? |
| **Equivalent Match** | Taxa de variante aceitável | Fração correspondendo à referência ou a uma variante aceitável (ordem de palavras, convenção ortográfica). Atualmente CRK; generalizando. |
| **Semantic Score** | Fidelidade semântica | Preservação de significado — a tradução captura o significado pretendido independentemente da forma de superfície? Atualmente CRK; generalizando. |

:::info Suite Completa de Métricas
A [Especificação de Pontuação](/docs/specifications/scoring) define o inventário completo de 19 métricas em 5 categorias, fórmula de pontuação composta, tabelas de peso e limiares de nível de qualidade.
:::

**[→ Ver o leaderboard](https://champollion.dev/leaderboard)**

---

## Datasets Disponíveis

### EDTeKLA Development Set v1

O primeiro dataset de avaliação, construído para tradução English→Plains Cree (SRO). Criado pelo [grupo de pesquisa EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) da Universidade de Alberta.

| Propriedade | Valor |
|-------------|-------|
| **ID** | `edtekla-dev-v1` |
| **Par de idiomas** | EN → CRK (Plains Cree, ortografia SRO) |
| **Contagem de entradas** | 404 (`master_corpus.json`: 62 ouro + 342 livro didático); 548 total disponível |
| **Licença** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
| **Proveniência** | `gold_standard` (verificado por falantes), `textbook` (materiais educacionais publicados) |

### FLORES+ Devtest — Apenas para Uso em Desenvolvimento

> [!WARNING]
> **FLORES+ está disponível para desenvolvimento e depuração, mas NÃO é usado para avaliação oficial do leaderboard.** FLORES+ (originalmente Meta FLORES-200) é um dataset de benchmark amplamente público que LLMs de fronteira quase certamente foram treinados. Pontuações contra FLORES+ não refletem de forma confiável a qualidade de tradução do mundo real para métodos baseados em LLM. Métodos não-LLM (FST, baseado em regras, NMT fine-tuned) são menos afetados, mas pontuações FLORES+ ainda não são publicadas no leaderboard.

Fixtures FLORES+ permanecem disponíveis em `test/benchmark/fixtures/` para testes de fumaça de pipeline, validação entre idiomas e uso em desenvolvimento. A avaliação oficial usa corpora personalizados construídos a partir de texto escrito por humanos não disponível publicamente em forma paralela.

Veja [Evaluation Datasets](/docs/leaderboard/datasets) para o schema completo do dataset, níveis de dificuldade e como criar o seu próprio.

:::danger NÃO TREINE em dados de avaliação

**Estes datasets são apenas para avaliação.** Métodos treinados, fine-tuned, com prompt de poucos exemplos ou de outra forma expostos a dados de avaliação produzirão pontuações artificialmente inflacionadas e serão **desqualificados do leaderboard.**

Isto não é uma sugestão — é a regra mais importante de integridade de avaliação. Use corpora separados para treinamento. Conjuntos de avaliação devem permanecer invisíveis para seu modelo durante o desenvolvimento.

Se você está usando dados de coaching ou exemplos de poucos exemplos, eles devem vir de **fontes completamente separadas**. Se tiver dúvida, não inclua.
:::

:::warning Não-determinismo de LLM

Saídas de LLM são não-determinísticas. Pontuações representam medições em um ponto no tempo sob versões de modelo específicas e configurações de API. Provedores de modelo podem atualizar pesos, estratégias de decodificação ou filtros de segurança a qualquer momento, o que pode causar desvio de pontuação entre execuções. O leaderboard registra o slug de modelo exato e timestamp para cada submissão.
:::

---

## O Que Faz um Bom Método

Nem todos os métodos são criados iguais. Aqui está o que separa trabalho rigoroso de pontuações inflacionadas.

### Características de um método forte

- **Separação limpa de dados de treinamento e avaliação** — seu método nunca viu o conjunto de avaliação durante desenvolvimento, ajuste, engenharia de prompt ou seleção de exemplos de poucos exemplos
- **Reproduzível** — alguém pode clonar seu repo, executar o harness e obter as mesmas pontuações (dentro dos limites de não-determinismo de LLM)
- **Documentado** — seu [método card](/docs/specifications/methods) descreve o que seu método faz, quais ferramentas usa e quais são suas limitações
- **Honesto sobre escopo** — se seu método funciona apenas para um par de idiomas, diga isso; se degrada em certos padrões morfológicos, documente isso
- **Consciente da comunidade** — para idiomas indígenas, seu método respeita soberania de dados. Você consultou comunidades de idiomas ou usou apenas dados com licença aberta

### Sinais de alerta (o que é desqualificado)

| Sinal de Alerta | Por Que É um Problema |
|-----------------|----------------------|
| Treinamento em dados de avaliação | Derrota completamente o propósito da avaliação. Pontuações inflacionadas enganam todos. |
| Cherry-picking de resultados | Executar 10 vezes e submeter a melhor execução sem divulgar as outras |
| Pós-processamento não divulgado | Corrigir manualmente saídas antes de pontuar |
| Dados de coaching contaminados | Usar exemplos do conjunto de avaliação como prompts de poucos exemplos ou entradas de dicionário |
| Reivindicar prontidão comercial sem proveniência | Se seu método usa dados CC BY-NC-SA, não está pronto comercialmente |

### Níveis de verificação

Níveis de verificação descrevem **quem validou o resultado** — separado dos níveis de qualidade (Baseline → Fluent) definidos na [Especificação de Pontuação, §5](/docs/specifications/scoring#5-quality-tiers), que descrevem o que a pontuação composta automatizada significa.

| Nível | Significado | Como Obter |
|-------|-------------|-----------|
| **Self-benchmarked** | Você executou o harness você mesmo e submeteu resultados | Abra um PR com seu run card |
| **GDS Verified** | Os mantenedores do champollion reproduziram seus resultados | Submeta seu método como um plugin instalável |
| **Community Validated** | Org de governança executou contra padrão ouro + revisão da comunidade | Submeta código do método para org de governança |

---

## Como Submeter

1. **Construa seu método** — veja [Building a Method](/docs/specifications/methods) para a interface do método
2. **Execute o harness** — veja [Eval Harness](/docs/specifications/harness) para setup e uso
3. **Gere um run card** — o harness produz um run card JSON com suas pontuações, impressão digital e metadados
4. **Abra um PR** — submeta seu run card para o [repositório do eval harness](https://github.com/gamedaysuits/arena)
5. **Apareça no leaderboard** — uma vez mesclado, seus resultados aparecem no [Method Leaderboard](https://champollion.dev/leaderboard)

---

## Direções Futuras

- **Execuções de comparação de modelo abrangentes** — avaliação sistemática de modelos de fronteira (GPT-4o, Claude, Gemini, etc.) em idiomas champollion usando corpora de avaliação personalizados (não benchmarks públicos)
- **Mais pares de idiomas** — Quechua, Inuktitut e outros idiomas de baixo recurso conforme datasets verificados pela comunidade ficarem disponíveis
- **Importação de dataset** — ferramentas para converter datasets de avaliação externos (WMT, Tatoeba, etc.) para o formato de avaliação champollion
- **Re-execuções automatizadas** — detectando mudanças de versão de modelo e re-executando benchmarks para rastrear desvio de pontuação

---

## Veja Também

- **[Method Leaderboard](https://champollion.dev/leaderboard)** — pontuações ao vivo e submissões
- **[Eval Harness](/docs/specifications/harness)** — como executar avaliações
- **[Evaluation Datasets](/docs/leaderboard/datasets)** — formato de dataset e datasets disponíveis
- **[Building a Method](/docs/specifications/methods)** — especificação da interface do método
- **[Run Card Specification](/docs/specifications/run-card)** — schema JSON do run card
- **[Benchmark Specification](/docs/specifications/benchmark)** — protocolo de avaliação, formato de corpus, soberania
- **[Scoring Specification](/docs/specifications/scoring)** — SSOT para métricas, pesos compostos e níveis de qualidade