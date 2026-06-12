---
sidebar_position: 5
title: "Apoiar um Idioma com Poucos Recursos"
related:
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "The first step for an uncovered language"
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
  - label: "Plains Cree, the trading card"
    to: https://champollion.dev/trading-cards?q=crk
    kind: card
    note: "The proof-of-concept language, as a card"
---
# Apoiar uma Língua de Baixo Recurso

> **Resumo Executivo.** Um guia abrangente para construir tradução automática para línguas de baixo recurso e polissintéticas. Cobre por que essas línguas são difíceis (complexidade morfológica, dados esparsos, alucinação), recursos computacionais existentes (ALTLab FST, GiellaLT, Apertium, UniMorph, EdTeKLA), 10+ estratégias de abordagem, o sistema de coaching champollion e o loop de avaliação. Comece aqui se você quer contribuir com um método para uma língua pouco atendida.

:::info Status: Em Desenvolvimento Ativo
O suporte para Plains Cree (nêhiyawêwin) está atualmente em desenvolvimento. As ferramentas, o harness de avaliação e o leaderboard descritos aqui são reais e utilizáveis hoje, mas o pipeline de tradução para Cree ainda não foi lançado. Quando for, isso servirá como modelo para outras línguas polissintéticas e de baixo recurso com infraestrutura FST.
:::

## O Problema Não Resolvido

Google Translate suporta ~130 línguas. O OMT-1600 da Meta (março de 2026) afirma cobertura para 1.600 — o maior sistema de MT já publicado. Mas para as ~1.300 línguas em seus níveis de recurso mais baixos, a qualidade está abaixo de limiares utilizáveis, os dados de treinamento são dominados por texto bíblico, os pesos do modelo não estão disponíveis para download, e não há avaliação independente ou framework de governança comunitária. Para as ~5.400 línguas restantes, nenhum modelo pré-treinado produz qualquer saída.

A paisagem mudou significativamente — Big Tech agora está investindo em cobertura de LRL. Mas cobertura não é qualidade, e qualidade sem verificação independente não é confiança. Línguas de baixo recurso precisam de mais do que um modelo que afirma cobri-las — elas precisam de avaliação independente com validação morfológica, corpora curados pela comunidade e governança que respeita a soberania.

**champollion foi construído para mudar isso.**

O [Method Leaderboard](https://champollion.dev/leaderboard) é um desafio aberto: construa o melhor método de tradução para uma língua pouco atendida, prove-o com avaliação reproduzível e reivindique o melhor score. Qualquer pessoa no mundo pode contribuir — linguistas, pesquisadores de ML, trabalhadores de línguas comunitárias, estudantes, entusiastas. O problema não está resolvido. A infraestrutura está aqui. O leaderboard está esperando.

---

## Por Que Isso É Difícil: Morfologia Polissintética

A maioria dos sistemas de MT comerciais foi projetada para línguas como inglês, francês e chinês — línguas onde as palavras são relativamente curtas e as frases são construídas a partir de tokens discretos. Mas muitas línguas indígenas, incluindo Plains Cree, são **polissintéticas**: uma única palavra pode codificar o que o inglês expressa como uma frase inteira.

### O exemplo Cree

Considere a palavra Plains Cree:

> **ê-kî-nitawi-kîskinwahamâkosiyân**
> *"when I went to school"*

Essa é **uma palavra**. Ela codifica tempo (passado), direção (indo para), a raiz (aprender), voz (passiva/reflexiva) e pessoa (primeira singular). Um LLM treinado predominantemente em inglês não tem intuição para esse tipo de densidade morfológica.

Os desafios se acumulam:

| Desafio | O Que Significa |
|---------|-----------------|
| **Complexidade morfológica** | Uma única raiz verbal pode gerar milhares de formas flexionadas válidas através de prefixação, sufixação e circunfixação |
| **Distinção animado/inanimado** | Nomes são gramaticalmente animados ou inanimados — isso afeta conjugação verbal, demonstrativos e pluralização. A classificação nem sempre segue animacidade biológica (*askiy* "terra" é animado; *maskisin* "sapato" também é animado) |
| **Obviation** | Referências de terceira pessoa são classificadas por proximidade/saliência. A distinção "proximal" e "obviativo" não tem equivalente em inglês |
| **Dados de treinamento esparsos** | LLMs viram muito pouco texto Plains Cree. O que viram pode misturar dialetos (dialeto Y, dialeto TH) ou ortografias (SRO vs. silábicos) |
| **Baseline comercial fraco** | OMT-1600 inclui CRK no nível R1 (Recurso Muito Baixo) com treinamento em domínio bíblico e tokenização BPE padrão. Google Translate não suporta Cree. Avaliação independente com métricas morfológicas é o que torna esses baselines significativos. |

A tradução de línguas polissintéticas permanece um **problema de pesquisa aberto** — OMT-1600 inclui línguas polissintéticas mas usa tokenização BPE padrão (vocabulário de 256K) sem consciência morfológica, o que significa que despedaça palavras composicionais em fragmentos de bytes sem sentido.

---

## Trabalho Anterior: Como as Pessoas Abordaram Isso

### O FST ALTLab

O recurso computacional mais significativo para Plains Cree é o **transdutor de estado finito (FST)** desenvolvido pelo [Alberta Language Technology Lab (ALTLab)](https://altlab.artsrn.ualberta.ca/) da Universidade de Alberta, em colaboração com [Giellatekno](https://giellatekno.uit.no/) da UiT The Arctic University of Norway.

O FST ALTLab é um **analisador e gerador morfológico**: dada uma palavra Cree flexionada, ele pode decompô-la em sua raiz e tags gramaticais, e dada uma raiz mais tags, ele pode gerar a forma flexionada correta. Isso é determinístico — sem rede neural, sem alucinação, sem probabilidade. Se o FST aceita uma palavra, essa palavra é morfologicamente válida em Cree.

É por isso que o leaderboard champollion rastreia **FST Acceptance Rate** como uma métrica. Um método de tradução que produz palavras que o FST rejeita está produzindo Cree morfologicamente inválido — independentemente do que o score chrF++ diz.

**Recursos-chave do ALTLab:**
- [itwêwina](https://itwewina.altlab.app/) — um dicionário Plains Cree–inglês inteligente alimentado pelo FST
- [Morphodict](https://github.com/UAlbertaALTLab/morphodict) — plataforma de dicionário de código aberto com consciência morfológica
- [crk-db](https://github.com/UAlbertaALTLab/crk-db) — banco de dados léxico Plains Cree
- [21st Century Tools for Indigenous Languages](https://21c.tools/) — o contexto do projeto mais amplo

### Registros FST e Morfológicos Globais

Plains Cree não é a única língua com infraestrutura FST de alta qualidade. Se você quer desenvolver pipelines de tradução para outras línguas de baixo recurso ou morfologicamente complexas, você pode aproveitar esses hubs globais estabelecidos:

* **[GiellaLT / Giellatekno](https://giellalt.github.io/) (UiT The Arctic University of Norway):** O maior repositório de analisadores e geradores morfológicos FST de código aberto, cobrindo mais de 100 línguas. Áreas de foco incluem línguas Sámi (`sme`, `smj`, `sma`, etc.), línguas Urálicas (Komi, Erzya, Udmurt, etc.) e outras línguas minoritárias/indígenas. Eles hospedam corpora de texto processado público (`corpus-xxx`) em sua [Organização GitHub](https://github.com/giellalt/).
* **[The Apertium Project](https://www.apertium.org/):** Uma plataforma de tradução automática baseada em regras de código aberto. Apertium mantém analisadores morfológicos FST altamente otimizados (usando `lttoolbox` e `hfst`) e dicionários bilíngues para dezenas de línguas, incluindo um grande conjunto de línguas Túrquicas (Cazaque, Tatar, Quirguiz, etc.) e línguas europeias minoritárias. Todos os recursos são públicos no [GitHub do Apertium](https://github.com/apertium).
* **[UniMorph (Universal Morphology)](https://unimorph.github.io/):** Um projeto colaborativo fornecendo paradigmas morfológicos padronizados para mais de 150 línguas. O dataset é hospedado no Hugging Face em [unimorph/universal_morphologies](https://huggingface.co/datasets/unimorph/universal_morphologies). Se um binário FST compilado não estiver disponível para uma língua, tabelas UniMorph podem ser usadas como um gate de busca em banco de dados estático.
* **[National Research Council Canada (NRC)](https://nrc-digital-repository.canada.ca/):** Oferece ferramentas para línguas indígenas canadenses, incluindo o analisador morfológico FST **Uqailaut** Inuktitut e o massivo **Nunavut Hansard Parallel Corpus** (1,3M pares de frases alinhadas inglês-inuktitut).

### O Corpus EdTeKLA

O grupo de pesquisa [EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) (também na UAlberta) montou um corpus de língua Plains Cree a partir de materiais educacionais, transcrições de áudio e fontes comunitárias. O dataset de avaliação champollion [EDTeKLA Dev v1](/docs/leaderboard/datasets) é derivado deste trabalho, licenciado [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

### Outras abordagens que as pessoas tentaram ou poderiam tentar

O leaderboard é agnóstico em relação ao método. Aqui estão estratégias que foram exploradas ou propostas para MT de baixo recurso, qualquer uma das quais poderia ser submetida:

| Abordagem | Como Funciona | Prós | Contras |
|-----------|---------------|------|---------|
| **[Coached LLM prompting](/docs/tutorials/coached-llm-prompting)** | Injete regras de gramática, dicionários e pares de exemplo no system prompt | Rápido para iterar, sem treinamento necessário | Teto de qualidade limitado pelo conhecimento base do LLM |
| **[Few-shot prompting](/docs/tutorials/few-shot-prompting)** | Inclua traduções verificadas como exemplos em contexto | Bom para estilo consistente | Janela de contexto pequena; exemplos NÃO devem vir dos dados de avaliação |
| **[FST-gated pipeline](/docs/tutorials/fst-gated-pipeline)** | LLM gera → FST valida → rejeita e tenta novamente morfologia inválida | Garante validade morfológica | Requer infraestrutura FST; loops de retry adicionam latência e custo |
| **[Dictionary lookup + LLM](/docs/tutorials/dictionary-augmented-llm)** | Force termos conhecidos de um dicionário bilíngue, deixe o LLM lidar com o resto | Reduz alucinação para termos conhecidos | Cobertura de dicionário é sempre incompleta |
| **[Fine-tuned model](/docs/tutorials/fine-tuned-model)** | Fine-tune um modelo aberto (Llama, Mistral) em texto paralelo — apenas não nos dados de avaliação | Potencialmente a mais alta qualidade | Requer corpus paralelo (escasso); caro; risco de overfitting |
| **[Chained models](/docs/tutorials/chained-models)** | Modelo A gera tradução aproximada → Modelo B pós-edita → Modelo C pontua | Pode combinar forças de especialistas | Complexo; lento; caro |
| **[Rule-based + LLM hybrid](/docs/tutorials/rule-based-hybrid)** | Use regras linguísticas para padrões conhecidos, LLM para tudo mais | Preciso onde as regras se aplicam | Requer expertise linguística profunda |
| **[Back-translation augmentation](/docs/tutorials/back-translation)** | Gere dados paralelos sintéticos traduzindo Cree→inglês, depois treine no reverso | Expande dados de treinamento barato | Amplifica erros do modelo existente |
| **[Evolutionary approach](/docs/tutorials/evolutionary-approach)** | Gere traduções candidatas, pontue-as, mute os melhores performers, repita | Pode descobrir soluções novas; paralelizável | Computacionalmente caro; precisa de uma boa função de fitness |
| **[Partial translation](/docs/tutorials/partial-translation)** | Traduza manualmente uma amostra representativa, prove que seu método corresponde ao seu estilo nela, depois auto-traduza o restante em massa | Combina qualidade humana com escala de máquina | Requer esforço humano inicial |
| **Manual JSON / exam grading** | Crie manualmente um arquivo JSON de dataset para testar respostas de alunos em um exame de língua, ou classifique um lote de traduções humanas contra um padrão ouro | Zero ML necessário; funciona para educação e QA | Não escala para necessidades de tradução contínua |

### É apenas JSON

O harness recebe JSON como entrada e produz JSON como saída. O [formato de dataset](/docs/leaderboard/datasets) é simples:

```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

Você pode construir isso manualmente. Você pode exportá-lo de uma planilha. Você pode gerá-lo a partir de um corpus. Um professor de língua poderia usá-lo para pontuar traduções de alunos. Uma agência de tradução poderia usá-lo para avaliar freelancers. Um laboratório de pesquisa poderia usá-lo para comparar arquiteturas de modelo. O harness não se importa de onde o JSON veio — ele apenas o pontua.

E porque o framework de implantação em produção usa a mesma interface de plugin, um método que pontua bem no harness é implantado em seu website com uma mudança de config. **Prove-o e use-o.**

As possibilidades são genuinamente infinitas. **Se você tem uma ideia, construa-a, execute o harness e envie seus scores.**

---

## Como champollion Se Encaixa

champollion fornece a camada de infraestrutura — você traz o método.

### O sistema de coaching

O método `llm-coached` do champollion permite que você injete conhecimento linguístico diretamente no prompt do LLM:

```json title=".champollion/coaching/crk.json"
{
  "grammar_rules": [
    "Plains Cree is polysynthetic — a single word can express what English needs a full sentence for",
    "Animate/inanimate noun distinction affects verb conjugation, demonstratives, and pluralization",
    "Use SRO (Standard Roman Orthography) as the working script — syllabic conversion is handled by the deterministic converter",
    "Obviation: when two third-person referents appear, the less salient one takes obviative marking (-a suffix on nouns, -iyiwa on verbs)"
  ],
  "dictionary": {
    "home": "kīwēwin",
    "settings": "isi-nākatohkēwin",
    "search": "nānātawāpahtam",
    "welcome": "tānisi",
    "dashboard": "kīskinwahamākēwin-māsinahikan"
  },
  "style_notes": "Use formal register appropriate for educational and community contexts. Preserve English technical terms in parentheses when no Cree equivalent exists or is widely accepted."
}
```

Os dados de coaching são injetados em cada prompt do LLM para o par `en:crk`, dando ao modelo contexto linguístico estruturado que ele não teria de outra forma. Veja [Coaching Data](https://champollion.dev/docs/concepts/coaching-data) para a especificação completa.

### Registers

O register é parte do system prompt que orienta tom, formalidade e convenções ortográficas. champollion vem com um register Plains Cree:

```
nêhiyawêwin (Plains Cree). Use SRO (Standard Roman Orthography) as the working
script. Output will be converted to Syllabics via deterministic converter.
Professional register appropriate for educational and community contexts.
```

Você pode sobrescrever isso em sua config para experimentar diferentes estratégias de prompting:

```json title="champollion.config.json"
{
  "languages": {
    "crk": {
      "register": "Casual Plains Cree (Y-dialect). Use SRO. Prefer everyday vocabulary over formal or archaic terms. Address the reader directly."
    }
  }
}
```

Diferentes registers produzem diferentes estilos de tradução — e diferentes scores no leaderboard. Cada submissão registra o register exato e o system prompt usado (como um hash SHA-256 no [run card](/docs/specifications/run-card)), então os experimentos são reproduzíveis.

### Conversão de script

Plains Cree é escrito em dois scripts: **Standard Roman Orthography (SRO)** e **Canadian Aboriginal Syllabics**. O pipeline do champollion:

1. LLM traduz para SRO (baseado em latim, que LLMs lidam melhor)
2. Quality gate valida a saída SRO
3. Conversor determinístico transforma SRO → Syllabics
4. Texto convertido é escrito em disco

O conversor lida com todos os diacríticos SRO (ê, î, ô, â para vogais longas) e os mapeia para os caracteres silábicos corretos. Veja [Script Converters](https://champollion.dev/docs/concepts/script-converters) para detalhes técnicos.

### O loop de avaliação

O [eval harness](/docs/specifications/harness) executa seu método contra o dataset de avaliação e produz um [run card](/docs/specifications/run-card) pontuado:

```bash
# Clone the harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install -e .

# Run a baseline experiment
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v7

# Run with FST validation (if you have an FST binary)
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --fst-analyzer ./bin/crk-analyzer \
  --condition fst-gated-v1
```

A flag `--condition` é um rótulo que você escolhe. Ela aparece no leaderboard para que as pessoas possam ver qual estratégia de prompt você usou. O harness registra o system prompt completo no run card, então sua abordagem exata é reproduzível.

:::tip Experimente livremente, envie o seu melhor
O harness é projetado para iteração rápida. Execute dezenas de experimentos com diferentes modelos, dados de coaching, registers e condições. Apenas envie para o leaderboard quando você tiver algo do qual se orgulhe.
:::

---

## Princípios OCAP

champollion é projetado para apoiar a soberania de dados indígena. Os [princípios OCAP](https://fnigc.ca/ocap-training/) (Ownership, Control, Access, Possession) guiam como abordamos tecnologia de língua para comunidades indígenas:

| Princípio | Como champollion o suporta |
|-----------|---------------------------|
| **Ownership** | Comunidades de língua possuem seus dados linguísticos. champollion nunca faz chamadas para casa ou transmite dados para nossos servidores |
| **Control** | O [método API](https://champollion.dev/docs/guides/serving-a-method) permite que comunidades hospedem seu próprio pipeline de tradução — fornecemos a interface, eles controlam a implementação |
| **Access** | Comunidades decidem quem pode usar seu método. A API pode ser protegida por autenticação |
| **Possession** | Todos os dados de tradução permanecem no sistema de arquivos do seu projeto. O [sistema de provenance](https://champollion.dev/docs/concepts/security) rastreia de onde cada tradução veio |

A arquitetura de plugin significa que uma comunidade pode construir um método que incorpora conhecimento sagrado ou restrito internamente, expor apenas a API de tradução e manter controle total sobre seus recursos linguísticos.

---

## A Visão: O Que Vem a Seguir

Plains Cree é o primeiro alvo. Uma vez que o pipeline seja validado e a comunidade esteja satisfeita com a qualidade, a mesma arquitetura se estende para outras línguas polissintéticas com infraestrutura FST:

- **Outras línguas Algonquianas**: Woods Cree, Swampy Cree, Ojibwe, Blackfoot
- **Línguas Inuit**: Inuktitut, Inuinnaqtun (que também usam scripts silábicos)
- **Outras famílias de línguas**: qualquer língua com um analisador FST pode usar o pipeline FST-gated

O leaderboard é escopo de par de línguas. Conforme novos datasets de avaliação são contribuídos por comunidades de língua, novas faixas de leaderboard abrem automaticamente.

**Este é um convite aberto.** Se você trabalha com uma língua de baixo recurso — como pesquisador, membro da comunidade, estudante ou apenas alguém que se importa — champollion oferece as ferramentas para construir algo real, medi-lo honestamente e compartilhá-lo com o mundo. O [Method Leaderboard](https://champollion.dev/leaderboard) está esperando sua submissão.

---

## Veja Também

- **[Method Leaderboard](https://champollion.dev/leaderboard)** — envie seus scores e veja como os métodos se comparam
- **[MT Evaluation](/docs/leaderboard/rules)** — o que faz um bom método, o que é desqualificado
- **[Eval Harness](/docs/specifications/harness)** — como executar experimentos
- **[Evaluation Datasets](/docs/leaderboard/datasets)** — EDTeKLA Dev v1 e FLORES+
- **[Coaching Data](https://champollion.dev/docs/concepts/coaching-data)** — como estruturar conhecimento linguístico para o LLM
- **[Script Converters](https://champollion.dev/docs/concepts/script-converters)** — o pipeline SRO→Syllabics
- **[Serving a Method via API](https://champollion.dev/docs/guides/serving-a-method)** — hospedagem de tradução controlada pela comunidade
- **[ALTLab](https://altlab.artsrn.ualberta.ca/)** — o Alberta Language Technology Lab
- **[EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/)** — o grupo de pesquisa Educational Technology, Knowledge & Language
- **[itwêwina dictionary](https://itwewina.altlab.app/)** — dicionário Plains Cree–inglês alimentado por FST