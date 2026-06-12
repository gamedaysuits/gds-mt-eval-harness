---
sidebar_position: 2
title: "Como Palestrantes Recebem Pagamento"
slug: '/perspectives/how-speakers-get-paid'
description: "O que validadores comunitários e tradutores recebem por trabalho em benchmarks, por que pagar palestrantes é inegociável e como a compensação escala conforme a Arena cresce. Todos os números vêm das especificações publicadas."
related:
  - label: "Speaker Validation Protocol"
    to: /docs/specifications/speaker-validation
    kind: spec
    note: "The work validators are paid for"
  - label: "Prize Specification"
    to: /docs/specifications/prizes
    kind: spec
    note: "Where prize money goes, and why"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
---
# Como Falantes Recebem Pagamento

> **Nota de transparência.** Todos os números nesta página já aparecem em uma especificação publicada — a [Especificação do Benchmark §10](/docs/specifications/benchmark#10-cost-framework), o [Protocolo de Validação de Falantes](/docs/specifications/speaker-validation), e a [Especificação de Prêmios](/docs/specifications/prizes). Esta página os reúne em um único lugar, em linguagem clara, para que ninguém precise ler uma especificação para descobrir quanto o tempo de um falante vale aqui. Não faz compromissos além do que esses documentos já estabelecem.

Um falante bilíngue que consegue julgar se uma sentença produzida por máquina é real, fluente e significa a coisa certa é o participante mais escasso e valioso em todo este sistema. Tudo mais — infraestruturas, métricas, leaderboards — existe para fazer uma pequena quantidade do tempo dessa pessoa render muito.

Então a primeira regra é simples: **falantes são pagos pelo seu tempo, em taxas profissionais, independentemente do que os resultados mostrem.**

---

## Por que pagar falantes é inegociável

A pesquisa em tecnologia de linguagem tem um longo hábito de tratar falantes fluentes como um recurso gratuito — "engajamento comunitário" que produz datasets, papers e carreiras para todos exceto os falantes. Consideramos esse padrão extrativista, e as pessoas mais qualificadas para fazer este trabalho são precisamente aquelas cujo tempo já é reclamado pelo trabalho urgente de ensinar, traduzir e criar filhos na língua.

Três consequências de design seguem:

1. **Sem pipeline de voluntários.** Não pedimos aos falantes que doem trabalho de avaliação como um favor à pesquisa. A participação é um engajamento remunerado, e recusá-lo não custa nada ao falante.
2. **Pagamento é incondicional.** Falantes são pagos independentemente de suas avaliações serem usadas, e o pagamento não é contingente aos resultados. O protocolo publicado se compromete com pagamento dentro de duas semanas após completar cada bloco de tarefas.
3. **Compensação não é tudo.** Falantes que contribuem com avaliações também recebem crédito (nomeado ou anônimo, sua escolha), co-autoria opcional em publicações que usam suas avaliações, o direito de retirar suas contribuições a qualquer momento, e poder de veto sobre a publicação de resultados que considerem problemáticos. Esses termos estão no [Protocolo de Validação de Falantes §5–6](/docs/specifications/speaker-validation), não em uma carta lateral.

## As taxas publicadas

O framework de custo do benchmark estabelece compensação para falantes bilíngues em **$50–65 CAD por hora** para trabalho de corpus e validação. O que isso significa por função:

### Construindo um corpus de benchmark

Criar as traduções de referência contra as quais cada método é avaliado é a tarefa fundamental de um falante. O orçamento de estabelecimento publicado por idioma:

| Trabalho | Intervalo publicado | Base |
|----------|---------------------|------|
| Curadoria de corpus (50–150 entradas) | $2.500–6.000 | $50–65/hr, tempo de falante bilíngue |
| Revisão de saída de método | $500–1.500 | Mesmas taxas horárias |

Um corpus completo tradicionalmente leva um falante aproximadamente 80 horas; o fluxo de trabalho planejado com assistência de agentes (rascunho de sentença e formatação tratados por ferramentas, tradução sempre por um humano) é projetado para levar isso em direção a 30–40 horas — menos horas de trabalho repetitivo, mesma taxa horária, com o falante fazendo apenas as partes que genuinamente requerem um humano.

### Validando as métricas

Antes de pontuações automatizadas significarem algo, falantes têm que verificá-las contra o julgamento humano. O [Protocolo de Validação de Falantes](/docs/specifications/speaker-validation) publica as tarefas exatas, horas e pagamento:

| Tarefa | Tempo | Pagamento por falante |
|--------|-------|----------------------|
| A — Avaliar 200 traduções de máquina para adequação e fluência | ~8 horas | $400–520 CAD |
| B — Revisar 50 pares de tradução "equivalentes" | ~2 horas | $100–130 CAD |
| C — Revisar 100 palavras que o analisador morfológico rejeitou | ~1,5 horas | $75–100 CAD |

Um falante fazendo os três se compromete com aproximadamente 11,5 horas ao longo de duas a quatro semanas por **$575–750 CAD**. A rodada completa de validação de três falantes custa ao projeto $1.475–1.920 — que é o ponto: validação de falantes é um item de linha pequeno para o projeto e nunca deve ser onde custos são "economizados".

### Revisando reivindicações de prêmios

Nenhum prêmio é pago apenas em pontuações automatizadas. O [Prêmio do Fundador](/docs/specifications/prizes) ($10.000 CAD, English→Plains Cree) requer que pelo menos dois falantes bilíngues revisem independentemente uma amostra estratificada de pelo menos 30 saídas, e que 70% ou mais sejam avaliadas como "aceitável" ou "excelente". Essa revisão é trabalho de falante pago sob as mesmas taxas — e também é um portão: falantes podem derrotar uma reivindicação de prêmio, e isso é por design.

## Como escala com competições

O modelo é construído para que a compensação de falantes cresça com a plataforma em vez de ser diluída por ela:

- **Cada novo idioma começa com um engajamento de corpus pago.** O custo de estabelecimento publicado por idioma ($3.350–8.500 tudo incluído) é principalmente compensação de falantes — o maior componente único, deliberadamente.
- **Cada novo pool de prêmios traz sua própria revisão paga.** Cada competição patrocinada que segue o [template de prêmios](/docs/specifications/prizes#4-future-prize-pools) carrega o mesmo requisito de validação comunitária, o que significa que cada competição financia trabalho de revisão de falantes para esse idioma.
- **Métodos implantados financiam revisão contínua.** Quando um método de propriedade comunitária ganha receita de API, 90% flui para a organização de governança da comunidade ([o modelo econômico](/docs/sovereignty/economic-model)), que pode financiar revisão contínua, crescimento de corpus e programas de idioma como achar adequado. Essa alocação é decisão da comunidade, não nossa.

## O que *não* prometemos

A honestidade requer marcar as bordas:

- As taxas acima são as taxas publicadas para o trabalho atual em Plains Cree. Taxas para idiomas futuros serão definidas com a comunidade parceira e publicadas da mesma forma — nas especificações, antes do trabalho começar.
- O ciclo virtuoso (receita → comunidade → mais trabalho pago) requer financiamento externo para começar e ainda não é autossustentável. O [modelo econômico](/docs/sovereignty/economic-model) descreve o mecanismo, não uma garantia.
- "Pago justamente" é necessário mas não suficiente. Pagamento por si só não torna um projeto não-extrativista — propriedade e controle fazem, é por isso que compensação fica dentro da [arquitetura de soberania](/docs/sovereignty/data-sovereignty) em vez de substituí-la.

---

## O que isso significa para você

:::info Se você é um membro da comunidade
Se você é bilíngue em um idioma pouco atendido e inglês, seu julgamento é a entrada mais valiosa neste sistema, e os termos publicados são: $50–65 CAD/hora, agendamento flexível, pagamento dentro de duas semanas, crédito nos seus termos, e o direito de retirar suas contribuições. Nenhuma programação é necessária. Comece com [Para Comunidades de Linguagem](/docs/community/for-language-communities) ou o [Protocolo de Validação de Falantes §7](/docs/specifications/speaker-validation#7-how-to-get-started).
:::

:::info Se você é um pesquisador
Orçamento compensação de falantes como um custo de pesquisa de primeira classe — os números publicados ($1.475–1.920 para uma rodada de validação de métrica; $2.500–6.000 para curadoria de corpus) são pequenos pelos padrões de bolsa e são o que torna pontuações automatizadas defensáveis. A [Estratégia de Parceria de Corpus](/docs/specifications/corpus-partnership) mostra como um departamento acadêmico se conecta a isso com trabalho de falante financiado integrado.
:::

:::info Se você é um construtor
Você se beneficia do trabalho de falante pago mesmo que nunca o financie: métricas validadas são o que torna sua pontuação de leaderboard significativa, e revisão comunitária paga é o que fica entre seu método e um prêmio. Se você vencer, espere que falantes tenham sido pagos para escrutinar sua saída — e espere que [propriedade do seu método seja transferida](/docs/sovereignty/ownership-transfer) para a comunidade cuja língua ele serve.
:::

## Veja também

- [Tradução Não É Revitalização](/docs/perspectives/translation-is-not-revitalization) — por que autoridade de falante enquadra tudo mais
- [Reportando Erros e Possuindo Correções](/docs/perspectives/reporting-errors-and-owning-corrections) — autoridade de falante após o benchmark, também
- [Especificação do Benchmark §10](/docs/specifications/benchmark#10-cost-framework) — o framework de custo completo de onde esses números vêm