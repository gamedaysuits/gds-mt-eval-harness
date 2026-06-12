---
sidebar_position: 2
title: "Transferência de Propriedade"
---
# Transferência de Propriedade

> **Resumo Executivo.** Quando um método de tradução atinge o nível Deployable (composite ≥ 0,70) e passa pela revisão comunitária, a propriedade do código é transferida do pesquisador para a organização de governança indígena. Esta página documenta o pipeline de transferência em cinco estágios, alinhamento com OCAP®, e orientações para pesquisadores desenvolvendo métodos para línguas indígenas.

Quando um método de tradução vence no leaderboard da Arena, o que acontece com o código? Para línguas indígenas e de baixos recursos, a resposta não é "o pesquisador fica com ele". A resposta é: **a comunidade é dona dele.**

---

## Como Funciona

A Arena impõe um pipeline claro da pesquisa para a propriedade comunitária:

### 1. Desenvolvimento do Método
Um pesquisador, estudante ou desenvolvedor constrói um método de tradução — um pipeline com FST-gating, um LLM treinado, um modelo fine-tuned, ou qualquer outra abordagem. Eles o desenvolvem usando seus próprios recursos.

### 2. Avaliação na Arena
O método é avaliado através do [harness de avaliação](/docs/specifications/harness). Cada submissão é fingerprinted para um commit Git específico e versão de dataset. Os scores são reproduzíveis.

### 3. Revisão Comunitária
Para métodos de línguas indígenas, os resultados são revisados por trabalhadores de língua comunitários e organizações de governança. Um score alto no leaderboard prova que o método *funciona*; não prova que é *apropriado*.

### 4. Transferência de Código
Quando um método atinge o nível **Deployable** (score composite ≥ 0,70 contra a avaliação gold-standard) **e** passa pela revisão comunitária (validação humana):
- O pesquisador entrega o código-fonte
- A propriedade legal é transferida para a organização de governança indígena (ex: um conselho tribal, autoridade de língua, ou organização Métis)
- A organização de governança detém as chaves de criptografia para datasets de avaliação
- O método se torna um ativo controlado pela comunidade

Veja a [Especificação de Scoring](/docs/specifications/scoring), §5 para definições de níveis de qualidade e a [Especificação de Benchmark](/docs/specifications/benchmark), §8.3 para as condições completas de transferência e §7 para o gate de validação humana.

### 5. Implantação em Produção
O método é exportado como um plugin [champollion](https://champollion.dev) e implantado na API de produção. A comunidade controla:
- Quem pode acessar o método
- Quais termos de preço se aplicam
- Se o método pode ser usado comercialmente
- Quando e como o método é atualizado

---

## Por Que Isso Importa

A pesquisa tradicional em ML segue um padrão extrativista:
1. Pesquisador coleta dados de uma comunidade
2. Pesquisador treina um modelo
3. Pesquisador publica um artigo
4. Comunidade não recebe nada

Este padrão agora opera em escala industrial. O OMT-1600 da Meta (março de 2026) treinou modelos de tradução para 1.600 línguas — incluindo línguas indígenas como Plains Cree — usando dados raspados da web e traduções da Bíblia. Os modelos foram treinados sem protocolos de consentimento comunitário, os pesos não estão atualmente disponíveis para download, e as comunidades cujas línguas foram modeladas não têm participação na propriedade, nenhum papel de governança, e nenhuma receita. O artigo é o produto. A comunidade é a fonte de dados.

A Arena inverte isso:
1. Pesquisador constrói um método
2. Arena valida contra corpora curados pela comunidade com métricas morfológicas
3. Comunidade recebe propriedade do código funcional
4. Comunidade ganha receita do uso da API

**Esta é a diferença fundamental entre Champollion e todos os outros esforços de MT para LRL, incluindo OMT-1600:** não apenas produzimos métodos para comunidades — transferimos propriedade de métodos *para* comunidades. O código, os pesos, a infraestrutura de implantação — tudo se torna propriedade comunitária. Isto não é um framework teórico — é o pipeline operacional para cada método de língua indígena na plataforma.

---

## Alinhamento com OCAP®

O processo de transferência de propriedade implementa diretamente os [princípios OCAP®](/docs/sovereignty/data-sovereignty):

| Princípio | Implementação |
|---|---|
| **Ownership** | A organização de governança detém o título do código do método e pesos do modelo |
| **Control** | A organização de governança controla termos de implantação, acesso e preço |
| **Access** | Membros da comunidade acessam o método através da API champollion ou download direto |
| **Possession** | Recursos linguísticos (dados de coaching, dicionários, regras FST) permanecem em infraestrutura controlada pela comunidade via método `api` |

---

## Para Pesquisadores

Se você está desenvolvendo um método para uma língua indígena:

1. **Estabeleça um relacionamento** com a comunidade de língua antes de começar
2. **Use dados com licença aberta** para desenvolvimento (não recursos restritos à comunidade)
3. **Documente a proveniência** em seu [run card](/docs/specifications/run-card) — liste cada recurso, sua licença e origem
4. **Esteja preparado para transferir** — se seu método for bem-sucedido, o código pertence à comunidade, não a você
5. **Isto é um recurso, não uma limitação** — sua contribuição é a arquitetura e técnica, que você pode publicar e reutilizar. A contribuição da comunidade é o conhecimento linguístico que faz funcionar para sua língua.

---

## Veja Também

- [Soberania de Dados](/docs/sovereignty/data-sovereignty) — princípios OCAP, CARE e Te Mana Raraunga
- [O Modelo Econômico](/docs/sovereignty/economic-model) — como propriedade se torna receita
- [Apoie uma Língua de Baixos Recursos](/docs/community/low-resource-languages) — o contexto de pesquisa