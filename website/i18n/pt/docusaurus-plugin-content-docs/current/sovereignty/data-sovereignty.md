---
sidebar_position: 7
title: "Soberania de Dados"
description: "Princípios OCAP, CARE e Māori Data Sovereignty para tradução de línguas indígenas. Por que o consentimento da comunidade vem antes da implantação."
related:
  - label: "Ownership Transfer"
    to: /docs/sovereignty/ownership-transfer
    kind: doc
    note: "How control of language data moves to communities"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
---
# Soberania de Dados

> **Resumo Executivo.** Esta página explica os princípios de soberania de dados OCAP®, CARE e Te Mana Raraunga e o que eles significam para desenvolvedores que criam métodos de tradução para línguas indígenas. Aborda quando o consentimento da comunidade é necessário, como a arquitetura do método `api` do champollion suporta soberania de dados, e as obrigações éticas de qualquer pessoa que trabalhe com dados linguísticos indígenas.

A tradução automática para línguas indígenas levanta questões que não existem para francês ou japonês. Quem é dono dos dados de treinamento? Quem controla como um modelo de linguagem fala? Quem decide se uma tradução é boa o suficiente para publicar?

**A resposta é sempre a comunidade.**

O champollion foi construído para apoiar isso. O método `api` mantém todos os recursos linguísticos no servidor sob controle da comunidade. O sistema de plugins separa o método da ferramenta. Mas a ferramenta não pode impor ética — esta página explica os princípios que você deve seguir.

---

## Princípios OCAP®

**OCAP** (Ownership, Control, Access, Possession) é um conjunto de princípios desenvolvido pelo [First Nations Information Governance Centre](https://fnigc.ca/ocap-training/) (FNIGC) que estabelecem como os dados das Primeiras Nações devem ser coletados, protegidos, usados e compartilhados.

| Princípio | O que Significa para Tradução |
|-----------|------------------------------|
| **Ownership** | A comunidade é dona de seus dados linguísticos — dicionários, gramáticas, textos paralelos, arquivos de coaching e qualquer tradução produzida a partir deles. |
| **Control** | A comunidade controla como seus dados de linguagem são usados, quem tem acesso e quais métodos de tradução são aceitáveis. |
| **Access** | Membros da comunidade têm o direito de acessar e gerenciar seus próprios recursos linguísticos independentemente de onde estejam armazenados. |
| **Possession** | Os dados físicos (arquivos de coaching, dicionários, pesos do modelo) devem residir em infraestrutura que a comunidade controla — não em nuvem de terceiros. |

### O que OCAP significa na prática

- **Não publique traduções** de uma língua indígena sem autorização explícita da comunidade.
- **Não treine modelos** em dados linguísticos fornecidos pela comunidade sem um acordo de compartilhamento de dados.
- **Não faça scraping** de recursos linguísticos da comunidade em sites, redes sociais ou materiais educacionais.
- **Use o método `api`** para que prompts, dados de coaching e dicionários permaneçam em servidores controlados pela comunidade. O método `api` do champollion é um "cano burro" — envia chaves e recebe traduções de volta. Toda a propriedade intelectual linguística fica no servidor.
- **Documente a proveniência** — o campo `provenance` no [manifesto do plugin](https://champollion.dev/docs/reference/plugin-spec) deve listar cada recurso usado, sua licença e sua origem.

:::warning OCAP® é uma marca registrada
OCAP® é uma marca registrada do First Nations Information Governance Centre. Aplica-se especificamente às Primeiras Nações no Canadá. Os princípios têm relevância mais ampla, mas a marca registrada e a autoridade de governança pertencem ao FNIGC.
:::

---

## Princípios CARE

Os **Princípios CARE para Governança de Dados Indígenas** foram desenvolvidos pela [Global Indigenous Data Alliance](https://www.gida-global.org/care) (GIDA) como complemento aos princípios de dados FAIR. FAIR diz que dados devem ser Findable, Accessible, Interoperable e Reusable. CARE diz que isso não é suficiente — a governança de dados também deve centralizar os direitos indígenas.

| Princípio | Aplicação |
|-----------|------------|
| **Collective Benefit** | Ferramentas de tradução devem beneficiar a comunidade linguística em primeiro lugar. Pontuações em leaderboards são um meio para melhorar métodos, não para extrair valor comercial de línguas comunitárias. |
| **Authority to Control** | Comunidades têm autoridade para governar como seus dados de linguagem são coletados, usados e compartilhados. Uma pontuação alta no leaderboard não concede permissão para publicar traduções. |
| **Responsibility** | Pesquisadores e desenvolvedores que trabalham com dados de línguas indígenas têm responsabilidade de construir relacionamentos, obter consentimento e compartilhar benefícios. |
| **Ethics** | Os direitos e bem-estar dos povos indígenas devem ser a preocupação primária. Métodos de tradução devem ser desenvolvidos *com* comunidades, não *sobre* elas. |

---

## Te Mana Raraunga — Soberania de Dados Māori

**Te Mana Raraunga** é a [Māori Data Sovereignty Network](https://www.temanararaunga.maori.nz/). Ela afirma que dados Māori — incluindo dados de linguagem — são um taonga (tesouro) sujeito aos princípios do Tratado de Waitangi e tikanga Māori (lei consuetudinária Māori).

Princípios-chave:

| Princípio | Significado |
|-----------|---------|
| **Rangatiratanga** (Autoridade) | Māori têm direito inerente de exercer autoridade sobre seus dados, incluindo dados de linguagem. |
| **Whakapapa** (Relacionamentos) | Dados têm origens e conexões. Dados de linguagem carregam os relacionamentos e conhecimento das pessoas que os criaram. |
| **Whanaungatanga** (Obrigações) | Aqueles que detêm ou processam dados Māori têm obrigações recíprocas com as comunidades de origem. |
| **Kotahitanga** (Benefício coletivo) | Dados Māori devem ser usados para o benefício coletivo de Māori. |
| **Manaakitanga** (Reciprocidade) | O uso de dados Māori deve envolver cuidado, respeito e reciprocidade. |
| **Kaitiakitanga** (Guardiania) | Guardiões de dados têm dever de proteger os dados e garantir que sejam usados apropriadamente. |

Esses princípios se aplicam a te reo Māori (a língua Māori) e a qualquer trabalho computacional envolvendo dados da língua Māori.

---

## O que Isso Significa para Usuários do champollion

### Para línguas padrão (francês, japonês, espanhol...)

Use o champollion normalmente. Essas línguas têm grandes corpora publicamente disponíveis, APIs de tradução estabelecidas e nenhuma preocupação de soberania. Traduza, sincronize e publique como desejar.

### Para línguas indígenas e de baixo recurso

A situação é fundamentalmente diferente:

1. **Obtenha consentimento primeiro.** Antes de construir um método de tradução para uma língua indígena, estabeleça um relacionamento com a comunidade. Um método construído sem envolvimento da comunidade — não importa quão tecnicamente impressionante — não deve ser publicado ou distribuído.

2. **Use o método `api`.** Hospede o pipeline de tradução em infraestrutura controlada pela comunidade. O método `api` no champollion foi projetado para isso: envia chaves e recebe traduções de volta sem expor os prompts, dicionários ou dados de coaching que fazem o método funcionar.

    ```json title="Community-controlled setup"
    {
      "pairs": {
        "en:crk": {
          "method": "api",
          "endpoint": "https://api.community-server.example/translate"
        }
      }
    }
    ```

3. **Documente tudo.** Use o campo `provenance` no seu manifesto de plugin para listar cada recurso, sua licença e se foi fornecido com consentimento da comunidade.

4. **Pontuações não são licenças.** Uma pontuação alta no leaderboard prova que um método funciona bem tecnicamente. Não concede permissão para publicar traduções, distribuir o plugin ou comercializar o método. A comunidade decide.

5. **Compartilhe o método, não os dados.** Se você desenvolver uma técnica que funciona bem (por exemplo, "LLM com gate FST e prompts coached"), compartilhe a *arquitetura* e *abordagem* no leaderboard. A comunidade retém controle sobre os dados linguísticos que a fazem funcionar para sua língua específica.

---

## O Método `api` e Soberania

O [método de tradução](https://champollion.dev/docs/guides/translation-methods) `api` existe especificamente para apoiar soberania de dados. Aqui está o porquê:

| Aspecto | Outros Métodos | Método `api` |
|--------|--------------|-------------|
| **Onde prompts vivem** | Nos arquivos de config do champollion (visíveis para todos os desenvolvedores) | No servidor da comunidade (privado) |
| **Onde dados de coaching vivem** | No diretório `.champollion/coaching/` (commitado no git) | No servidor da comunidade (privado) |
| **Onde dicionários vivem** | No diretório do plugin (distribuído com o plugin) | No servidor da comunidade (privado) |
| **Quem controla o pipeline** | Quem executa `champollion sync` | A comunidade que opera a API |
| **O que champollion vê** | Tudo | Chaves dentro, traduções fora |

O método `api` é uma escolha arquitetônica deliberada. É um "cano burro" porque a propriedade intelectual — o conhecimento linguístico, as regras de gramática, os exemplos de coaching cuidadosamente curados — pertence à comunidade, não à ferramenta.

Veja [Serving a Method via API](https://champollion.dev/docs/guides/serving-a-method) para detalhes de implementação.

---

## Estudo de Caso: OMT-1600 e Soberania de Dados

O OMT-1600 da Meta (março de 2026) fornece um exemplo concreto de por que soberania de dados importa para línguas indígenas. O OMT-1600 treinou modelos de tradução para 1.600 línguas usando:

- **CC-2000-Web**: Texto monolíngue coletado por web scraping de 2.000+ languoides — coletado sem consentimento da comunidade
- **Traduções da Bíblia**: Textos religiosos usados como dados de treinamento paralelo e avaliação para as línguas com menor recurso
- **MeDLEy**: Bitext manualmente curado — mas sem conformidade OCAP® ou CARE documentada
- **Dados sintéticos retrotraduzidos**: ~270 milhões de sentenças paralelas sintéticas geradas pelos próprios modelos

Para línguas indígenas como Plains Cree (CRK), isso significa:

| Princípio | Prática OMT-1600 | Impacto |
|-----------|-------------------|--------|
| **Ownership** | Meta é dona dos modelos e decide como liberá-los | Comunidade não tem participação na propriedade de como sua língua é modelada |
| **Control** | Meta controla seleção de dados de treinamento, arquitetura do modelo e cronograma de lançamento | Comunidade não tem entrada em quais dados são usados ou como a língua é representada |
| **Access** | Pesos do modelo não estão disponíveis atualmente — "não lançados devido a fatores fora do controle dos autores" | Comunidade não pode acessar, inspecionar ou modificar o modelo que fala sua língua |
| **Possession** | Todos os dados e modelos residem em infraestrutura da Meta | Comunidade não pode hospedar, auditar ou deletar os dados usados para treinar o modelo |

OMT-1600 é uma realização de pesquisa. É também um exemplo de prática extrativista de dados: dados linguísticos foram coletados da web e textos religiosos, processados em um modelo e publicados como um artigo — tudo sem envolvimento, consentimento ou compartilhamento de benefícios da comunidade.

**Este é exatamente o padrão que a arquitetura de soberania do champollion previne.** O método `api` mantém propriedade intelectual linguística em servidores controlados pela comunidade. Corpora de avaliação são fornecidos com consentimento da comunidade e armazenados sob custódia de chaves da comunidade. Métodos vencedores de prêmios são transferidos para propriedade da comunidade. A diferença não é técnica — é ética e estrutural.

:::note OMT-1600 não é uniquamente culpado
Este padrão — web scraping seguido de treinamento de modelo sem consentimento da comunidade — é prática padrão em pesquisa de PNL massivamente multilíngue. OMT-1600 é um estudo de caso por causa de sua escala (1.600 línguas) e recência (março de 2026), não porque é uniquamente extrativista. A mesma crítica se aplica a NLLB-200, esforços multilíngues do Google e a maioria da pesquisa de MT em larga escala.
:::

---

## Leitura Adicional

- [First Nations Information Governance Centre — OCAP®](https://fnigc.ca/ocap-training/)
- [Global Indigenous Data Alliance — CARE Principles](https://www.gida-global.org/care)
- [Te Mana Raraunga — Māori Data Sovereignty Network](https://www.temanararaunga.maori.nz/)
- [USIDSN — United States Indigenous Data Sovereignty Network](https://usindigenousdata.org/)

---

## Veja Também

- [Support a Low-Resource Language](/docs/community/low-resource-languages) — o guia técnico com contexto OCAP
- [Translation Methods](https://champollion.dev/docs/guides/translation-methods) — o método `api` e como protege propriedade intelectual
- [Serving a Method via API](https://champollion.dev/docs/guides/serving-a-method) — hospedando um pipeline controlado pela comunidade
- [Plugin Specification](https://champollion.dev/docs/reference/plugin-spec) — o campo `provenance` para atribuição de recursos
- [Cookbook: FST-Gated Pipeline](/docs/tutorials/fst-gated-pipeline) — construindo um pipeline que uma comunidade pode auto-hospedar