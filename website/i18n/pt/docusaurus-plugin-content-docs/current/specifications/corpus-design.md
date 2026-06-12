---
sidebar_position: 7
title: "Framework de Design de Corpus"
---
# Framework de Design de Corpus de Avaliação

> **Versão:** 1.0  
> **Status:** Rascunho  
> **Propósito:** Uma metodologia sistemática para construir corpora de avaliação que produzam avaliações de qualidade de tradução válidas, confiáveis e linguisticamente significativas. Este é o documento de referência para como os datasets de avaliação do Champollion são projetados, construídos e mantidos.

---

## 1. Princípios de Design

### 1.1 — Por que não usar Benchmarks Públicos?

Corpora paralelos públicos (FLORES+, Tatoeba, conjuntos de teste WMT, OPUS) estão disponíveis para desenvolvimento e depuração, mas são **excluídos da avaliação oficial do leaderboard**. A razão é direta:

**Contaminação.** LLMs de ponta são treinados em enormes raspagens da web. Qualquer texto paralelo que tenha existido publicamente — especialmente em datasets de benchmark curados e amplamente citados — provavelmente está em seus dados de treinamento. Quando você avalia GPT-4o em FLORES+ e ele marca 85 chrF++, você não consegue distinguir "o modelo é bom em traduzir" de "o modelo memorizou esses pares de sentenças específicos." Isso não é uma preocupação teórica — [pesquisas demonstraram](https://arxiv.org/abs/2311.04850) efeitos mensuráveis de contaminação em benchmarks de MT.

Para o Champollion, isso importa acutamente porque:
- Nosso leaderboard compara principalmente métodos baseados em LLM
- Nossa proposta de valor é *avaliação honesta e rigorosa*
- Nossos usuários-alvo (comunidades linguísticas) tomam decisões de implantação com base nessas pontuações

### 1.2 — Requisitos Centrais

Todo corpus de avaliação do Champollion deve satisfazer:

| Requisito | Justificativa |
|-----------|---------------|
| **Autoria humana** | Sem dados sintéticos. Todo texto-fonte e todas as traduções de referência devem ser escritos por humanos. LLMs podem auxiliar com alinhamento e formatação, mas nunca gerar conteúdo. |
| **Não disponível publicamente em forma paralela** | O texto-fonte pode ser público; as traduções de referência podem ser públicas; mas o *emparelhamento* específico não deve existir como um corpus paralelo para download. |
| **Proveniência rastreada** | Cada entrada deve ter origem documentada: documento-fonte, tradutor, licença, data. |
| **Informada linguisticamente** | A cobertura deve ser guiada por características tipológicas, não amostragem aleatória. |
| **Estratificada por domínio** | As entradas devem abranger domínios definidos com representação controlada. |
| **Escalonada por dificuldade** | As entradas devem ser atribuídas a níveis de dificuldade (1–5) com base na complexidade estrutural. |
| **Versionada** | As versões do corpus são com hash de conteúdo. As pontuações são comparáveis apenas dentro da mesma versão. |
| **Revisável pela comunidade** | As traduções de referência devem ser revisáveis por membros da comunidade linguística. |

---

## 2. Seleção de Texto-Fonte

### 2.1 — Taxonomia de Domínios

O Champollion avalia tradução para **contextos de implantação prática**, não exercícios acadêmicos. A taxonomia de domínios reflete tipos de texto do mundo real que os usuários de tradução encontram:

| Domínio | Código | Descrição | Fontes de Exemplo |
|---------|--------|-----------|-------------------|
| **Interface de Software** | `ui` | Rótulos de botões, itens de menu, mensagens de erro, dicas, fluxos de integração | Strings de aplicativos de código aberto, portais de documentação |
| **Oficial/Administrativo** | `admin` | Documentos governamentais, avisos legais, formulários, declarações de política | Publicações governamentais públicas, documentos municipais |
| **Educacional** | `edu` | Conteúdo de livros didáticos, materiais de aula, texto instrucional | Materiais educacionais publicados, guias de ensino |
| **Narrativo/Literário** | `lit` | Histórias, textos culturais, transcrições de história oral | Livros publicados, arquivos culturais (com permissão) |
| **Conversacional** | `conv` | Diálogo, trocas semelhantes a chat, comunicação escrita informal | Corpora de diálogo publicados, roteiros, transcrições de entrevistas |
| **Técnico** | `tech` | Documentação de API, arquivos README, especificações técnicas | Documentação de projetos de código aberto |
| **Saúde/Médico** | `health` | Informações médicas voltadas para pacientes, mensagens de saúde pública | Publicações de saúde governamentais |
| **Notícias/Jornalístico** | `news` | Artigos de notícias, comunicados à imprensa, assuntos atuais | Jornais comunitários, meios de comunicação indígenas |

### 2.2 — Distribuição de Domínios

Um corpus de avaliação padrão deve visar a seguinte distribuição. Os percentuais exatos podem variar por par de idiomas com base em quais tipos de texto são mais relevantes para a comunidade-alvo:

| Domínio | % Alvo | Justificativa |
|---------|--------|---------------|
| Interface de Software | 25% | Contexto de implantação primária para usuários da CLI do champollion |
| Oficial/Administrativo | 15% | Tradução de alto risco com implicações legais |
| Educacional | 15% | Caso de uso central para revitalização linguística |
| Narrativo/Literário | 10% | Testa nuance cultural e registro literário |
| Conversacional | 10% | Testa registro informal e padrões de fala natural |
| Técnico | 10% | Testa precisão e consistência de terminologia |
| Saúde/Médico | 10% | Alto risco, testa vocabulário específico do domínio |
| Notícias/Jornalístico | 5% | Testa vocabulário contemporâneo e registro neutro |

### 2.3 — Critérios de Seleção de Fonte

Ao selecionar textos-fonte para um novo corpus:

1. **Compatibilidade de licença.** O texto-fonte deve estar sob uma licença que permita o uso em um corpus de avaliação. Prefira CC BY, CC BY-SA ou domínio público. Documente a licença.

2. **Recência.** Prefira textos publicados nos últimos 10 anos. A linguagem evolui — especialmente vocabulário em torno de tecnologia, governança e medicina.

3. **Diversidade de registro.** Dentro de cada domínio, busque textos em diferentes níveis de formalidade. Um comunicado à imprensa governamental (formal) e uma postagem em mídia social governamental (informal) são ambos domínio `admin` mas registros diferentes.

4. **Relevância cultural.** Para idiomas indígenas e minoritários, priorize textos que importam para a comunidade — documentos de gestão de terras, materiais educacionais no idioma, textos de preservação cultural — em vez de textos que acontecem existir em forma paralela.

5. **Sem fontes traduzidas por máquina.** Se um documento "paralelo" foi criado executando o original através do Google Translate e depois editando, NÃO é aceitável como tradução de referência. A referência deve ser uma tradução humana independente.

---

## 3. Sistema de Níveis de Dificuldade

### 3.1 — Definições de Níveis

Cada entrada é atribuída a um nível de dificuldade (1–5) com base na complexidade estrutural do *texto-fonte*, não na dificuldade de tradução (que varia por método).

| Nível | Rótulo | Características Estruturais |
|-------|--------|---------------------------|
| 1 | **Elementar** | Sentenças simples. Cláusula única. Tempo presente. Vocabulário comum. Sem idiomas. Sem estruturas incorporadas. |
| 2 | **Intermediário** | Sentenças compostas. Duas cláusulas unidas por conjunção. Tempo passado/futuro. Algum vocabulário de domínio. |
| 3 | **Avançado** | Sentenças complexas. Cláusulas subordinadas, cláusulas relativas. Tempos mistos. Terminologia específica do domínio. Voz passiva. |
| 4 | **Especialista** | Múltiplas cláusulas incorporadas. Registro legal/técnico. Estruturas condicionais. Conceitos abstratos. Referências culturais. |
| 5 | **Extremo** | Prosa densa com múltiplos desafios simultâneos: subordinação aninhada, referência de pronome ambígua, idiomas culturais, registro misto, vocabulário raro. |

### 3.2 — Fatores de Dificuldade Linguisticamente Informados

Além da complexidade estrutural, a dificuldade é modulada pela **distância tipológica** entre o idioma-fonte e o idioma-alvo. Esses fatores são extraídos de características tipológicas WALS e dados de classificação do cartão de idioma:

| Fator | Baixa Dificuldade | Alta Dificuldade |
|-------|------------------|-----------------|
| **Ordem de palavras** | Mesma ordem básica (ex: SVO→SVO) | Ordem básica diferente (ex: SVO→SOV) |
| **Tipo morfológico** | Tipo similar (ex: analítico→analítico) | Tipo diferente (ex: analítico→polissintético) |
| **Gênero gramatical** | Mesmo sistema ou sem gênero | Fonte sem gênero, alvo com gênero complexo |
| **Honorífico/registro** | Sem marcação de registro | Alvo com sistema de registro complexo (ex: japonês, coreano) |
| **Script** | Mesmo script | Script diferente (transliteração necessária) |
| **Animacidade** | Sem distinção de animacidade | Alvo com concordância baseada em animacidade (ex: Cree) |
| **Evidencialidade** | Sem evidencialidade | Alvo marca fonte de informação gramaticalmente |

### 3.3 — Distribuição de Níveis

Um corpus padrão deve ter aproximadamente:

| Nível | % Alvo | Justificativa |
|-------|--------|---------------|
| 1 | 15% | Estabelece linha de base — até métodos ruins devem lidar com estes |
| 2 | 25% | Tradução prática do dia a dia |
| 3 | 30% | Onde as diferenças de qualidade do método se tornam visíveis |
| 4 | 20% | Separa métodos bons de ótimos |
| 5 | 10% | Teste de teto — muito poucos métodos lidarão bem com estes |

---

## 4. Qualidade da Tradução de Referência

### 4.1 — Requisitos do Tradutor

As traduções de referência devem ser produzidas por humanos que sejam:

1. **Falantes fluentes** do idioma-alvo (L1 ou equivalente)
2. **Alfabetizados** em idioma-fonte e idioma-alvo
3. **Conscientes do domínio** para o domínio do texto (um tradutor médico para textos de saúde, etc.)
4. **Independentes** — o tradutor não deve ter acesso a nenhuma saída de MT para o mesmo texto durante a tradução

### 4.2 — Briefing de Tradução

Todo tradutor recebe um briefing que inclui:

- O **registro** a usar (formal, conversacional, etc.)
- O **público-alvo** (público geral, especialistas, crianças, etc.)
- Quaisquer **convenções de terminologia** específicas da comunidade linguística
- Instrução explícita: "Traduza o significado, não as palavras. Uma tradução que soe natural é mais valiosa que uma literal."

### 4.3 — Garantia de Qualidade

1. **Tradução dupla.** Idealmente, cada entrada tem duas traduções de referência independentes de tradutores diferentes. Quando isso não é viável, priorize tradução dupla para Níveis 4–5.

2. **Revisão comunitária.** As traduções de referência devem ser revisadas por pelo menos um falante adicional que não produziu a tradução.

3. **Variantes aceitáveis.** Para cada referência, documente variantes aceitáveis conhecidas (ordem de palavras, convenções ortográficas, formas dialetais). Estas alimentam a métrica `equivalent_match_rate`.

### 4.4 — O que Torna uma Referência Ruim

| Problema | Por que Invalida Avaliação |
|---------|---------------------------|
| Traduzida por máquina e depois editada | A edição preserva estrutura de MT; penaliza métodos que produzem traduções mais naturais |
| Traduzida por um aprendiz, não um falante fluente | A referência pode conter erros que penalizam saída de MT correta |
| Excessivamente literal | Traduções naturais pontuam mal contra referências literais |
| Interpretação única válida para fonte ambígua | Penaliza interpretações alternativas válidas |

---

## 5. Prevenção de Contaminação

### 5.1 — Modelo de Ameaça de Contaminação

| Ameaça | Descrição | Mitigação |
|--------|-----------|-----------|
| **Sobreposição de dados de treinamento** | LLMs treinados no corpus paralelo | Não publique o corpus paralelo publicamente |
| **Vazamento de poucos exemplos** | Autor do método usa entradas de avaliação como exemplos de poucos exemplos | Verificação de impressão digital: entradas no prompt são detectadas e sinalizadas |
| **Contaminação indireta** | Texto-fonte existe em dados de treinamento de LLM (monolíngue) | Aceitável — texto-fonte monolíngue é esperado. O *emparelhamento* deve ser novo. |
| **Contaminação de multidão** | Revisores comunitários compartilham entradas publicamente | Termos de licença proíbem redistribuição do corpus paralelo |

### 5.2 — Níveis de Sigilo do Corpus

| Nível | Visibilidade | Uso |
|-------|-------------|-----|
| **Conjunto de desenvolvimento público** | Totalmente público | Desenvolvimento de método, depuração, testes de regressão. Pontuações NÃO publicadas no leaderboard. |
| **Conjunto de avaliação retido** | Texto-fonte visível, referências secretas | Avaliação oficial do leaderboard. Métodos recebem texto-fonte e retornam traduções; a pontuação acontece no servidor. Referências nunca são expostas ao método. |
| **Conjunto padrão-ouro** | Totalmente secreto, controlado pela comunidade | Avaliação validada pela comunidade. Gerenciado pela organização de governança. Usado para verificação de nível "Validado pela Comunidade". |

### 5.3 — Política de Rotação

Os corpora de avaliação devem ser **rotacionados** periodicamente:

1. Após um corpus estar em uso por 12 meses, comece a construir um substituto
2. Retire o corpus antigo para status de "conjunto de desenvolvimento" (público)
3. Promova o novo corpus para status de "conjunto de avaliação retido"
4. Isso previne contaminação gradual através de otimização iterativa contra um alvo fixo

---

## 6. Fluxo de Trabalho de Construção de Corpus

### 6.1 — Processo Passo a Passo

```
Step 1: Language Pair Selection
    └─ Identify target language, read language card
    └─ Review typological features (WALS), contact influences, scripts
    └─ Identify which difficulty factors apply

Step 2: Source Text Curation
    └─ Identify candidate source documents per domain
    └─ Verify licenses
    └─ Extract candidate sentences/segments
    └─ Classify by domain and preliminary difficulty tier

Step 3: Segment Selection
    └─ Sample segments to match domain distribution (§2.2)
    └─ Sample segments to match difficulty distribution (§3.3)
    └─ Ensure linguistic phenomenon coverage (§6.2)
    └─ Target minimum corpus size (§6.3)

Step 4: Reference Translation
    └─ Assign segments to qualified translators
    └─ Provide translation brief
    └─ Collect translations
    └─ Dual-translate Tier 4–5 entries

Step 5: Quality Assurance
    └─ Community review of references
    └─ Document acceptable variants
    └─ Flag and resolve disagreements

Step 6: Metadata & Packaging
    └─ Assign final difficulty tiers
    └─ Add provenance metadata per entry
    └─ Content-hash the corpus for versioning
    └─ Package as corpus JSON per harness spec

Step 7: Registration
    └─ Register in Supabase datasets table
    └─ Add to ATTRIBUTION.md if new sources used
    └─ Document in arena website
```

### 6.2 — Cobertura de Fenômeno Linguístico

Todo corpus deve incluir entradas que testem fenômenos linguísticos específicos relevantes para o par de idiomas. Estes são extraídos dos campos `linguisticChallenges` e `contactInfluences` do cartão de idioma:

**Fenômenos universais (todos os pares de idiomas):**
- Resolução de pronome (antecedentes ambíguos)
- Negação (simples, dupla, escopo)
- Quantificadores (todos, alguns, nenhum, maioria)
- Expressões temporais (datas relativas, durações)
- Entidades nomeadas (pessoas, lugares, organizações)
- Números e medidas
- Listas e enumeração

**Fenômenos específicos do par (do cartão de idioma):**
- Para alvos polissintéticos: morfologia verbal complexa, incorporação
- Para alvos com gênero: concordância de gênero, referência neutra/inclusiva
- Para alvos SOV: verbos finais de cláusula, posposições
- Para idiomas tonais: distinções de significado dependentes de tom
- Para idiomas honoríficos: marcadores de registro, contexto social
- Para idiomas de contato: limites de alternância de código, integração de empréstimo

### 6.3 — Tamanho Mínimo de Corpus

A confiabilidade estatística requer contagens mínimas de entradas. Estas são baseadas em requisitos de intervalo de confiança bootstrap pareado (de `significance.py`):

| Propósito | Entradas Mínimas | Recomendado |
|-----------|-----------------|------------|
| Conjunto de desenvolvimento | 50 | 100–200 |
| Conjunto de avaliação retido | 100 | 200–500 |
| Conjunto padrão-ouro | 200 | 500+ |
| Mínimo por domínio | 10 | 25+ |
| Mínimo por nível | 10 | 20+ |

**Por que 100 mínimo para avaliação?** Com menos de ~100 entradas, testes de significância bootstrap pareado (1.000 reamostragens) não conseguem detectar confiávelmente diferenças menores que ~5 pontos chrF++. Com 200+ entradas, podemos detectar diferenças de ~2 pontos em p<0,05.

---

## 7. Formato JSON do Corpus

Cada entrada do corpus segue a especificação do harness:

```json
{
  "id": "edtekla-dev-v1-042",
  "source": "The school board will meet on Tuesday to discuss the new curriculum.",
  "reference": "ᑭᓯᑭᓄᐦᐊᒫᑐᐏᓐ ᑲ ᐃᔑ ᐱᒥᐸᔨᐦᑕᐦᒃ ᑭᔅᑭᓄᐦᐊᒫᑐᐏᓇ ᐁ ᐃᔑ ᒫᒥᑐᓀᔨᐦᑕᐦᒃ ᐅᔥᑭ ᑭᔅᑭᓄᐦᐊᒫᑫᐏᓂᔭ ᓂᔓ ᑭᔑᑲᐤ",
  "acceptable_variants": [
    "ᑭᔅᑭᓄᐦᐊᒫᑐᐏᓐ ᓂᔓ ᑭᔑᑲᐤ ᑲ ᐃᔑ ᒫᒥᑐᓀᔨᐦᑕᐦᒃ ᐅᔥᑭ ᑭᔅᑭᓄᐦᐊᒫᑫᐏᓂᔭ"
  ],
  "domain": "edu",
  "difficulty": 3,
  "phenomena": ["temporal_expression", "named_entity", "future_tense"],
  "provenance": {
    "source_doc": "EdTeKLA Module 4, Unit 7",
    "source_license": "CC BY-NC-SA 4.0",
    "translator": "anonymous-speaker-001",
    "translator_qualification": "L1 Plains Cree, certified translator",
    "translation_date": "2025-11-15",
    "reviewer": "anonymous-speaker-002",
    "review_date": "2025-12-01"
  }
}
```

---

## 8. Medidas Anti-Gaming

### 8.1 — Integridade do Corpus

| Medida | Implementação |
|--------|---------------|
| **Hash de conteúdo** | Versão do corpus = SHA-256 de IDs de entrada ordenados + referências. Qualquer modificação produz uma nova versão. |
| **Impressão digital de entrada** | Cada entrada tem um ID derivado de conteúdo. Se alguém enviar resultados contra um corpus modificado, a impressão digital não corresponderá. |
| **Aplicação retida** | Para avaliação oficial, métodos recebem APENAS texto-fonte. Referências nunca são expostas. A pontuação acontece no servidor. |
| **Cronograma de rotação** | Corpora rodam anualmente para prevenir otimização de longo prazo contra um alvo fixo. |

### 8.2 — Integridade de Envio

| Medida | Implementação |
|--------|---------------|
| **Impressão digital determinística** | Configuração de execução (modelo, temperatura, prompt, versão do corpus) é feita hash. Configurações idênticas produzem impressões digitais idênticas. |
| **Detecção de cherry-pick** | Submissores devem divulgar todas as execuções, não apenas a melhor. Múltiplos envios com a mesma impressão digital são sinalizados. |
| **Verificação de contaminação** | Se entradas de avaliação aparecem verbatim no prompt ou dados de coaching do método, o envio é desqualificado. |

---

## 9. Corpora Existentes

### 9.1 — Conjunto de Desenvolvimento EDTeKLA v1

| Propriedade | Valor |
|-------------|-------|
| **ID** | `edtekla-dev-v1` |
| **Par** | EN → CRK (Cree das Planícies, SRO) |
| **Entradas** | 404 (`master_corpus.json`: 62 ouro + 342 livro didático); 548 total disponível |
| **Domínios** | Educacional (100%) |
| **Níveis** | 1–5 (distribuição TBD por auditoria de entrada) |
| **Licença** | CC BY-NC-SA 4.0 |
| **Status** | Conjunto de desenvolvimento (público) |

**Limitações:** Domínio único (apenas educacional). Sem estratificação de domínio. Atribuições de nível podem precisar auditoria. Tamanho pequeno de corpus limita poder estatístico para testes de significância.

### 9.2 — Corpora Planejados

| Corpus | Par | Status | Proprietário |
|--------|-----|--------|--------------|
| Corpus customizado EN → TL (Filipino) | EN → TL | Planejado | Proprietário do projeto |
| Conjunto retido EN → CRK | EN → CRK | Futuro (precisa de parceiro comunitário) | Organização de governança comunitária |

---

## 10. Integração do Cartão de Idioma

O framework de corpus se integra com o sistema de cartão de idioma:

1. **Seleção de domínio** é informada pelo `linguisticChallenges` do cartão — se um idioma tem desafios únicos (polissíntese, tom, animacidade), o corpus deve incluir entradas que os testem.

2. **Calibração de dificuldade** usa o `classification` do cartão — a distância tipológica entre famílias de fonte e alvo afeta o que constitui "difícil".

3. **Cobertura de registro** usa o `registers` do cartão — se um idioma tem registros definidos (filipiniano-formal, taglish-profissional, taglish-casual), o corpus deve incluir entradas em cada nível de registro.

4. **Teste de influência de contato** usa o `contactInfluences` do cartão — para idiomas com camadas de empréstimo pesadas (Filipino: espanhol + inglês + árabe), inclua entradas que testem se métodos lidam corretamente com empréstimos vs. sobre-traduzindo-os.

5. **Manipulação de script** usa o `scripts[]` do cartão — para idiomas multi-script (sérvio: cirílico + latino), inclua entradas que testem seleção correta de script.

---

## Referências

- **Especificação de Pontuação do Champollion** — define todas as métricas, pesos compostos, níveis de qualidade
- **Especificação de Benchmark do Champollion** — protocolo de avaliação, formato de corpus, soberania de dados
- **WALS** (World Atlas of Language Structures) — banco de dados de características tipológicas
- **Glottolog** — fonte de verdade de classificação de idioma
- **ISO 639-3** — padrão de identificação de idioma
- **EdTeKLA** — fonte do primeiro corpus de avaliação

---

*Este documento é uma especificação viva. Atualize-o conforme novos corpora são construídos e lições são aprendidas.*