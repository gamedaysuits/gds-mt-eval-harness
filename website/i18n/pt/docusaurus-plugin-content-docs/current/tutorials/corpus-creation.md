---
sidebar_position: 11
title: "Guia Prático: Criação de Corpus"
---
# Guia de Criação de Corpus

> **A ideia:** Antes de avaliar um método de tradução, você precisa de um corpus de avaliação. Este guia cobre como construir um do zero — coleta de dados, requisitos de formato, padrões de qualidade, licenciamento e contribuição para a Arena.

:::info Isto não é um método de tradução
Este guia é um pré-requisito para muitos métodos. Um bom corpus de avaliação é a base que torna tudo mais possível. Até 50 pares curados são suficientes para abrir uma nova trilha no leaderboard.
:::

## Quando Usar Isto

- Você quer **adicionar um novo par de idiomas** ao leaderboard da Arena
- Você é um **professor de idiomas** que quer avaliar traduções de alunos
- Você é um **trabalhador de idioma comunitário** com acesso a materiais bilíngues
- Você é um **pesquisador** que precisa de um conjunto de avaliação padronizado para seu par de idiomas

## Formato do Corpus

O harness aceita JSON simples:

```json title="my-corpus.json"
{
  "metadata": {
    "name": "Quechua Dev v1",
    "version": "1.0.0",
    "source_language": "eng",
    "target_language": "que",
    "entry_count": 75,
    "license": "CC-BY-SA-4.0",
    "author": "Your Name / Organization",
    "description": "75 English-Quechua pairs from educational materials"
  },
  "entries": [
    {
      "id": 1,
      "source": "Hello, how are you?",
      "reference": "Allillanchu, imaynallan kashanki?"
    },
    {
      "id": 2,
      "source": "The sun is shining today",
      "reference": "Kunan p'unchay inti k'anchashan"
    }
  ]
}
```

## Onde Obter Dados

| Fonte | Qualidade | Volume | Licenciamento |
|--------|---------|--------|-----------|
| **Livros didáticos / materiais educacionais** | Alta (revisada por especialistas) | Baixa-média | Verifique com a editora |
| **Documentos governamentais** | Média (registro formal) | Média-alta | Frequentemente domínio público |
| **Dicionários bilíngues** | Alta (entradas verificadas) | Média | Varia |
| **Anciãos / falantes da comunidade** | Altíssima (intuição nativa) | Baixa (tempo limitado) | Governada pela comunidade |
| **Textos religiosos** | Média (específica do domínio) | Alta | Geralmente aberta |
| **Corpora existentes** (Hansard, FLORES) | Média-alta | Alta | Verifique a licença |
| **Criada manualmente** | Altíssima | Baixa | Você é o proprietário |

## Padrões de Qualidade

Um bom corpus de avaliação tem:

1. **Conteúdo diverso** — não apenas saudações ou frases simples. Inclua perguntas, comandos, frases complexas, termos específicos do domínio
2. **Traduções verificadas** — revisadas por pelo menos um falante fluente, idealmente dois
3. **Ortografia consistente** — um script, uma convenção de ortografia em todo o corpus
4. **Fontes independentes** — não derivadas do mesmo texto que os métodos usarão para treinamento
5. **Licenciamento claro** — licença explícita que permite uso em avaliação

:::danger Contaminação do corpus
O corpus de avaliação deve ser **independente** de qualquer dado de treinamento. Se um método foi treinado ou solicitado com dados do corpus de avaliação, ele será desqualificado. Projete seu corpus para ser mantido separado desde o início.
:::

## Diretrizes de Tamanho

| Tamanho | O Que Permite |
|------|----------------|
| **50 entradas** | Avaliação viável mínima — suficiente para detectar diferenças grosseiras de qualidade |
| **100–200 entradas** | Ranking confiável — suficiente para significância estatística entre métodos |
| **500+ entradas** | Nível de pesquisa — pontuações compostas robustas, intervalos de confiança |
| **1.000+ entradas** | Padrão ouro — equivalente à cobertura do devtest do FLORES |

Comece pequeno. 50 entradas são suficientes para abrir uma trilha no leaderboard. Você pode expandir depois.

## Contribuindo para a Arena

1. **Crie seu corpus** no formato JSON acima
2. **Licencie-o** — CC BY-SA 4.0 é recomendado para avaliação aberta; CC BY-NC-SA 4.0 para uso restrito
3. **Envie um PR** para o [repositório do harness de avaliação](https://github.com/gamedaysuits/arena) com seu corpus em `data/`
4. **O leaderboard abre automaticamente** para seu par de idiomas assim que o corpus é mesclado

## Para Comunidades de Idiomas Indígenas

A criação de corpus é um ato de **soberania linguística**. Seu corpus, seus termos:

- Você decide a licença e as condições de acesso
- Você pode contribuir com um **conjunto de desenvolvimento público** (para desenvolvimento de métodos) enquanto mantém um **conjunto de teste secreto** (para avaliação oficial) sob controle da comunidade
- O [framework de soberania](/docs/sovereignty/data-sovereignty) protege seus dados em todos os níveis

Até um corpus pequeno é um **ativo estratégico** — é o benchmark que decide o que significa "bom o suficiente" para seu idioma.

## Combina Bem Com

- **[Tradução Parcial](./partial-translation)** — criar um corpus É a etapa de tradução humana
- **[Retro-tradução](./back-translation)** — dados sintéticos complementam corpora criados por humanos
- Todos os outros cookbooks — todos precisam de um corpus de avaliação

## Veja Também

- [Conjuntos de Dados de Avaliação](/docs/leaderboard/datasets) — corpora existentes (EDTeKLA, FLORES+)
- [Soberania de Dados](/docs/sovereignty/data-sovereignty) — propriedade e controle
- [Para Comunidades de Idiomas](/docs/community/for-language-communities) — engajamento comunitário
- [Apoiar um Idioma de Baixos Recursos](/docs/community/low-resource-languages) — a visão geral