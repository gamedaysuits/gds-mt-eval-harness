---
sidebar_position: 3
title: "Do Benchmark ao Uso Diário: O Caminho da Pós-Edição"
slug: '/perspectives/from-benchmark-to-daily-use'
description: "Como um método de tradução avaliado em benchmark se torna um fluxo de trabalho de tradução comunitária: rascunho automático, pós-edição por falante fluente, texto publicado — com limites de qualidade honestos em cada etapa."
related:
  - label: "Deploy to Production"
    to: /docs/getting-started/deploy-to-production
    kind: guide
    note: "From proven method to live translation"
  - label: "Cookbook: Partial Translation (Human + Machine)"
    to: /docs/tutorials/partial-translation
    kind: cookbook
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "The quality thresholds behind the path"
  - label: "Translation Is Not Revitalization"
    to: /docs/perspectives/translation-is-not-revitalization
    kind: position
---
# Do Benchmark ao Uso Diário: O Caminho da Pós-Edição

> **A versão resumida.** Uma pontuação em leaderboard não é um produto. O caminho de "este método marca 0,78" para "o escritório da comunidade publica documentos no idioma toda semana" passa por exatamente um fluxo de trabalho: a máquina produz um rascunho, um falante fluente o corrige, e apenas o texto corrigido é publicado. Cada limite de qualidade em nossas especificações é calibrado para esse fluxo de trabalho — não para saída de máquina não supervisionada, que não endossamos para nenhum idioma nesta plataforma.

Às vezes as pessoas perguntam quando um método de tradução será "bom o suficiente para apenas usar". Para os idiomas que esta Arena serve, essa pergunta tem uma armadilha. A resposta honesta é que o limite que vale a pena buscar não é "bom o suficiente para publicar sem revisão" — é **"bom o suficiente para que revisar um rascunho seja melhor que traduzir do zero."** Esse limite é muito mais baixo, é mensurável, e cruzá-lo muda o que um escritório de tradução comunitário pode produzir em uma semana.

---

## O fluxo de trabalho, de ponta a ponta

```
 English source document
        │
        ▼
 Machine draft  ←  a benchmarked, community-owned method
        │
        ▼
 Fluent-speaker post-edit  ←  the human gate; nothing skips it
        │
        ▼
 Published text  ←  carries human approval, not a machine score
        │
        ▼
 (Optional, community-controlled) corrections become
 data that improves the next version of the method
```

Três coisas a notar:

1. **A máquina nunca publica.** A unidade de saída é um rascunho. A passagem de correção do falante não é garantia de qualidade colada no final — é o fluxo de trabalho.
2. **O tempo do falante é o recurso sendo otimizado.** Um método é melhor que outro método exatamente na medida em que deixa menos para o falante corrigir. Pesquisas sobre pós-edição para idiomas bem-dotados de recursos consistentemente encontram ser mais rápido que traduzir do zero em qualidade MT moderada (Plitt & Masselot 2010; Green, Heer & Manning 2013, ambos citados com links em [Translation Is Not Revitalization](/docs/perspectives/translation-is-not-revitalization)). Se isso se mantém para idiomas polissintéticos é precisamente o que o benchmark existe para descobrir — tratamos como uma hipótese a verificar por idioma, não uma suposição.
3. **O loop de feedback é de propriedade da comunidade.** Cada documento corrigido é potencial dado de treinamento e coaching — e pertence à comunidade, para realimentar (ou não) em seus próprios termos sob as regras de [data sovereignty](/docs/sovereignty/data-sovereignty). O mecanismo de feedback é um objetivo de design da plataforma, ainda não um recurso construído; veja [Reporting Errors and Owning Corrections](/docs/perspectives/reporting-errors-and-owning-corrections) para como correções e proveniência devem funcionar.

## O que os níveis de qualidade significam para uso real

O leaderboard avalia métodos em um composto de métricas automatizadas ([Scoring Specification](/docs/specifications/scoring)), e as pontuações mapeiam para níveis nomeados. Aqui está a tradução honesta desses níveis em termos de uso diário:

| Nível (composto) | O que significa para o caminho da pós-edição |
|---|---|
| **Baseline** (0,00–0,30) | Não utilizável para nada. A saída é em grande parte não o idioma alvo. Útil apenas como piso de pesquisa. |
| **Emerging** (0,30–0,50) | Ainda não é uma ferramenta de rascunho. Fragmentos corretos aparecem, mas um falante gastaria mais tempo corrigindo que escrevendo do zero. |
| **Functional** (0,50–0,70) | O primeiro nível onde pós-edição *pode* ser melhor que tradução do zero para textos fáceis — vale a pena pilotar com um falante, não vale a pena depender. Erros morfológicos frequentes permanecem. |
| **Deployable** (0,70–0,85) | O nível alvo para o fluxo de trabalho acima: rascunhos onde a maioria da morfologia está correta e um falante fluente pode corrigir significativamente mais rápido que retraduzir. **"Deployable" significa deployable *em um fluxo de trabalho de pós-edição* — nunca "publicar sem revisão."** |
| **Fluent** (0,85–1,00) | Aproximando-se de tradução humana competente; erros raros e menores. A passagem de revisão permanece — apenas fica mais rápida. |

Duas regras de honestidade estrutural ficam no topo desta tabela, direto da [Benchmark Specification §5 e §7](/docs/specifications/benchmark#5-quality-tiers):

- **Níveis automatizados são rótulos provisórios, não vereditos.** São indicações para revisão humana. Os limites serão recalibrados conforme dados de validação de falantes se acumulam, e podem cair diferentemente para idiomas diferentes.
- **Nenhum método pode reivindicar Deployable ou acima sem revisão comunitária.** Uma amostra estratificada de sua saída vai para falantes bilíngues, que avaliam cada tradução como *reject / gist / acceptable / excellent*. A organização de governança — não o leaderboard — decide se o método avança.

Para comparação, o limite do [Founder's Prize](/docs/specifications/prizes) (composto ≥ 0,80, ≥99% palavras morfologicamente válidas, ≥70% falantes avaliando acceptable-or-better) descreve um método cujos erros restantes são *erros de linguagem real* — inflexão errada, não palavras fabricadas. É assim que "um rascunho que vale o tempo de um falante" se parece em números.

## De um método vencedor para um escritório funcionando

Suponha que um método ultrapasse esses portões. Os passos restantes são organizacionais, e são especificados em vez de improvisados:

1. **A propriedade é transferida.** O código do método se torna propriedade da organização de governança da comunidade — o desenvolvedor mantém direitos de atribuição e publicação ([Ownership Transfer](/docs/sovereignty/ownership-transfer)).
2. **O método se torna um serviço.** É empacotado como um plugin e servido através da plataforma de deployment, com a comunidade controlando acesso, preços e usos permitidos ([Deploy to Production](/docs/getting-started/deploy-to-production)).
3. **Tradutores o conectam ao seu dia.** Um escritório de tradução aponta seu fluxo de trabalho de documento existente para a API do método: texto de origem entra, rascunho sai, pós-edita, publica. O texto publicado carrega o nome e autoridade do tradutor — a máquina é uma ferramenta na sua mesa, como um dicionário.
4. **A receita segue o uso.** Desenvolvedores externos que usam o método pagam taxas medidas, e 90% dessa receita flui para a organização de governança ([The Economic Model](/docs/sovereignty/economic-model)) — que pode financiar mais horas de tradutor, fechando o loop.

## Onde isso está hoje

Claramente: o caminho completo é especificado de ponta a ponta, e parcialmente construído. O harness de avaliação, métricas, run cards e leaderboard público existem; o corpus de desenvolvimento Plains Cree e um prêmio ativo existem; a plataforma de deployment existe. A interface de revisão comunitária, a sandbox de avaliação e o loop de realimentação de texto corrigido são especificados mas ainda não operacionais — as especificações os marcam como planejados, e nós também. Nenhum método completou ainda a jornada inteira do benchmark ao uso diário comunitário. Essa jornada é a definição de sucesso do projeto, que é exatamente por que não a reivindicaremos cedo.

---

## O que isso significa para você

:::info Se você é um membro da comunidade
Um badge "Deployable" no leaderboard nunca significa que uma máquina publicará no seu idioma sem supervisão — significa que um gerador de rascunho pode estar pronto para *fazer uma audição* para seus tradutores, em seus termos, com seus falantes como juízes (pagos — veja [How Speakers Get Paid](/docs/perspectives/how-speakers-get-paid)). Se sua comunidade executa um escritório de tradução, a pergunta relevante a nos trazer é: "como seria um piloto, e quem revisa a saída?"
:::

:::info Se você é um pesquisador
O enquadramento de pós-edição muda o que vale a pena medir: tempo para texto aceitável com um falante no loop, não apenas pontuação composta. As métricas da Arena são proxies para isso ([Scoring Specification §1](/docs/specifications/scoring)), e estudos de pós-edição por idioma para idiomas morfologicamente complexos são uma lacuna de pesquisa aberta que esta infraestrutura é projetada para apoiar.
:::

:::info Se você é um construtor
Otimize para o editor, não para a métrica. Um método que produz palavras reais com inflexões ocasionalmente erradas é corrigível em segundos por um falante; um método que alucina formas plausíveis envenena todo o fluxo de trabalho — é por isso que a validade morfológica é tão rigorosamente controlada aqui. Comece em [Submit a Method](/docs/getting-started/submit-a-method), e leia [Method Interface](/docs/specifications/methods) para o que você eventualmente entregará se vencer.
:::

## Veja também

- [Translation Is Not Revitalization](/docs/perspectives/translation-is-not-revitalization) — por que o portão humano é o ponto, não uma limitação
- [Reporting Errors and Owning Corrections](/docs/perspectives/reporting-errors-and-owning-corrections) — o que acontece quando o texto publicado está errado mesmo assim
- [Benchmark Specification §7](/docs/specifications/benchmark#7-human-validation) — o portão de validação humana, formalmente