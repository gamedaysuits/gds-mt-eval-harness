---
sidebar_position: 8
title: "Especificação do Prêmio"
slug: '/specifications/prizes'
related:
  - label: "How Speakers Get Paid"
    to: /docs/perspectives/how-speakers-get-paid
    kind: position
    note: "The plain-language version of these numbers"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
---
# Especificação de Prêmios

> **Propósito.** Este documento define a estrutura do fundo de prêmios, condições de limite, processo de reclamação e regras para a MT Eval Arena. Especifica exatamente o que "capaz de tradução automática" significa em termos mensuráveis e sob quais condições o dinheiro do prêmio é liberado. Este documento referencia SCORING_SPEC para definições de métricas e BENCHMARK_SPEC para protocolo de avaliação — não as duplica.
>
> **Status:** ATIVO. O Founder's Prize (§2.1) está financiado e ativo.
>
> Última atualização: 2026-06-04

---

## 1. Filosofia

### 1.1 Prêmios Recompensam Avanços, Não Participação

O dinheiro do prêmio é liberado apenas quando um método demonstra alcançar um limite de capacidade definido. Não há prêmios de participação, prêmios para segundo lugar ou pagamentos de consolação. Se ninguém ultrapassar a barra, ninguém recebe pagamento. Isso é intencional — significa que os patrocinadores pagam apenas por resultados que realmente funcionam.

### 1.2 Validação Comunitária É Inegociável

Métricas automatizadas são proxies (SCORING_SPEC §1.1). Um método pode ter bom desempenho em chrF++ e aceitação FST enquanto produz saída que nenhum falante aceitaria. **Toda reclamação de prêmio requer validação comunitária** — falantes bilíngues devem confirmar que a saída é utilizável. Este é o portão de validação humana (BENCHMARK_SPEC §7).

### 1.3 Transferência de Propriedade Faz Parte do Acordo

Métodos que reclamam um prêmio estão sujeitos à cláusula de transferência de propriedade (BENCHMARK_SPEC §8.3). O desenvolvedor mantém direitos de atribuição e publicação. A organização de governança ganha o direito de usar, modificar, distribuir e monetizar o método para seu idioma. Isso não é uma penalidade — é o ponto. O dinheiro do prêmio financia a criação de tecnologia que pertence à comunidade linguística.

### 1.4 Anti-Gaming

Os limites de prêmio são definidos contra **avaliação de padrão ouro** (conjunto de testes secreto, executado pela organização de governança em sandbox). Desenvolvedores nunca veem os dados de teste. Isso é aplicado arquitetonicamente — não é uma política que depende de honra. Veja BENCHMARK_SPEC §8.2.

### 1.5 Licenciamento de Corpus: Corpus Não-Comerciais Ficam Fora da Pista de Prêmios

Alguns corpus usados durante o desenvolvimento do método carregam licenças não-comerciais — por exemplo, o corpus EdTeKLA Cree Language Textbook é **CC BY-NC-SA 4.0**. Esses corpus são **apenas para pista de pesquisa/desenvolvimento**:

1. **Os corpus de padrão ouro de prêmios não devem incorporar conteúdo de corpus com licença NC.** Segmentos de teste de padrão ouro são originais encomendados pela comunidade (veja Corpus Partnership Strategy) — criados por humanos para o prêmio, com direitos esclarecidos para avaliação e implantação comercial desde o início.
2. **Um método que reclama um prêmio não deve incorporar conteúdo de corpus com licença NC** (por exemplo, como dados de coaching, exemplos incorporados ou tabelas de consulta). O método transferido é destinado à implantação comercial pela organização de governança (BENCHMARK_SPEC §8.3, Method Submission Agreement §6); conteúdo com licença NC dentro dele prejudicaria essa implantação.
3. **Desenvolvedores podem usar livremente corpus com licença NC para desenvolver e auto-avaliar** — é para isso que a pista de desenvolvimento existe. A restrição se aplica ao que é enviado e ao que é implantado, não a como um desenvolvedor aprende.

### 1.6 Classes de Dependência Controlam Elegibilidade de Prêmios

Toda avaliação de prêmio acontece em um sandbox (§1.4), e métodos vencedores de prêmios são transferidos para a organização de governança (§1.3). Ambos os fatos impõem a mesma restrição: **tudo de que um método depende deve ser algo que o desenvolvedor tem o direito de colocar no sandbox e transmitir à comunidade.** Cada envio declara uma classe de dependência — definida na [especificação de Interface de Método](/docs/specifications/methods#method-validity-and-dependency-classes), com termos de admissibilidade no Method Submission Agreement §2.6 — e a elegibilidade segue a classe:

| Classe de dependência | Elegível para prêmio? | Condições |
|----------------------|----------------------|-----------|
| **S** — auto-contida | ✅ Sim | Nenhuma além das condições de limite em §2 |
| **O** — aberta externa (por exemplo, FST AGPL espelhado no envio) | ✅ Sim | Artefatos fixados e inclusos no envio; licenças permitem transferência comunitária; termos copyleft preservados (a comunidade recebe os mesmos direitos que a licença concede a todos) |
| **A1** — inferência LLM substituível | ⚠️ Condicional | Modelo declarado, fixado e substituível (deve executar contra um modelo de peso aberto hospedado pela comunidade); avaliação roteada através do gateway LLM do sandbox (🔲 planejado — métodos A1 não podem produzir pontuações de padrão ouro até que o gateway esteja operacional); transferência transmite a receita completa (prompts, coaching, código), não o modelo |
| **A2** — dados externos não-substituíveis/API de serviço | ❌ Ainda não | Inelegível até que o detentor dos direitos conceda permissões de inclusão em sandbox e transferência. Permitido no leaderboard aberto com uma flag visível de "dependência externa" |
| **X** — conteúdo agrupado sem direitos | ❌ Nunca | Inadmissível em todas as pistas |

A classe de um método é a classe mais restritiva entre suas dependências declaradas. Dependências não declaradas de qualquer classe são desqualificantes (§5).

---

## 2. Fundos de Prêmios Ativos

### 2.1 O Founder's Prize — EN→Plains Cree (nêhiyawêwin)

| Campo | Valor |
|-------|-------|
| **Fundo de prêmios** | **$10.000 CAD** |
| **Par de idiomas** | Inglês → Plains Cree (EN→CRK) |
| **Financiado por** | Fundador do projeto Champollion |
| **Status** | **ATIVO** — aceitando envios |
| **Abre** | Quando corpus de padrão ouro + organização de governança estiverem em vigor |
| **Expira** | Sem expiração. O prêmio permanece ativo até ser reclamado ou explicitamente retirado. |

#### Condições de Limite

Um método reclama o Founder's Prize atendendo **TODAS** as seguintes condições simultaneamente:

| # | Condição | Métrica | Limite | Justificativa |
|---|----------|---------|--------|---------------|
| 1 | **Pontuação composta** | `composite` (SCORING_SPEC §4) | **≥ 0,80** | Entre Deployable (0,70) e Fluent (0,85). Requer alta qualidade em todas as dimensões de métrica — não apenas validade morfológica. |
| 2 | **Aceitação FST** | `fst_acceptance_rate` (SCORING_SPEC §2.2) | **≥ 0,99 (99%+)** | Efetivamente todas as palavras de saída devem ser formas morfologicamente válidas reconhecidas pelo FST GiellaLT. A tolerância de 1% leva em conta casos extremos (nomes próprios, neologismos, empréstimos) que o FST pode legitimamente não cobrir. Este é o portão de qualidade definidor para MT polissintética — se o FST rejeita mais de 1% das palavras, o método está produzindo formas que não existem no idioma. O ponto inteiro deste prêmio é comprar um sistema que não destrói as coisas. |
| 3 | **chrF++** | `chrf_plus_plus` (SCORING_SPEC §2.1) | **≥ 55,0** | A sobreposição de n-gramas de caracteres deve exceder 55 na escala 0–100. Garante similaridade de nível de superfície com traduções de referência, não apenas validade morfológica. |
| 4 | **Validação comunitária** | Revisão humana (BENCHMARK_SPEC §7) | **≥ 70% "aceitável" ou "excelente"** | Uma amostra estratificada de saídas (≥30 entradas em níveis de dificuldade 2–5) é revisada por ≥2 falantes bilíngues de CRK. Pelo menos 70% das entradas revisadas devem receber uma classificação "aceitável" ou "excelente". |
| 5 | **Avaliação de padrão ouro** | Execução em sandbox (BENCHMARK_SPEC §8.2) | **Obrigatório** | Todas as métricas automatizadas devem ser computadas contra o segmento de corpus `gold_standard`, executado pela organização de governança em um ambiente em sandbox. Pontuações de conjunto de desenvolvimento não contam. |
| 6 | **Reprodutibilidade** | Correspondência de impressão digital (BENCHMARK_SPEC §3.8) | **±2%** | A organização de governança deve ser capaz de re-executar o método e alcançar pontuações dentro de ±2% da run card enviada. |

> **Por que 99+% FST?** O problema central na tradução automática para idiomas polissintéticos é alucinação — LLMs produzem strings que *parecem* o idioma alvo mas são morfologicamente inválidas. Um método que produz 95% de saída válida ainda tem 5% de palavras fabricadas — ruído inaceitável para qualquer uso em produção. O limite de 99%+ exige alucinação quase zero enquanto permite o caso raro (um nome próprio que o FST não conhece, um neologismo legítimo). Se um método não conseguir alcançar aceitação FST de 99%+, ele não resolveu o problema.
>
> **Por que 0,80 composto?** Isso fica entre Deployable (0,70) e Fluent (0,85). Um método em 0,80 com aceitação FST de 99%+ produz saída onde praticamente cada palavra é uma palavra real de Cree *e* a qualidade geral da tradução é alta em dimensões de superfície, estrutural e semântica. O portão de validação comunitária (condição #4) garante que isso não seja apenas gaming de métrica — falantes devem confirmar que a saída é genuinamente utilizável.

#### O Que Este Limite Significa na Prática

Em composto ≥ 0,80 com FST ≥ 0,99 e chrF++ ≥ 55, um falante bilíngue tipicamente veria:

- **Praticamente cada** palavra de saída é uma palavra real de Cree (FST valida 99%+ — formas alucinadas quase zero)
- Categorias gramaticais principais (pessoa, número, tempo) estão corretas na maioria das entradas
- A ordem das palavras é geralmente natural
- O significado é preservado de forma confiável
- Os erros restantes são erros de linguagem real (inflexão errada, obviation incorreta, incompatibilidades de animacy) — não palavras fabricadas
- Um falante fluente poderia usar a saída como um rascunho de alta qualidade e corrigi-lo significativamente mais rápido do que traduzir do zero

Este é um sistema que **não destrói o idioma.** Pode não ser perfeito, mas cada palavra que produz é uma palavra real. Essa é a barra mínima para tradução automática respeitosa de um idioma polissintético.

---

## 3. Processo de Reclamação de Prêmio

### 3.1 Envio

1. Desenvolvedor envia seu método completo e executável para a organização de governança:
   - Todo código-fonte
   - Todas as dependências (dados de coaching, dicionários, configurações FST, prompts)
   - Instruções de instalação e execução
   - Um README descrevendo a abordagem do método
   - Uma run card de conjunto de desenvolvimento mostrando pontuações aproximadas (para pré-triagem)

2. Desenvolvedor assina os termos de participação, incluindo:
   - Cláusula de transferência de propriedade (BENCHMARK_SPEC §8.3)
   - Declaração de não treinamento em dados de avaliação
   - Compromisso de reprodutibilidade

### 3.2 Avaliação

1. Organização de governança instala e executa o método em um harness em sandbox contra o corpus `gold_standard`
2. Métricas automatizadas são computadas (composto, FST, chrF++, etc.)
3. Se os limites automatizados são atendidos (condições 1–3), a organização de governança procede para revisão comunitária
4. Se os limites automatizados NÃO são atendidos, desenvolvedor recebe pontuações e feedback. Nenhuma revisão comunitária é acionada.

### 3.3 Revisão Comunitária

1. Uma amostra estratificada de saídas (≥30 entradas, cobrindo níveis de dificuldade 2–5) é apresentada a falantes bilíngues
2. No mínimo 2 revisores independentes classificam cada entrada
3. Escala de classificação: **rejeitar** / **gist** / **aceitável** / **excelente**
4. Se ≥70% das entradas recebem "aceitável" ou "excelente" de ambos os revisores, a validação comunitária passa

### 3.4 Pagamento

1. Todas as 6 condições são atendidas
2. Organização de governança confirma resultado
3. Prêmio é pago dentro de 30 dias da confirmação
4. Propriedade do método é transferida per BENCHMARK_SPEC §8.3
5. Resultado é publicado no leaderboard com nível de verificação "Community Validated"

### 3.5 Múltiplos Envios

- O mesmo desenvolvedor/equipe pode enviar múltiplas vezes
- Cada envio é avaliado independentemente
- Se um método é melhorado e re-enviado, apenas a run card mais recente conta
- O prêmio é concedido ao **primeiro** método que limpa todos os limites — não é dividido

### 3.6 Envios de Equipe

- Equipes e pares Elder-youth são elegíveis
- Distribuição de prêmio dentro de uma equipe é responsabilidade da equipe
- Todos os membros da equipe devem assinar os termos de participação
- Atribuição no leaderboard lista todos os membros da equipe

---

## 4. Fundos de Prêmios Futuros {#4-future-prize-pools}

O Founder's Prize é a semente. Fundos de prêmios adicionais são financiados por patrocinadores. Cada novo fundo de prêmios é documentado como uma nova subseção de §2 com seu próprio:

- Valor e moeda do prêmio
- Par de idiomas
- Atribuição de patrocinador
- Condições de limite (que podem diferir do Founder's Prize)
- Data de expiração (se houver)
- Quaisquer condições especiais

### 4.1 Modelo de Prêmio de Patrocinador

Patrocinadores financiam fundos de prêmios em qualquer valor. Níveis sugeridos:

| Nível | Valor | Limite Sugerido |
|-------|-------|-----------------|
| **Seed** | $5.000–$15.000 | Deployable (composto ≥ 0,70) + validação comunitária |
| **Breakthrough** | $25.000–$50.000 | Fluent (composto ≥ 0,85) + validação comunitária |
| **Grand Prize** | $100.000+ | Fluent + cobertura multi-registro + integração de implantação |

Patrocinadores também podem financiar:
- **Bounties de melhoria** — pagamento fixo para cada melhoria de 5 pontos em chrF++ sobre o melhor atual
- **Prêmios de registro** — prêmios separados para registros específicos (formal, cerimonial, educacional)
- **Prêmios de velocidade** — melhor pontuação ajustada por custo (SCORING_SPEC §6.3)

### 4.2 Escrow de Fundo de Prêmios

Todos os fundos de prêmios são mantidos em escrow (gerenciados pelo projeto ou um trustee designado) até que as condições de limite sejam atendidas. Se um prêmio expira sem ser reclamado, fundos são devolvidos ao patrocinador ou redirecionados para um novo fundo de prêmios a critério do patrocinador.

---

## 5. Desqualificação

Um envio é desqualificado se:

1. **Treinamento em dados de avaliação.** Método foi exposto a entradas de corpus `gold_standard` ou `held_out`. (Arquitetonicamente prevenido por execução em sandbox — mas se evidência de contaminação é encontrada, o resultado é anulado.)
2. **Não-reproduzível.** Organização de governança não consegue reproduzir pontuações dentro de ±2%.
3. **Dependências não declaradas ou inelegíveis.** O método requer acesso em tempo de execução a serviços externos além do que seu manifesto de dependência declara, ou sua classe de dependência efetiva é A2 ou X (§1.6). Inferência LLM de Classe A1 declarada roteada através do gateway de avaliação é permitida; qualquer outra dependência de rede em tempo de execução — e qualquer dependência não declarada de qualquer classe — é desqualificante.
4. **Termos de participação não assinados.** Todos os membros da equipe devem concordar com a transferência de propriedade.
5. **Gaming detectado.** Saída é otimizada para a métrica em vez de qualidade de tradução (capturado por revisão comunitária e/ou verificações anti-gaming per BENCHMARK_SPEC §9.3).

---

## 6. Relação com Outras Especificações

| Este Documento | Referencia | Para |
|----------------|-----------|------|
| §2 condições de limite | SCORING_SPEC §4 (composto), §2.1–2.2 (métricas), §5 (níveis) | Definições de métrica e escala |
| §2 validação comunitária | BENCHMARK_SPEC §7 | Protocolo de revisão humana |
| §3 execução em sandbox | BENCHMARK_SPEC §8.2 | Mecanismo de soberania |
| §3 transferência de propriedade | BENCHMARK_SPEC §8.3 | Termos de transferência de IP |
| §1.6 classes de dependência | Especificação de Interface de Método; Method Submission Agreement §2.6; BENCHMARK_SPEC §8.6 | Definições de classe, termos de admissibilidade, política de rede de sandbox |
| §4 prêmios ajustados por custo | SCORING_SPEC §6.3 | Fórmula ajustada por custo |

---

## 7. Sincronização Código–Especificação

### 7.1 Fonte Canônica

Este documento (`arena/website/docs/specifications/prize-spec.md`) é a fonte canônica para:
- Definições de fundo de prêmios (§2)
- Condições de limite (§2.x)
- Processo de reclamação (§3)
- Regras de desqualificação (§5)

### 7.2 Requisitos de Implementação

Quando um fundo de prêmios é ativado:
1. A UI do leaderboard deve exibir prêmios ativos e suas condições de limite
2. Run cards que atendem limites automatizados (condições 1–3) devem ser sinalizadas para revisão comunitária
3. O campo `quality_tier` no esquema de run card já captura o nível ("deployable", "fluent")
4. Nenhuma mudança de código nova no harness é necessária — a especificação de prêmio é uma camada de política em cima da pontuação existente

---

*Estruturas de prêmios devem ser compatíveis com termos de transferência de propriedade. O vencedor pode reclamar o prêmio, mas o método se torna propriedade da organização de governança se atingir nível Deployable. Isso é intencional — o prêmio financia a criação de tecnologia que pertence à comunidade linguística.*