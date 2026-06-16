---
sidebar_position: 5
title: "Especificação de Pontuação"
slug: '/specifications/scoring'
related:
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
    note: "When a score difference actually means something"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
    note: "The tool that computes these metrics"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "These scores, live"
---
# Especificação de Pontuação

> **Resumo Executivo.** Este é o documento único e autoritário para todas as métricas de avaliação, pontuação composta, níveis de qualidade e análise de custos no ecossistema de avaliação de MT do Champollion. As métricas de avaliação específicas de idioma — validade morfológica FST, classes de equivalência de linter e validação semântica determinística — são coletivamente denominadas **LYSS** (Linguistically-informed Yield & Structural Scoring). Toda métrica computada pelo harness, todo peso na fórmula composta e todo limiar de nível é definido aqui — e apenas aqui. Código, documentação e esquemas de banco de dados derivam deste documento. Quando há conflito, este documento é autoritário.
>
> **Escopo.** Este documento define *o que* medimos e *como* pontuamos. Ele não define o esquema de run card (ver BENCHMARK_SPEC §3), o protocolo de benchmark (BENCHMARK_SPEC §6) ou as regras de leaderboard (ver docs da arena). Esses documentos fazem referência a este para definições de métricas e lógica de pontuação.
>
> Última atualização: 2026-06-07

---

## 1. Filosofia de Pontuação

### 1.1 Filosofia de Microeval

> *"Se nos concentrarmos apenas no que generaliza, inevitavelmente esqueceremos de onde não generaliza — e perderemos esses idiomas e todo seu conhecimento e sabedoria."*

Este projeto pratica **desenvolvimento de microeval**: construindo métricas de avaliação adaptadas a idiomas específicos usando as melhores ferramentas linguísticas disponíveis — transdutores de estado finito, dicionários bilíngues, analisadores morfológicos, regras de equivalência curadas por linguistas. Isto é o oposto do paradigma dominante em avaliação de MT, que busca métricas universais que funcionem em todos os idiomas. Métricas universais são valiosas, mas são mais fracas precisamente onde são mais necessárias: para idiomas com morfologia complexa, dados de treinamento limitados e sem representação em conjuntos de treinamento de métricas neurais.

Não estamos fazendo progresso em tradução automática para muitos idiomas do mundo não apenas porque nos faltam corpora, mas porque **nem mesmo sabemos como se parece o progresso** — nos faltam ferramentas de avaliação automatizadas para medir se um sistema de tradução está melhorando. LYSS é nossa tentativa de construir essas ferramentas, idioma por idioma, usando qualquer recurso linguístico que exista.

### 1.2 Métricas Automatizadas São Proxies

Toda métrica definida aqui é computada por máquina. Elas são úteis para iteração rápida, comparação sistemática e detecção de regressões. Elas **não são substitutos para julgamento humano**. Os níveis de qualidade em §5 são rótulos heurísticos — apenas revisão humana pode confirmar usabilidade real.

### 1.3 Design Multi-Sinal

Nenhuma métrica única captura qualidade de tradução. Uma tradução pode ter sobreposição perfeita de chrF++ mas falhar na validação morfológica. Pode passar em verificações FST mas carregar o significado errado. Pode ser semanticamente precisa mas estilisticamente estranha para o idioma alvo. A pontuação composta em §4 agrega múltiplos sinais independentes, cada um capturando uma dimensão diferente de qualidade.

### 1.4 Extensibilidade

Este inventário de métricas não é fechado. Novos idiomas trazem novos requisitos: precisão de tom para idiomas tonais, precisão diacrítica para scripts semíticos, correção de silabário para Cree. A arquitetura (protocolo MetricPlugin, composto ponderado com renormalização) é projetada para que métricas sejam adicionadas sem quebrar pontuações existentes. Métricas específicas de idioma (por exemplo, linter e validador semântico do CRK) são declaradas em cartões de idioma sob `evalMetrics` e carregadas de `eval_standards/` — o harness é enviado apenas com métricas comportamentais genéricas (code-switching, alucinação, terminologia).

### 1.5 Três Dimensões de Avaliação

Cada run card mede três dimensões independentes:

```
Quality   — How good is the translation?   (composite score, §4)
Cost      — How much does it cost?          (cost metrics, §6)
Speed     — How fast does it run?           (speed metrics, §7)
```

Estes são eixos independentes. Um método pode ser de alta qualidade mas caro, rápido mas impreciso, ou qualquer combinação. O leaderboard permite ordenação por qualquer dimensão. A pontuação ajustada por custo (§6.3) é a única métrica que combina dimensões.

### 1.6 Status de Validação

Toda métrica nesta especificação tem um **status de validação** distinto de seu status de implementação (§3). Status de implementação rastreia se o código existe. Status de validação rastreia se a métrica foi mostrada correlacionar com julgamentos de qualidade humana.

| Nível de Validação | Significado | Métricas Atuais |
|------------------|---------|----------------|
| **✅ Validado externamente** | Estudos de correlação humana publicados existem (WMT, artigos acadêmicos) | `chrf_plus_plus`, `bleu`, `comet_score` |
| **⚡ Validado por proxy** | Validado para idiomas de alto recurso; não validado para nossos LRLs alvo | `comet_score` (validado para pares EU, não para CRK) |
| **🔶 Heurística de engenharia** | Projetado a partir de princípios linguísticos ou modos de falha observados; sem dados de correlação humana | `fst_acceptance_rate`, `equivalent_match_rate`, `semantic_score`, `code_switching_rate`, `hallucination_rate`, `terminology_adherence` |
| **🔲 Não validado** | Ainda não testado em nenhum dado | `morphological_accuracy`, `orthographic_accuracy`, `consistency_score` |

> **O que isto significa na prática.** A pontuação composta (§4) agrega métricas em todos os níveis de validação. Esta é uma escolha de design explícita: acreditamos que uma heurística de engenharia estruturalmente fundamentada (aceitação FST) é mais informativa para idiomas polissintéticos do que uma métrica neural validada apenas em pares europeus (COMET). Mas não provamos isto. A pontuação composta deve ser tratada como uma **estimativa de engenharia**, não uma medição de qualidade validada, até que estudos de correlação humana sejam concluídos para cada idioma alvo.
>
> **Experimentos de validação necessários** (ver `mt-evaluation-landscape.md` §6 e `speaker-validation.md`):
> 1. Estudo de correlação com julgamento humano: 200+ pares de sentenças avaliados por 3+ falantes bilíngues
> 2. Medição de taxa de rejeição falsa FST em um corpus representativo
> 3. Porta de segundo idioma (Sámi do Norte) para testar generalização
> 4. Comparação direta com COMET nos mesmos dados


---

## 2. Inventário de Métricas {#2-metric-inventory}

Métricas são organizadas em quatro categorias. Cada métrica tem um status de implementação, escala e nível (por entrada, nível de corpus ou ambos).

### 2.1 Métricas de Superfície

Métricas de superfície comparam a tradução prevista com a tradução de referência no nível de string. Elas não requerem ferramentas linguísticas — apenas comparação de strings.

| ID | Métrica | Status | Escala | Nível | Implementação |
|----|--------|--------|-------|-------|---------------|
| `exact_match_rate` | Correspondência Exata | ✅ Implementado | 0.0–1.0 | Ambos | Binário: previsto == referência? Taxa de corpus = correspondências / total. |
| `equivalent_match_rate` | Correspondência Equivalente | ⚡ Parcial | 0.0–1.0 | Ambos | A saída prevista corresponde a qualquer variante aceita? Para CRK: implementado via padrão de avaliação CRK `CrkLinterMetric` (em `eval_standards/crk/`) usando regras de classe de variante determinísticas (ordem de palavras, ortográfica, partícula opcional, sinônimo de lema, ambiguidade progressiva). Carregado automaticamente via declaração `evalMetrics` do cartão de idioma CRK. Implementação genérica entre idiomas requer `variants[]` por entrada no corpus. |
| `chrf_plus_plus` | chrF++ | ✅ Implementado | 0–100 | Ambos | F-score de n-grama de caractere (sacrebleu). Robusto a variação morfológica. A métrica de superfície primária para idiomas aglutinadores/polissintéticos. Por entrada usa `sentence_chrf`; corpus usa `corpus_chrf`. |
| `bleu` | BLEU | ✅ Implementado | 0–100 | Corpus | Precisão de n-grama no nível de palavra (sacrebleu). **Excluído da composta** — pontuação no nível de palavra penaliza variação morfológica injustamente. Computado e reportado para compatibilidade com literatura de MT. |
| `ter` | Taxa de Edição de Tradução | ✅ Implementado | 0–∞ (menor é melhor) | Ambos | Distância de edição mínima entre previsto e referência, normalizada pelo comprimento da referência (sacrebleu `corpus_ter`). Computado junto com chrF++ e BLEU. Excluído da composta — correlaciona com chrF++ então incluir ambos dobraria a contagem de similaridade de superfície. |
| `length_ratio` | Razão de Comprimento | ✅ Implementado | 0–∞ (1.0 é ideal) | Ambos | `len(predicted) / len(reference)` em caracteres. Detecta truncamento (<0.5) e inflação/alucinação (>2.0). Média em entradas no nível de corpus. |

### 2.2 Métricas Estruturais

Métricas estruturais validam a bem-formação linguística da tradução. Elas requerem ferramentas específicas de idioma (analisadores FST, parsers morfológicos) e são os sinais mais fortes para idiomas morfologicamente ricos.

| ID | Métrica | Status | Escala | Nível | Implementação |
|----|--------|--------|-------|-------|---------------|
| `fst_acceptance_rate` | Aceitação FST | ✅ Implementado | 0.0–1.0 | Ambos | Proporção de palavras de saída aceitas por um transdutor de estado finito (GiellaLT). Uma palavra é "válida" se o FST retorna pelo menos uma análise morfológica. Disponível para qualquer idioma com analisador `.hfstol` GiellaLT. |
| `morphological_accuracy` | Precisão Morfológica | 🔲 Planejado | 0.0–1.0 | Ambos | Uma palavra pode ser FST-válida mas ter a inflexão errada (raiz correta, sufixo errado). Esta métrica compara a análise FST da palavra prevista contra as características morfológicas esperadas. Requer anotações morfológicas por entrada no corpus. |
| `orthographic_accuracy` | Precisão Ortográfica | 🔲 Planejado | 0.0–1.0 | Ambos | Valida correção específica de script: uso de macron/circunflexo SRO para Cree, marcas diacríticas para Inuktitut, marcadores de comprimento de vogal para Ojibwe. Conjuntos de regras por idioma. |

> **Por que métricas estruturais importam.** O OMT-1600 da Meta — o maior sistema de MT já publicado (1.600 idiomas) — avalia com ChrF++, xCOMET, MetricX e BLASER 3. Nenhuma delas valida correção morfológica. ChrF++ mede sobreposição de n-grama de caractere: recompensa strings que *parecem* o idioma alvo. Para idiomas polissintéticos, isto significa uma palavra morfologicamente inválida que compartilha muitos caracteres com a referência pontua bem. Nossa métrica de aceitação FST é um teste estrutural binário: a palavra é ou uma forma válida no idioma, ou não é. Nenhuma outra estrutura de avaliação de MT fornece isto em escala.

### 2.3 Métricas Semânticas

Métricas semânticas medem preservação de significado usando embeddings ou modelos aprendidos. Elas capturam traduções que são superficialmente diferentes mas semanticamente equivalentes, e sinalizam traduções que são superficialmente similares mas semanticamente erradas.

| ID | Métrica | Status | Escala | Nível | Implementação |
|----|--------|--------|-------|-------|---------------|
| `semantic_score` | Similaridade Semântica | ⚡ Parcial | 0.0–1.0 | Ambos | CRK: pontuação ponderada por veredicto do padrão de avaliação CRK `CrkSemanticMetric` (em `eval_standards/crk/`, proxy). Universal: similaridade de cosseno de embeddings de sentença (fonte + previsto vs fonte + referência). Modelo TBD — deve suportar idiomas de baixo recurso, o que exclui a maioria dos modelos de embedding centrados em inglês. |
| `comet_score` | COMET | ✅ Implementado | ~0.0–1.0 | Ambos | Métrica de avaliação de MT aprendida (Unbabel). Treinada em julgamentos de qualidade humana. **Excluída da composta** — dados de treinamento são enviesados para idiomas europeus de alto recurso; pontuações para LRLs são não confiáveis. Computada quando `unbabel-comet` está instalado. Reportada com sinalizador de aviso de baixo recurso. Para 35 idiomas africanos, o harness seleciona automaticamente AfriCOMET (`masakhane/africomet-mtl`) via `resolve_comet_model()`, que tem melhor correlação com julgamento humano para esses idiomas. |

> **Por que COMET é excluído da composta.** COMET é treinado em dados de avaliação humana WMT, que é predominantemente pares de idiomas europeus de alto recurso. Quando aplicado a Plains Cree ou outros LRLs, as representações internas do modelo não têm exposição a esses idiomas — está extrapolando de idiomas com sistemas morfológicos fundamentalmente diferentes. As pontuações ainda são direcionalmente úteis (COMET mais alto ≈ saída mais fluente em geral) mas os valores absolutos não são calibrados. Reportamos COMET por transparência mas não deixamos influenciar a pontuação composta até que possamos validá-la contra julgamentos humanos para cada idioma alvo.

> **AfriCOMET para idiomas africanos.** Cada cartão de idioma tem um campo `metricModelSupport` (ver especificação de cartão de idioma §9) que declara quais modelos COMET especializados são treinados para esse idioma. Para 35 idiomas africanos (yor, hau, ibo, amh, swa, etc.), o cartão declara AfriCOMET (`masakhane/africomet-mtl`) — um modelo COMET ajustado em julgamentos humanos de MT de idiomas africanos pela comunidade Masakhane. O harness seleciona automaticamente o modelo recomendado via `resolve_comet_model()` lendo de cartões de idioma, mas isto pode ser sobrescrito com `--comet-model`. Adicionar novos mapeamentos idioma→modelo é feito enriquecendo o cartão de idioma (não editando código Python).

### 2.4 Métricas Comportamentais

Métricas comportamentais detectam modos de falha específicos em saída de tradução. Elas não medem qualidade diretamente — elas detectam problemas.

| ID | Métrica | Status | Escala | Nível | Implementação |
|----|--------|--------|-------|-------|---------------|
| `code_switching_rate` | Taxa de Code-Switching | ✅ Implementado | 0.0–1.0 (menor é melhor) | Ambos | Proporção de palavras de saída que estão no idioma fonte (tipicamente inglês). Detectado via análise de script Unicode e/ou lista de palavras de idioma fonte. Modo de falha muito comum de LLM: o modelo insere palavras em inglês quando não conhece o equivalente no idioma alvo. |
| `hallucination_rate` | Taxa de Alucinação | ✅ Implementado | 0.0–1.0 (menor é melhor) | Ambos | Proporção de conteúdo de saída que não tem conteúdo de fonte correspondente. Detectado via alinhamento de palavras ou sobreposição de embedding cross-lingual. Captura o modelo gerando traduções plausíveis mas fabricadas. |
| `terminology_adherence` | Aderência de Terminologia | ✅ Implementado | 0.0–1.0 | Ambos | Para métodos treinados: proporção de termos de terminologia prescrita que aparecem na saída. Requer dados de dicionário de treinamento. Mede se o modelo respeita vocabulário fornecido por especialista. |
| `consistency_score` | Consistência Entre Entradas | 🔲 Planejado | 0.0–1.0 | Apenas Corpus | O modelo traduz o mesmo termo fonte da mesma forma em entradas? Consistência baixa sugere que o modelo está adivinhando em vez de aplicar padrões aprendidos. Requer termos repetidos em entradas de corpus. |

### 2.5 Métricas de Conformidade

Métricas de conformidade validam que traduções preservam integridade estrutural — placeholders, formatação e convenções tipográficas. Elas são verificações de portão de qualidade, não pontuações de qualidade.

| ID | Métrica | Status | Escala | Nível | Implementação |
|----|--------|--------|-------|-------|---------------|
| `compliance_index` | Conformidade de Dupla Passagem | ✅ Implementado | 0.0–1.0 | Ambos | Composta ponderada: 60% integridade de variável (variáveis `{placeholder}` são preservadas?) + 20% conformidade de aspas (caracteres de aspas corretos por cartão de idioma) + 20% conformidade de maiúsculas (sem vazamento de letra latina para idiomas sem maiúsculas). Computado em saída bruta e pós-processada. Via `DoublePassCompliancePlugin`. |
| `repair_effectiveness` | Efetividade de Reparo | ✅ Implementado | 0.0–1.0 | Corpus | Proporção de violações de conformidade que foram automaticamente reparadas por hooks pós-tradução. Mede quanto o portão de qualidade melhorou a saída bruta. |

> **Por que conformidade não está na composta.** Métricas de conformidade medem preservação estrutural (placeholders, aspas), não qualidade de tradução. Uma tradução pode ser perfeita linguisticamente mas falhar conformidade porque descartou uma variável `{name}`. Estes são portões de qualidade — eles bloqueiam saída ruim de ser enviada, mas não classificam qualidade de tradução.

---

## 3. Níveis de Status de Métrica

Toda métrica em §2 cai em um de quatro níveis de implementação:

| Nível | Significado | Comportamento de Run Card |
|------|---------|-------------------|
| **✅ Implementado** | Código existe, testado, produzindo valores em run cards hoje | Valor numérico em run card |
| **⚡ Parcial** | Proxy específico de idioma existe (ex: CRK) mas implementação universal está pendente | Valor numérico quando proxy se aplica, `null` caso contrário |
| **🔲 Planejado** | Especificado mas ainda não implementado | `null` em run card (campo presente, valor ausente) |
| **💡 Proposto** | Sob discussão, ainda não especificado | Não em run card |

Uma métrica se move de Planejado → Parcial quando:
1. Uma implementação específica de idioma é mesclada e testada
2. Produz valores para pelo menos um par de idiomas
3. A implementação universal permanece pendente (documentada nesta especificação)

Uma métrica se move de Parcial → Implementado quando:
1. Uma implementação agnóstica de idioma é mesclada e testada
2. Produz valores para qualquer par de idiomas sem plugins específicos de idioma
3. Este documento é atualizado para refletir status ✅

Uma métrica se move de Planejado → Implementado quando:
1. Implementação é mesclada e testada
2. Foi validada em pelo menos uma execução de avaliação real
3. Este documento é atualizado com seus detalhes de implementação

Uma métrica se move de Proposto → Planejado quando:
1. Sua definição, escala e método de computação são acordados
2. É adicionada a este documento com status `🔲 Planned`
3. Um placeholder nulo é adicionado ao esquema de run card

---

## 4. Pontuação Composta {#4-composite-score}

### 4.1 Fórmula

A pontuação composta é uma média ponderada de todas as métricas *disponíveis*, renormalizada para que os pesos das métricas disponíveis somem 1.0:

```
composite = Σ (weight_i × value_i)    for all available metrics
             ─────────────────────
             Σ weight_i               (re-normalization denominator)
```

Uma métrica é "disponível" se seu valor no run card é um número (não `null`). Quando uma métrica não está disponível — porque o idioma não tem FST, ou porque uma métrica ainda não está implementada — seu peso é redistribuído proporcionalmente entre as métricas restantes.

**Isto significa que a composta é sempre comparável dentro de uma execução:** usa qualquer métrica disponível e normaliza de acordo. Comparação entre execuções é válida quando execuções usam o mesmo conjunto de métricas disponíveis.

> [!WARNING]
> **Comparabilidade entre execuções.** Ao comparar execuções com disponibilidade de métrica diferente (ex: uma execução tem pontuações FST, outra não), as pontuações compostas **não são diretamente comparáveis**. Uma composta de 0.72 computada de 5 métricas carrega mais informação do que uma composta de 0.72 computada de 2 métricas. O leaderboard exibe um aviso quando cobertura de métrica difere entre execuções comparadas. Para comparação rigorosa, use testes de significância bootstrap pareados (§8.2) apenas em métricas compartilhadas.

### 4.2 Normalização de Entrada

Antes de entrar na fórmula composta, todas as métricas devem estar em uma **escala 0.0–1.0** onde 1.0 = perfeito:

| Métrica | Escala Nativa | Normalização |
|--------|-------------|---------------|
| `exact_match_rate` | 0.0–1.0 | Nenhuma (já normalizada) |
| `equivalent_match_rate` | 0.0–1.0 | Nenhuma |
| `fst_acceptance_rate` | 0.0–1.0 | Nenhuma |
| `morphological_accuracy` | 0.0–1.0 | Nenhuma |
| `chrf_plus_plus` | 0–100 | **Dividir por 100** |
| `semantic_score` | 0.0–1.0 | Nenhuma |
| `code_switching_rate` | 0.0–1.0 (menor = melhor) | **`1.0 - value`** (inverter: 0% code-switching = 1.0) |
| `hallucination_rate` | 0.0–1.0 (menor = melhor) | **`1.0 - value`** (inverter) |
| `terminology_adherence` | 0.0–1.0 | Nenhuma |

Métricas excluídas da composta (`bleu`, `comet_score`, `ter`, `length_ratio`, `consistency_score`) não são normalizadas para este propósito.

### 4.3 Tabelas de Peso {#43-weight-tables}

#### Perfil A: Idiomas COM Cobertura FST

Para idiomas que têm um transdutor de estado finito GiellaLT disponível. Métricas estruturais carregam 40% da composta (FST 0.25 + precisão morfológica 0.15), refletindo a primazia de correção morfológica para idiomas polissintéticos/aglutinadores.

| Métrica | Peso Alvo | Justificativa |
|--------|--------------|-----------|
| `fst_acceptance_rate` | **0.25** | Peso mais alto. Se o FST rejeita uma palavra, não é uma forma válida no idioma — independentemente do que outras métricas dizem. Binário, estruturalmente fundamentado. |
| `morphological_accuracy` | **0.15** | Uma palavra pode ser FST-válida mas morfologicamente errada (raiz correta, inflexão errada). Junto com FST, métricas estruturais carregam 40%. |
| `chrf_plus_plus` | **0.15** | Sobreposição de n-grama de caractere: o melhor proxy de nível de superfície para idiomas polissintéticos. Lida com morfologia aglutinadora melhor do que métricas no nível de palavra. |
| `semantic_score` | **0.15** | Preservação de significado quando forma de superfície diverge. Captura traduções semanticamente erradas que passam verificações estruturais. |
| `equivalent_match_rate` | **0.10** | Recompensa variantes aceitáveis, não apenas a tradução de referência única. Importante para idiomas com ordem de palavras flexível. |
| `code_switching_rate` | **0.05** | Penaliza vazamento de idioma fonte. Invertido: 0% code-switching = 1.0. |
| `terminology_adherence` | **0.05** | Recompensa métodos treinados que respeitam vocabulário prescrito. Ativo apenas quando dados de treinamento estão presentes. |
| `hallucination_rate` | **0.05** | Penaliza conteúdo fabricado. Invertido: 0% alucinação = 1.0. |
| `exact_match_rate` | **0.05** | Peso mais baixo. Muito rigoroso para idiomas polissintéticos — múltiplas traduções corretas existem. Mantido como verificação de teto. |

> **Total: 1.00.** Quando métricas não estão disponíveis, seus pesos são redistribuídos proporcionalmente entre métricas disponíveis. Atualmente, `morphological_accuracy` (peso 0.15) é a única métrica de Perfil A ainda não computada — requer anotações morfológicas de padrão-ouro por entrada. Com esta métrica ausente, as 8 métricas restantes (peso total 0.85) são cada uma escaladas por 1/0.85 ≈ 1.176. Por exemplo:
> - FST: 0.25/0.85 = 0.294
> - chrF++: 0.15/0.85 = 0.176
> - semântica: 0.15/0.85 = 0.176

#### Perfil B: Idiomas SEM Cobertura FST

Para idiomas sem ferramentas de validação morfológica. Métricas semânticas e de superfície carregam peso igual.

| Métrica | Peso Alvo | Justificativa |
|--------|--------------|-----------|
| `semantic_score` | **0.25** | Sem validação estrutural, preservação de significado é o sinal disponível mais forte. |
| `chrf_plus_plus` | **0.25** | Sem FST, sobreposição no nível de caractere se torna a verificação de superfície primária. |
| `equivalent_match_rate` | **0.15** | Correspondência de variante fornece avaliação de qualidade estruturada sem requerer ferramentas morfológicas. |
| `exact_match_rate` | **0.10** | Sem FST, correspondência exata carrega mais peso como único proxy de validação estrutural. |
| `code_switching_rate` | **0.10** | Vazamento de idioma fonte importa mais quando não há FST para capturar saída ruim. |
| `terminology_adherence` | **0.05** | Conformidade de vocabulário treinado. |
| `hallucination_rate` | **0.05** | Detecção de conteúdo fabricado. |
| `orthographic_accuracy` | **0.05** | Correção específica de script preenche parte da lacuna deixada por FST ausente. |

> **Total: 1.00.** `orthographic_accuracy` (peso 0.05) é planejado mas ainda não computado. Com ele ausente, as 7 métricas restantes (peso total 0.95) são escaladas por 1/0.95 ≈ 1.053 — um impacto negligenciável na composta.

> **Nota sobre evolução de peso.** Estes pesos são provisórios e serão recalibrados conforme dados de validação humana se acumulam. O objetivo de longo prazo é derivar pesos empiricamente: quais métricas automatizadas melhor predizem julgamentos de qualidade humana para cada família de idiomas?

### 4.4 Adicionando uma Nova Métrica à Composta

Para adicionar uma nova métrica à composta:

1. **Defina-a** em §2 com status `🔲 Planned`, incluindo escala, nível e método de computação.
2. **Implemente-a** como um MetricPlugin (ou em `tester.py` para métricas principais).
3. **Adicione um placeholder nulo** no bloco de pontuações de run card.
4. **Atribua um peso alvo** em §4.3 ajustando pesos existentes para baixo. Pesos devem somar 1.00.
5. **Atualize BENCHMARK_SPEC.md** §3 se o esquema de run card mudar.
6. **Atualize `scoring.py`** tabelas de peso (o código deve espelhar este documento).
7. **Execute um benchmark de validação** para confirmar que a métrica produz valores sensatos em dados reais.
8. **Atualize este documento** para mudar status de `🔲` para `✅`.

---

## 5. Níveis de Qualidade {#5-quality-tiers}

Estes níveis são rótulos heurísticos em pontuações compostas automatizadas. Eles descrevem o que as pontuações tendem a significar na prática, baseado em revisão humana de saídas em cada nível. **Eles não são julgamentos de qualidade validados** — apenas revisão humana pode confirmar usabilidade real.

> [!IMPORTANT]
> **Níveis automatizados são provisórios.** Estes rótulos são indicações para revisão, não declarações de qualidade. Um método atingindo "Implantável" em métricas automatizadas é um candidato para avaliação comunitária — não um produto para enviar. Apenas revisão humana por falantes bilíngues pode confirmar usabilidade real (ver [BENCHMARK_SPEC §7](/docs/specifications/benchmark#7-human-validation)). Nenhum método pode reivindicar Implantável ou acima sem revisão comunitária confirmando que falantes concordam que a saída é usável. Limites de nível podem diferir entre idiomas conforme dados de validação humana se acumulam.

| Nível | Intervalo Composto | O Que um Falante Tipicamente Vê |
|------|----------------|-------------------------------|
| **Baseline** | 0.00–0.30 | Saída bruta de LLM sem suporte específico de idioma. Morfologia é principalmente alucinada. |
| **Emergente** | 0.30–0.50 | Alguns padrões corretos começando a aparecer. Treinamento está ajudando, mas saída não é confiável. |
| **Funcional** | 0.50–0.70 | Saída é reconhecível para um falante. Categorias gramaticais principais geralmente corretas. Erros morfológicos frequentes. |
| **Implantável** | 0.70–0.85 | Adequado para tradução de rascunho com revisão humana. Maioria da morfologia está correta. |
| **Fluente** | 0.85–1.00 | Aproximando-se de tradução humana competente. Erros são raros e menores. |

Estes níveis são provisórios. Serão recalibrados conforme dados de validação humana se acumulam e aprendemos onde o limiar "um falante acha isto útil" realmente cai para cada idioma. Nenhum método pode reivindicar **Implantável** ou acima sem revisão comunitária confirmando que falantes bilíngues concordam que a saída é usável.

### 5.1 Limites de Nível (Legível por Máquina)

Para implementações de código, os limites são (avaliados de cima para baixo, primeira correspondência vence):

```
composite >= 0.85  →  "fluent"
composite >= 0.70  →  "deployable"
composite >= 0.50  →  "functional"
composite >= 0.30  →  "emerging"
composite >= 0.00  →  "baseline"
composite is null  →  "unscored"
```

---

## 6. Métricas de Custo

Métricas de custo medem a eficiência financeira de um método de tradução. Elas são reportadas separadamente de qualidade — custo não influencia a pontuação composta (exceto na classificação secundária ajustada por custo).

### 6.1 Métricas de Token

| ID | Métrica | Computação |
|----|--------|-------------|
| `prompt_tokens` | Total de tokens de entrada | Soma de `usage.prompt_tokens` em todas as chamadas de API |
| `completion_tokens` | Total de tokens de saída | Soma de `usage.completion_tokens` |
| `reasoning_tokens` | Tokens de cadeia de pensamento | Soma de `usage.completion_tokens_details.reasoning_tokens` (0 para maioria dos modelos) |
| `cached_tokens` | Tokens em cache do provedor | Soma de `usage.prompt_tokens_details.cached_tokens` |
| `total_tokens` | Total de tokens consumidos | `prompt_tokens + completion_tokens` |
| `tokens_per_entry` | Média de tokens por tradução | ✅ `total_tokens / entry_count` |

### 6.2 Métricas de Custo

| ID | Métrica | Computação | Caso de Uso |
|----|--------|-------------|----------|
| `total_cost_usd` | Custo total de execução | Preço reportado por provedor × contagens de token | "Quanto custou este benchmark?" |
| `cost_per_entry_usd` | Custo por entrada de corpus | `total_cost_usd / entry_count` | Comparando métodos no mesmo corpus |
| `cost_per_1k_tokens` | Custo por 1.000 tokens | ✅ `total_cost_usd / total_tokens × 1000` | Eficiência universal de LLM — comparável entre corpora |
| `cost_per_source_char` | Custo por caractere fonte | `total_cost_usd / total_source_chars` | Comparável entre idiomas com tokenização diferente |

> **Por que múltiplas métricas de custo?** Uma "entrada" varia em comprimento — uma frase de 3 palavras custa menos do que um parágrafo. `cost_per_entry_usd` é útil para comparar métodos no *mesmo* corpus (mesmas entradas = mesmos comprimentos = comparação justa). `cost_per_1k_tokens` é a métrica de eficiência de LLM padrão, comparável *entre* corpora. `cost_per_source_char` normaliza para diferenças de tokenização — a mesma sentença pode tokenizar em números diferentes de tokens dependendo do vocabulário do modelo.

### 6.3 Pontuação Ajustada por Custo

Para métodos usando APIs pagas, computamos uma classificação secundária:

```
cost_adjusted = composite / log2(1 + cost_per_entry_usd × 1000)
```

Isto recompensa métodos que alcançam boas pontuações eficientemente. Usa `cost_per_entry_usd` (não por token) porque a pontuação ajustada por custo é sempre computada dentro de um único benchmark (mesmo corpus), tornando comparação por entrada justa.

A pontuação ajustada por custo é uma **classificação secundária** — o leaderboard primário classifica por pontuação composta. Ela responde uma pergunta diferente: "dado um orçamento, qual método dá os melhores resultados?"

---

## 7. Métricas de Velocidade

Métricas de velocidade medem latência e throughput de um método de tradução. Como custo, velocidade não influencia a pontuação composta.

| ID | Métrica | Computação | Nível |
|----|--------|-------------|-------|
| `elapsed_seconds` | Duração de execução em tempo real | `time_end - time_start` | Execução |
| `avg_latency_seconds` | Latência média por entrada | `Σ latency_s / n_entries` | Corpus |
| `median_latency_seconds` | Latência mediana por entrada | 50º percentil de `latency_s` | Corpus |
| `p95_latency_seconds` | Latência do 95º percentil | 95º percentil de `latency_s` | Corpus |
| `tokens_per_second` | Throughput | `total_tokens / elapsed_seconds` | Execução |
| `entries_per_minute` | Taxa de tradução | `entry_count / (elapsed_seconds / 60)` | Execução |

---

## 8. Confiança e Significância

### 8.1 Intervalos de Confiança Bootstrap

Todas as métricas-chave suportam intervalos de confiança bootstrap (método percentil, n=1000 reamostragens, α=0.05):

| Métrica | IC Reportado |
|--------|------------|
| `chrf_plus_plus` | ✅ `chrf_ci_lower`, `chrf_ci_upper` |
| `exact_match_rate` | ✅ `exact_match_ci_lower`, `exact_match_ci_upper` |
| `fst_acceptance_rate` | ✅ `fst_ci_lower`, `fst_ci_upper` (computado apenas quando dados FST existem) |
| `comet_score` | ✅ `comet_ci_lower`, `comet_ci_upper` (bootstrapped de pontuações por entrada em cache — sem inferência neural redundante) |
| `composite` | ✅ `composite_ci_lower`, `composite_ci_upper` (computado quando chrF++ e exact_match estão disponíveis) |
| ICs por nível | ✅ `confidence_intervals_by_tier` — ICs de chrF++ e exact_match por nível de dificuldade (Nível 1-5) |

### 8.2 Testes de Significância Bootstrap Pareados

Para comparar dois métodos, o harness computa testes de reamostragem bootstrap pareados:

```
H₀: The two methods perform equally on this corpus.
H₁: One method is significantly better.
```

Se o p-valor < 0.05 e o intervalo de confiança da diferença exclui zero, a diferença é estatisticamente significante no nível 95%.

---

## 9. Esquema de Pontuações de Run Card

Esta seção define a estrutura hierárquica do bloco `scores` em um run card. Este esquema é derivado das métricas definidas em §2–§7 e deve ser mantido em sincronização.

```jsonc
{
  "scores": {
    // §2.1 Surface metrics
    "exact_match_rate":       0.6613,       // 0.0–1.0
    "exact_matches":          41,           // count
    "equivalent_match_rate":  0.7258,       // ⚡ partial (CRK: eval_standards/crk CrkLinterMetric)
    "equivalent_matches":     45,           // ⚡ partial (CRK: eval_standards/crk CrkLinterMetric)
    "chrf_plus_plus":         80.65,        // 0–100 (sacrebleu native scale)
    "bleu":                   54.78,        // 0–100, NOT in composite
    "ter":                    42.3,         // ✅ implemented, 0–∞ (lower=better)
    "length_ratio":           1.03,         // ✅ implemented, ideal=1.0

    // §2.2 Structural metrics
    "fst_acceptance_rate":    1.0,          // 0.0–1.0
    "fst_accepted":           74,           // count
    "morphological_accuracy": null,         // 🔲 planned
    "orthographic_accuracy":  null,         // 🔲 planned

    // §2.3 Semantic metrics
    "semantic_score":         0.6842,       // ⚡ partial (CRK: eval_standards/crk CrkSemanticMetric)
    "comet_score":            null,         // nullable, NOT in composite
    "comet_model":            "",           // model ID used for COMET

    // §2.4 Behavioral metrics
    "code_switching_rate":    0.03,         // ✅ implemented (lower=better)
    "hallucination_rate":     0.01,         // ✅ implemented (lower=better)
    "terminology_adherence":  null,         // ✅ implemented (null when no glossary)
    "consistency_score":      null,         // 🔲 planned

    // §4 Composite
    "composite":              0.8988,       // 0.0–1.0
    "quality_tier":           "fluent",     // §5 tier label
    "cost_adjusted":          null,         // §6.3 secondary ranking

    // §7 Speed metrics (merged into scores block)
    "tokens_per_second":      4462.5,       // ✅ total_tokens / elapsed
    "entries_per_minute":     82.30,        // ✅ entry_count / (elapsed/60)
    "avg_latency_seconds":    0.234,
    "median_latency_seconds": 0.190,
    "p95_latency_seconds":    0.415,

    // §8.1 Confidence intervals
    "confidence_intervals": {
      "chrf_plus_plus":     { "ci_lower": 78.2, "ci_upper": 83.1 },
      "exact_match_rate":   { "ci_lower": 0.54, "ci_upper": 0.78 },
      "corpus_comet":       { "ci_lower": 0.71, "ci_upper": 0.76 }
    },
    "confidence_intervals_by_tier": {
      "1": { "corpus_chrf": { "ci_lower": 68.1, "ci_upper": 76.5 } },
      "3": { "corpus_chrf": { "ci_lower": 36.2, "ci_upper": 47.0 } }
    },

    // Breakdowns
    "by_difficulty":          {},           // scores grouped by difficulty tier
    "by_provenance":          {},           // scores grouped by entry provenance

    // Counts
    "total":                  62,
    "evaluated":              62,
    "errors":                 0
  },

  "totals": {
    // §6.1 Token metrics
    "prompt_tokens":          13985,
    "completion_tokens":      187822,
    "reasoning_tokens":       175726,
    "cached_tokens":          0,
    // §6.2 Cost metrics
    "total_cost_usd":         1.7114,
    "cost_per_entry_usd":     0.027603,
    "cost_per_source_char":   null          // 🔲 needs source char counting
  }
}
```

> **Histórico de esquema.** Rascunhos de especificação anteriores propuseram blocos separados `cost`, `speed` e `tokens`. Estes foram mesclados em `scores` e `totals` respectivamente por simplicidade. Métricas de velocidade (`tokens_per_second`, `entries_per_minute`, latências) vivem em `scores`; contagens de token e figuras de custo vivem em `totals`.

### 9.1 Mapeamento Esquema–Banco de Dados

O JSON de run card é armazenado em sua totalidade como coluna `jsonb` em Supabase. Métricas-chave também são desnormalizadas em colunas de nível superior para desempenho de ordenação/filtro:

| Campo de Run Card | Coluna Supabase | Tipo | Índice |
|---------------|----------------|------|-------|
| `scores.composite` | `composite_score` | `real` | `idx_composite` |
| `scores.quality_tier` | `quality_tier` | `text` | — |
| `scores.chrf_plus_plus` | `chrf_plus_plus` | `real` | `idx_leaderboard` |
| `scores.exact_match_rate` | `exact_match_rate` | `real` | — |
| `scores.fst_acceptance_rate` | `fst_acceptance_rate` | `real` | — |
| `scores.bleu` | `corpus_bleu` | `real` | — |
| `scores.comet_score` | `comet_score` | `real` | — |
| `totals.total_cost_usd` | `total_cost_usd` | `real` | — |
| `totals.cost_per_entry_usd` | `cost_per_entry_usd` | `real` | — |
| `totals.cost_per_source_char` | `cost_per_source_char` | `real` | — |
| `scores.avg_latency_seconds` | `avg_latency_seconds` | `real` | — |
| `model_slug` | `model_slug` | `text` | `idx_model` |
| `condition` | `condition` | `text` | — |
| `dataset.id` | `dataset_id` | `text` | `idx_leaderboard` |
| `dataset.language_pair` | `language_pair` | `text` | — |
| `fingerprint.hash` | `fingerprint_hash` | `text` | `idx_fingerprint` |
| `scores.equivalent_match_rate` | `equivalent_match_rate` | `real` | — |
| `scores.semantic_score` | `semantic_score` | `real` | — |
| `scores.ter` | `ter` | `real` | — |
| `scores.length_ratio` | `length_ratio` | `real` | — |
| `scores.code_switching_rate` | `code_switching_rate` | `real` | — |
| `scores.hallucination_rate` | `hallucination_rate` | `real` | — |
| `scores.terminology_adherence` | `terminology_adherence` | `real` | — |
| `scores.tokens_per_second` | `tokens_per_second` | `real` | — |
| `scores.entries_per_minute` | `entries_per_minute` | `real` | — |
| `elapsed_seconds` | `elapsed_seconds` | `real` | — |
| *(cartão completo)* | `run_card` | `jsonb` | — |

Quando novas métricas são implementadas, a coluna correspondente deve ser adicionada via migração numerada em `arena/migrations/`.

---

## 10. Sincronização Código–Especificação

### 10.1 Fonte Canônica

Este documento (`arena/website/docs/specifications/scoring.md`) é a fonte canônica para:
- Definições de métrica (§2)
- Tabelas de peso composto (§4.3)
- Limites de nível de qualidade (§5.1)
- Fórmulas de métrica de custo (§6.2)
- Esquema de pontuações de run card (§9)

### 10.2 Espelho de Código

O arquivo `arena/mt_eval_harness/scoring.py` espelha as tabelas de peso e limites de nível de qualidade deste documento. É a **implementação de código** de §4.3 e §5.1. Quando este documento é atualizado:

1. Atualize `scoring.py` para corresponder
2. Execute `pytest tests/test_scoring_ssot.py` para validar alinhamento
3. Atualize FAQ e docs de website que resumem os pesos

### 10.3 Documentos Que Fazem Referência a Esta Especificação

| Documento | O Que Faz Referência | Como Manter em Sincronização |
|----------|-------------------|---------------------|
| `arena/website/docs/specifications/benchmark-spec.md` §4–§5 | Fórmula composta, tabelas de peso, limites de nível | Referência cruzada este doc; não duplique tabelas |
| `website/docs/getting-started/faq.md` | Resumo de peso simplificado | Deve corresponder §4.3; link de volta para este doc |
| `arena/website/docs/how-it-works.md` | Limiar Implantável | Deve corresponder §5 |
| `publish.py` via `scoring.py` | Dicts de peso + função de nível | Teste automatizado valida correspondência |

---

## Apêndice A: Métricas NÃO na Composta (e Por Quê)

| Métrica | Por Que Excluída |
|--------|-------------|
| **BLEU** | Pontuação no nível de palavra penaliza variação morfológica em idiomas polissintéticos. Uma diferença inflexional menor (significado correto, sufixo ligeiramente diferente) conta como uma falha completa. chrF++ lida melhor com isto no nível de caractere. |
| **COMET** | Treinado em dados WMT (pares europeus de alto recurso). Pontuações para LRLs são não confiáveis — o modelo está extrapolando de idiomas com sistemas morfológicos diferentes. Reportado por transparência, não para pontuação. |
| **TER** | Distância de edição correlaciona com chrF++ para maioria dos casos de uso. Incluir ambos dobraria a contagem de similaridade de superfície. TER é reportado para referência. |
| **Razão de Comprimento** | Um diagnóstico, não um sinal de qualidade. Uma razão de 1.02 e uma razão de 0.98 são ambas boas. Apenas valores extremos indicam problemas. |
| **Pontuação de Consistência** | Apenas nível de corpus — sem valor por entrada para agregar. Também, alguma inconsistência é legítima (mesma palavra em inglês → diferentes traduções em idioma alvo dependendo de contexto). |
| **Índice de Conformidade** | Portão de qualidade, não sinal de qualidade. Mede preservação estrutural (placeholders, aspas), não precisão de tradução. |

## Apêndice B: LYSS — Implementações de Métrica Específica de Idioma

O framework **LYSS** (Linguistically-informed Yield & Structural Scoring) fornece métricas específicas de idioma que vão além de comparação de string de nível de superfície. LYSS tem três componentes principais:

- **LYSS-fst** — Validade morfológica (`fst_acceptance_rate`): Cada palavra é uma forma válida no idioma alvo?
- **LYSS-eq** — Equivalência linguística (`equivalent_match_rate`): A saída é uma variante aceitável da referência?
- **LYSS-sem** — Validação semântica (`semantic_score`): A saída preserva o significado da fonte?

> **Status de validação: 🔶 Heurística de engenharia.** Métricas LYSS NÃO foram validadas contra julgamentos de qualidade humana. Elas são projetadas a partir de princípios linguísticos (FSTs, dicionários, regras gramaticais construídas por linguistas no ALTLab da UAlberta), mas a correlação entre pontuações LYSS e qualidade de tradução real não foi medida. Ver [Protocolo de Validação de Falante](/docs/specifications/speaker-validation) para os experimentos de validação necessários.

| Idioma | Plugin | Localização | Componente LYSS | Chave de Métrica | Notas |
|----------|--------|----------|----------------|------------|-------|
| CRK (Plains Cree) | `CrkLinterMetric` | `eval_standards/crk/metrics.py` | **LYSS-eq** | `equivalent_match_rate` | Regras de classe de variante determinísticas: ordem de palavras, ortográfica, partícula opcional, sinônimo de lema, ambiguidade progressiva, inclusivo/exclusivo. Produz `lint_verdict` por entrada (EXACT/EQUIVALENT/MISS/NO_OUTPUT). |
| CRK | `CrkSemanticMetric` | `eval_standards/crk/metrics.py` | **LYSS-sem** | `semantic_score` | Determinístico: extração de lema FST + glossas de dicionário + sobreposição de palavra de conteúdo spaCy. Produz veredictos (EXACT_MATCH/VALID/GRAMMAR_ISSUES/PARTIAL/INCOMPLETE/WRONG/NO_OUTPUT). |
| Idiomas GiellaLT | `GiellaLTFSTMetric` | `plugins/giellalt_fst.py` | **LYSS-fst** | `fst_acceptance_rate` | Genérico: funciona para CRK, SME, SMA, SMJ, SMN, SMS, FIN, NOB, IKU — qualquer idioma com analisador `.hfstol`. |

> **Nota de arquitetura (junho de 2026).** Métricas LYSS específicas de idioma agora são declaradas no cartão de idioma sob `evalMetrics` e carregadas de `eval_standards/<lang>/` por `plugin_discovery.py`. Elas são **padrões de avaliação** (árbitro), não métricas de plugin de método (concorrente). Isto significa qualquer método de tradução visando CRK é automaticamente pontuado por LYSS — nenhuma configuração específica de método necessária. `CrkFSTMetric` foi removido; sua funcionalidade é totalmente coberta pelo `GiellaLTFSTMetric` genérico.

## Apêndice C: Métricas Sob Consideração

Estas são ideias sendo avaliadas mas ainda não especificadas o suficiente para §2:

| Ideia | O Que Mediria | Bloqueadores |
|------|----------------------|----------|
| Fluência (perplexidade de LM) | A saída é prosa bem-formada no idioma alvo? | Requer um LM de idioma alvo. Nenhum bom modelo existe para maioria dos LRLs. |
| Correspondência de registro | A tradução corresponde ao nível de formalidade esperado? | Requer classificadores sociolinguísticos. Problema de pesquisa. |
| Apropriação cultural | Referências culturais são tratadas corretamente? | Não pode ser automatizado — inerentemente requer revisão humana. |
| Coerência de discurso | Traduções consecutivas formam uma passagem coerente? | Requer avaliação no nível de documento, não no nível de sentença. |

---

## Referências

Artigos acadêmicos, ferramentas e recursos de idioma citados ao longo desta especificação.

### Métricas de Superfície

1. Popović, M. (2017). "chrF++: words helping character n-grams." *Proceedings of the Second Conference on Machine Translation (WMT 2017)*, pp. 612–618. Copenhagen, Denmark.

2. Papineni, K., Roukos, S., Ward, T., & Zhu, W.-J. (2002). "BLEU: a method for automatic evaluation of machine translation." *Proceedings of the 40th Annual Meeting of the Association for Computational Linguistics (ACL 2002)*, pp. 311–318. Philadelphia, PA.

3. Post, M. (2018). "A Call for Clarity in Reporting BLEU Scores." *Proceedings of the Third Conference on Machine Translation (WMT 2018)*, pp. 186–191. Belgium, Brussels. Implementação de referência: [sacrebleu](https://github.com/mjpost/sacrebleu).

4. Snover, M., Dorr, B., Schwartz, R., Micciulla, L., & Makhoul, J. (2006). "A Study of Translation Edit Rate with Targeted Human Annotation." *Proceedings of the 7th Conference of the Association for Machine Translation in the Americas (AMTA 2006)*, pp. 223–231. Cambridge, MA.

### Métricas Neurais

5. Rei, R., Stewart, C., Farinha, A. C., & Lavie, A. (2020). "COMET: A Neural Framework for MT Evaluation." *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP 2020)*, pp. 2685–2702. Online.

6. Juraska, J., Finkelstein, M., Deutsch, D., Siddhant, A., Miber, D., & Markl, A. (2023). "MetricX-23: The Google Submission to the WMT 2023 Metrics Shared Task." *Proceedings of the Eighth Conference on Machine Translation (WMT 2023)*. Singapore.

7. Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y. (2020). "BERTScore: Evaluating Text Generation with BERT." *Proceedings of the Eighth International Conference on Learning Representations (ICLR 2020)*. Addis Ababa, Ethiopia.

8. Sellam, T., Das, D., & Parikh, A. (2020). "BLEURT: Learning Robust Metrics for Text Generation." *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020)*, pp. 7881–7892. Online.

### Ferramentas Morfológicas e Linguísticas

9. Lindén, K., Silfverberg, M., Axelson, E., Hardwick, S., & Pirinen, T. (2011). "HFST—Framework for Compiling and Applying Morphologies." *Systems and Frameworks for Computational Morphology (SFCM 2011)*, Communications in Computer and Information Science, vol. 100, pp. 67–85. Springer, Berlin, Heidelberg.

10. Sánchez-Cartagena, V. M., & Toral, A. (2024). "MorphEval: Automatic Evaluation of Morphological Capabilities of Machine Translation Systems." *Machine Translation*, vol. 38, pp. 1–28.

### Classificação de Erro e Avaliação Diagnóstica

11. Popović, M. (2011). "Hjerson: An Open Source Tool for Automatic Error Classification of Machine Translation Output." *The Prague Bulletin of Mathematical Linguistics*, no. 96, pp. 59–68.

12. Dreyer, M. & Marcu, D. (2012). "HyTER: Meaning-Equivalent Semantics for Translation Evaluation." *Proceedings of the 2012 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2012)*, pp. 162–171. Montréal, Canada.

13. Reiter, E. & Belz, A. (2009). "An Investigation into the Validity of Some Metrics for Automatically Evaluating Natural Language Generation Systems." *Computational Linguistics*, vol. 35, no. 4, pp. 529–558. (Trabalho relacionado em métricas de avaliação baseadas em características, incluindo FUSE.)

### Detecção de Alucinação

14. Raunak, V., Menezes, A., & Junczys-Dowmunt, M. (2021). "The Curious Case of Hallucinations in Neural Machine Translation." *Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2021)*, pp. 1172–1183. Online.

15. Guerreiro, N. M., Voita, E., & Martins, A. F. T. (2023). "Looking for a Needle in a Haystack: A Comprehensive Study of Hallucinations in Neural Machine Translation." *Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2023)*, pp. 1059–1075. Dubrovnik, Croatia.

### Recursos de Idioma Cree

16. Wolfart, H. C. (1973). "Plains Cree: A Grammatical Study." *Transactions of the American Philosophical Society*, vol. 63, no. 5, pp. 1–90.

17. Wolvengrey, A. (2001). *nêhiyawêwin: itwêwina / Cree: Words.* Canadian Plains Research Center, University of Regina.

### Governança de Dados

18. First Nations Information Governance Centre. "The First Nations Principles of OCAP®." [https://fnigc.ca/ocap-training/](https://fnigc.ca/ocap-training/). (OCAP® é uma marca registrada do First Nations Information Governance Centre.)

19. Carroll, S. R., Garba, I., Figueroa-Rodríguez, O. L., Holbrook, J., Lovett, R., Materechera, S., Parsons, M., Raseroka, K., Rodriguez-Lonebear, D., Rowe, R., Sara, R., Walker, J. D., Anderson, J., & Hudson, M. (2020). "The CARE Principles for Indigenous Data Governance." *Data Science Journal*, vol. 19, no. 1, p. 43.