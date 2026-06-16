---
sidebar_position: 1
title: "Para Comunidades de Linguagem"
---
# Para Comunidades Linguísticas

> **Resumo Executivo.** Um guia para falantes de línguas indígenas e de baixo recurso explicando como contribuir para a Arena (traduções de referência, revisão de tradução, dados de treinamento) e o que a comunidade recebe em troca (propriedade do código, receita de API, controle total de implantação). Nenhuma programação necessária.

Você não precisa ser programador para contribuir para a Arena. Se fala uma língua indígena ou de baixo recurso, você é a pessoa mais importante neste ecossistema.

---

## O Que Precisamos De Você

### Traduções de referência

Precisamos de pares de tradução curados para avaliação — inglês de um lado, sua língua do outro. Estes se tornam a "chave de resposta" contra a qual todos os métodos de tradução são avaliados.

Você pode criar estes a partir de:
- **Materiais educacionais** — exercícios de livros didáticos, planos de aula, folhas de trabalho
- **Documentos comunitários** — atas de reuniões, boletins informativos, anúncios
- **Frases do dia a dia** — strings de interface, rótulos de aplicativos, expressões comuns
- **Conteúdo cultural** — histórias, músicas ou descrições (com permissões apropriadas)

O formato é JSON simples:
```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

### Revisão de tradução

Todo método que afirma produzir traduções funcionais precisa de validação humana. Falantes bilíngues revisam os resultados e nos dizem se o computador acertou — e mais importante ainda, *por que* errou.

### Dados de treinamento

Regras gramaticais, entradas de dicionário, padrões morfológicos — estes são os recursos linguísticos que fazem os métodos de tradução funcionarem. Seu conhecimento de como sua língua funciona é insubstituível por qualquer modelo de IA.

---

## O Que Você Recebe Em Troca

### Propriedade

Quando um método de tradução é construído para sua língua e validado na Arena, a [propriedade é transferida](/docs/sovereignty/ownership-transfer) para a organização de governança da sua comunidade. Você possui o código, os pesos do modelo e a implantação.

### Receita

Quando desenvolvedores usam o método da sua língua através da API champollion, sua comunidade recebe [90% da receita de API](/docs/sovereignty/economic-model). Os 10% restantes cobrem custos de infraestrutura.

### Controle

Sua organização de governança controla:
- Quem pode acessar o método
- Se pode ser usado comercialmente
- Quais termos de preço se aplicam
- Quando e como é atualizado
- Quais dados são usados para desenvolvimento futuro

---

## Como Se Envolver

1. **Entre em contato** — Abra uma issue no [repositório da Arena](https://github.com/gamedaysuits/arena) ou envie um email para os mantenedores
2. **Descreva sua língua** — A qual família pertence? Quantos falantes tem? Quais sistemas de escrita são usados? Quais recursos computacionais existem (FSTs, dicionários, corpora)?
3. **Comece pequeno** — Até 50 pares de tradução curados são suficientes para criar um conjunto de dados de avaliação e abrir uma nova faixa de leaderboard
4. **Conecte-nos à governança** — Quem em sua comunidade tem autoridade sobre dados e tecnologia linguística? O modelo de soberania da Arena requer um parceiro de governança

---

## Soberania de Dados

Seus dados linguísticos são seus. A Arena é construída sobre [princípios OCAP®](/docs/sovereignty/data-sovereignty):

- Nunca coletamos ou armazenamos seus dados linguísticos em nossos servidores
- Métodos de tradução usam a arquitetura `api` — todos os dados de treinamento, dicionários e regras gramaticais permanecem em infraestrutura que você controla
- Você decide quem pode desenvolver métodos para sua língua
- Pontuações de leaderboard provam que um método funciona; elas não concedem permissão para implantá-lo

---

## Veja Também

- [Soberania de Dados](/docs/sovereignty/data-sovereignty) — o framework completo OCAP, CARE e Te Mana Raraunga
- [Transferência de Propriedade](/docs/sovereignty/ownership-transfer) — o que acontece quando um método vence
- [O Modelo Econômico](/docs/sovereignty/economic-model) — como pontuações se tornam receita
- [Apoiar uma Língua de Baixo Recurso](/docs/community/low-resource-languages) — contexto técnico para pesquisadores trabalhando ao lado de comunidades