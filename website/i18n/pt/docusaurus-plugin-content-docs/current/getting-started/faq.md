---
sidebar_position: 2
title: "Perguntas Frequentes"
related:
  - label: "How It Works"
    to: /docs/how-it-works
    kind: doc
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Glossary"
    to: https://champollion.dev/glossary
    kind: glossary
    note: "Plain-language definitions for every technical term"
---
# Perguntas Frequentes

> **Resumo Executivo.** Respostas para perguntas comuns sobre o MT Eval Arena — como funciona a pontuação, o que resulta em desqualificação, como lidar com idiomas sem FSTs, recomendações de modelos e parâmetros, e o processo de submissão.

---

## Pontuação & Métricas

### Quais métricas o harness calcula?

O harness calcula cinco métricas para Plains Cree (o idioma de benchmark atual). Três são agnósticas de idioma e funcionam para qualquer idioma; duas atualmente dependem de plugins específicos do CRK e serão generalizadas conforme expandimos para mais idiomas.

| Métrica | Escala | O Que Mede | Status |
|---------|--------|-----------|--------|
| **chrF++** | 0–100 | Sobreposição de n-gramas de caracteres entre traduções preditas e de referência. Melhor métrica de superfície para idiomas morfologicamente ricos. Usa pontuação nativa do sacrebleu. | ✅ Todos os idiomas |
| **Exact match** | 0.0–1.0 | Proporção de entradas onde a predição corresponde exatamente à referência após normalização. | ✅ Todos os idiomas |
| **FST acceptance** | 0.0–1.0 | Proporção de palavras de saída aceitas por um transdutor de estados finitos (analisador morfológico). Calculado apenas quando um binário FST é fornecido. | ✅ Todos os idiomas com FST |
| **Equivalent match** | 0.0–1.0 | Fração de entradas correspondentes à referência ou a uma variante aceitável — levando em conta ordem de palavras, convenção ortográfica e diferenças dialetais. | ⚡ CRK (generalizando) |
| **Semantic score** | 0.0–1.0 | Pontuação de preservação de significado — quão bem a tradução captura o significado pretendido independentemente da forma de superfície? | ⚡ CRK (generalizando) |

Métricas adicionais estão planejadas: **morphological accuracy**, **code-switching detection**, **terminology adherence** e **hallucination detection**. Veja [Scoring Specification §2](/docs/specifications/scoring#2-metric-inventory) para o inventário completo de 19 métricas.

### Como é calculada a pontuação composta?

A composta é uma média ponderada das métricas disponíveis, normalizada para uma escala 0.0–1.0. Os pesos são definidos em dois perfis:

- **Profile A** (idiomas com FST): 9 métricas, métricas estruturais (FST + morphological accuracy) carregam 40% do peso composto
- **Profile B** (idiomas sem FST): 8 métricas, semântica e chrF++ carregam peso de topo igual

Quando uma métrica não está disponível, seu peso é redistribuído proporcionalmente entre as métricas restantes. Isso significa que benchmarks em estágio inicial (com apenas chrF++ e exact match disponíveis) ainda produzem compostas válidas — os pesos efetivos apenas refletem o que está disponível.

**As tabelas de peso completas, regras de normalização e justificativa de exclusão estão em [Scoring Specification §4](/docs/specifications/scoring#4-composite-score).** O código do harness espelha essas tabelas em `mt_eval_harness/scoring.py`. chrF++ é normalizado dividindo por 100 antes da ponderação; taxas de code-switching e hallucination são invertidas (menor = melhor).

### O que são níveis de qualidade?

Níveis de qualidade são rótulos heurísticos mapeados para intervalos de pontuação composta. Eles ajudam a comunicar o que uma pontuação *significa* na prática:

| Nível | Intervalo Composto | Interpretação |
|-------|-------------------|----------------|
| **Baseline** | 0.00 – 0.30 | Abaixo de qualidade útil. Método precisa de melhoria significativa. |
| **Emerging** | 0.30 – 0.50 | Mostra promessa. Algumas traduções estão corretas mas inconsistentes. |
| **Functional** | 0.50 – 0.70 | Utilizável como referência com revisão humana. Não adequado para implantação sem revisão. |
| **Deployable** | 0.70 – 0.85 | Pronto para uso em produção com revisão periódica. Dispara elegibilidade de transferência de propriedade. |
| **Fluent** | 0.85 – 1.00 | Qualidade quase nativa. Adequado para implantação sem supervisão. |

### Qual é a diferença entre níveis de qualidade e níveis de verificação?

**Níveis de qualidade** descrevem *o que a pontuação automatizada significa* (Baseline → Fluent). **Níveis de verificação** descrevem *quem validou o resultado*:

| Nível de Verificação | O Que Significa |
|----------------------|-----------------|
| **Self-benchmarked** | O submissor executou o harness por conta própria. Pontuações são plausíveis mas não verificadas. |
| **GDS Verified** | Um mantenedor reproduziu o resultado usando a configuração de método submetida. |
| **Community Validated** | Falantes bilíngues revisaram as traduções e confirmaram a qualidade. |

Um método pode ser "Deployable" em qualidade mas apenas "Self-benchmarked" em verificação — significando que a pontuação parece ótima mas ninguém confirmou independentemente.

---

## Submissão & Desqualificação

### O que resulta em desqualificação da minha submissão?

Sua submissão será rejeitada ou sinalizada se:

1. **Seu método foi exposto aos dados de avaliação.** Se você treinou, ajustou, fez few-shot-prompt ou de outra forma usou qualquer entrada do conjunto de dados de avaliação, suas pontuações são artificialmente inflacionadas. Isso inclui usar as traduções de referência em seu prompt.
2. **Seu run card falha nas verificações de integridade.** A impressão digital deve corresponder à configuração. Run cards adulterados são rejeitados.
3. **Seu método não implementa o protocolo TranslationMethod.** O harness espera `translate(entries, config) → results`. Integrações personalizadas que contornam o harness não são aceitas.

### Posso submeter múltiplas vezes?

Sim. O leaderboard rastreia todas as submissões. Você pode iterar — executar dezenas de experimentos, submeter apenas o melhor. Cada submissão registra uma impressão digital única, então não há ambiguidade sobre qual execução produziu qual pontuação.

### Como faço para verificar minha pontuação?

1. **Self-benchmarked (automático):** Toda submissão começa aqui.
2. **GDS Verified:** Submeta seu método como um pacote reproduzível (código + configuração + dados de coaching). Um mantenedor o executará novamente contra o mesmo conjunto de dados e confirmará que as pontuações correspondem.
3. **Community Validated:** Para idiomas indígenas, isso requer que falantes bilíngues revisem uma amostra de traduções. Isso não pode ser automatizado — requer engajamento comunitário.

### A API de submissão está ativa?

Ainda não. O endpoint `https://mtevalarena.org/api/leaderboard/submit` é aspiracional. Submissões atuais devem ser feitas via pull request para o [repositório eval harness](https://github.com/gamedaysuits/arena) com seu JSON de run card no diretório `results/`.

---

## Modelos & Parâmetros

### Qual modelo devo usar?

Não há um único melhor modelo — depende do par de idiomas, seu orçamento e sua abordagem. Orientação geral:

| Tipo de Idioma | Ponto de Partida Recomendado | Por Quê |
|----------------|------------------------------|---------|
| **Alto recurso** (Francês, Espanhol, Japonês) | `google/gemini-2.5-flash` ou `gpt-4o-mini` | Rápido, barato, baseline forte |
| **Baixo recurso com alguma cobertura LLM** (Quéchua, Iorubá) | `google/gemini-2.5-pro` ou `anthropic/claude-sonnet-4` | Modelos maiores têm melhor conhecimento latente |
| **Polissintético / muito baixo recurso** (Plains Cree, Inuktitut) | `google/gemini-2.5-pro` com coaching | Dados de coaching importam mais que a escolha do modelo. OMT-1600 inclui alguns idiomas polissintéticos (ex., CRK em tier R1) mas com tokenização BPE padrão — faça benchmark como baseline na Arena. |

O harness de avaliação usa OpenRouter, então qualquer modelo disponível no OpenRouter pode ser avaliado. Execute `champollion models --method llm` para ver modelos disponíveis.

### Qual temperatura devo usar?

Menor é geralmente melhor para tradução:

| Temperatura | Efeito | Recomendado Para |
|-------------|--------|-----------------|
| **0.0 – 0.2** | Saída altamente determinística, consistente | Métodos de produção, benchmarks finais |
| **0.3 – 0.5** | Alguma variação, ocasionalmente mais criativo | Exploração, iteração inicial |
| **0.6+** | Alta variação, imprevisível | Não recomendado para benchmarking de MT |

Temperatura é registrada no run card, então diferentes temperaturas produzem diferentes impressões digitais — são tratadas como experimentos diferentes.

### Dados de coaching ajudam?

Sim, significativamente — para idiomas de baixo recurso. Dados de coaching (regras gramaticais, entradas de dicionário, notas de estilo) são injetados no prompt do sistema do LLM. Para Plains Cree, métodos com coaching consistentemente superam métodos LLM brutos para idiomas polissintéticos porque LLMs de propósito geral têm exposição limitada a polissintéticos e nenhuma consciência morfológica. Mesmo OMT-1600, que foi especificamente treinado para CRK, usa tokenização BPE padrão que não pode representar morfologia polissintética estruturalmente. Os dados de coaching fornecem o contexto linguístico que o modelo não possui.

Para idiomas de alto recurso (Francês, Espanhol), coaching tem menos impacto porque o modelo já tem conhecimento baseline forte.

Veja [Coaching Data](https://champollion.dev/docs/concepts/coaching-data) para a especificação completa.

---

## FST & Validação Morfológica

### E se não houver FST para meu idioma?

Muitos idiomas não têm um transdutor de estados finitos. Tudo bem — o harness funciona sem um. A pontuação composta usa pesos de Profile B (veja [Scoring Specification §4.3](/docs/specifications/scoring#43-weight-tables)) que deslocam peso para métricas semânticas e de superfície. FST acceptance é marcado como `null` no run card.

Os principais registros para FSTs existentes:

| Registro | Cobertura | URL |
|----------|-----------|-----|
| **GiellaLT** | Sámi, Cree, Inuktitut e outros idiomas do Ártico/subartico | [giellalt.uit.no](https://giellalt.uit.no/) |
| **ALTLab** | Plains Cree, Woods Cree, Ojibwe | [altlab.artsrn.ualberta.ca](https://altlab.artsrn.ualberta.ca/) |
| **Apertium** | ~60 pares de idiomas, principalmente europeus | [apertium.org](https://apertium.org/) |
| **UniMorph** | Paradigmas morfológicos para 150+ idiomas | [unimorph.github.io](https://unimorph.github.io/) |

### Posso construir um FST?

Sim, mas não é trivial. Um FST codifica as regras morfológicas de um idioma — todas as formas de palavras válidas. Construir um requer conhecimento linguístico profundo do idioma. Se você tiver acesso a uma gramática morfológica (ex., de um departamento de linguística), ela pode ser compilada em um FST usando ferramentas como [HFST](https://hfst.github.io/) ou [Foma](https://fomafst.github.io/).

### Como o gating de FST funciona na prática?

O pipeline com gating de FST funciona assim:

1. LLM gera uma tradução
2. Cada palavra na saída é verificada contra o FST
3. Palavras que o FST rejeita são sinalizadas como morfologicamente inválidas
4. O método pode tentar novamente com feedback ("a palavra X não é válida, tente novamente")
5. Após tentativas, palavras inválidas restantes são registradas

A taxa de aceitação de FST mede quantas palavras passam na validação. Veja o [FST-Gated Pipeline Tutorial](/docs/tutorials/fst-gated-pipeline) para um exemplo completo trabalhado.

---

## Dados & Conjuntos de Dados

### Posso contribuir com um conjunto de dados para um novo idioma?

Sim. Requisitos mínimos de [Benchmark Specification §11](/docs/specifications/benchmark#11-extending-to-new-languages):

- **50 entradas padrão-ouro** (fonte + tradução de referência verificada)
- **30 entradas de desenvolvimento** (podem sobrepor com padrão-ouro para corpora pequenos)
- **Consentimento comunitário** (para idiomas indígenas, autorização explícita de um órgão de governança)
- **Documentação de proveniência** (de onde os dados vieram, qual licença se aplica)

Novos conjuntos de dados abrem novas faixas de leaderboard automaticamente. Veja [For Language Communities](/docs/community/for-language-communities) para o guia do contribuidor.

### Em qual formato meu conjunto de dados deve estar?

JSON com os nomes de campo canônicos:

```json
{
  "name": "my-language-dev-v1",
  "language_pair": "en-xxx",
  "segment": "development",
  "version": "1.0",
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "[translation in target language]",
      "difficulty": 1,
      "domain": "general"
    }
  ]
}
```

Veja [Datasets](/docs/leaderboard/datasets) para o esquema completo e definições de tier de dificuldade.

---

## Soberania & Propriedade

### Quem é o proprietário de um método construído para um idioma indígena?

Para idiomas indígenas, métodos que atingem tier Deployable (composta ≥ 0.70) E passam na validação comunitária disparam o processo de [ownership transfer](/docs/sovereignty/ownership-transfer). A propriedade do código é transferida do pesquisador para a organização de governança da comunidade linguística.

O pesquisador retém:
- Direitos de publicação (artigos acadêmicos sobre o método)
- Crédito no leaderboard
- O direito de aplicar as mesmas *técnicas* a outros idiomas

A organização de governança ganha:
- Propriedade total do código do método e dados de coaching
- Controle sobre implantação (quando, onde, como)
- Receita do uso de API (90% comunidade, 10% infraestrutura)

### Posso usar champollion para idiomas não indígenas sem preocupações de soberania?

Sim. Para idiomas padrão (Francês, Japonês, Espanhol, etc.), não há considerações de soberania. Use champollion normalmente — traduza, sincronize, publique como desejar. O framework de soberania se aplica especificamente a idiomas indígenas e governados por comunidades onde princípios de governança de dados (OCAP®, CARE, Te Mana Raraunga) requerem consideração especial.

---

## Veja Também

- **[How It Works](https://champollion.dev/how-it-works)** — o explicador de solução completo
- **[Scoring Specification](/docs/specifications/scoring)** — a SSOT para toda lógica de pontuação (métricas, pesos, níveis)
- **[Benchmark Specification](/docs/specifications/benchmark)** — protocolo de avaliação, formato de corpus, soberania
- **[Submit a Method](/docs/getting-started/submit-a-method)** — quickstart passo a passo
- **[Leaderboard Rules](/docs/leaderboard/rules)** — critérios de submissão
- **[Data Sovereignty](/docs/sovereignty/data-sovereignty)** — OCAP®, CARE e obrigações éticas