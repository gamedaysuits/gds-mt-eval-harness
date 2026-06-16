---
sidebar_position: 1
title: For Language Communities
---

# For Language Communities

> **Executive Summary.** A guide for Indigenous and low-resource language speakers explaining how to contribute to the Arena (reference translations, translation review, coaching data) and what the community receives in return (code ownership, API revenue, full deployment control). No programming required.

You don't need to be a programmer to contribute to the Arena. If you speak an Indigenous or low-resource language, you are the most important person in this ecosystem.

---

## What We Need From You

### Reference translations

We need curated translation pairs for evaluation — English on one side, your language on the other. These become the "answer key" that all translation methods are scored against.

You might create these from:
- **Educational materials** — textbook exercises, lesson plans, worksheets
- **Community documents** — meeting minutes, newsletters, announcements
- **Everyday phrases** — UI strings, app labels, common expressions
- **Cultural content** — stories, songs, or descriptions (with appropriate permissions)

The format is simple JSON:
```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

### Translation review

Every method that claims to produce working translations needs human validation. Bilingual speakers review outputs and tell us whether the computer got it right — and more importantly, *why* it got it wrong.

### Coaching data

Grammar rules, dictionary entries, morphological patterns — these are the linguistic resources that make translation methods work. Your knowledge of how your language works is irreplaceable by any AI model.

---

## What You Get Back

### Ownership

When a translation method is built for your language and validated on the Arena, the [ownership transfers](/docs/sovereignty/ownership-transfer) to your community's governance organization. You own the code, the model weights, and the deployment.

### Revenue

When developers use your language's method through the champollion API, your community receives [90% of the API revenue](/docs/sovereignty/economic-model). The remaining 10% covers infrastructure costs.

### Control

Your governance organization controls:
- Who can access the method
- Whether it can be used commercially
- What pricing terms apply
- When and how it gets updated
- What data is used for further development

---

## How To Get Involved

1. **Reach out** — Open an issue on the [Arena repository](https://github.com/gamedaysuits/arena) or email the maintainers
2. **Describe your language** — What family is it in? How many speakers? What writing systems are used? What computational resources exist (FSTs, dictionaries, corpora)?
3. **Start small** — Even 50 curated translation pairs are enough to create an evaluation dataset and open a new leaderboard track
4. **Connect us to governance** — Who in your community has authority over language data and technology? The Arena's sovereignty model requires a governance partner

---

## Data Sovereignty

Your language data is yours. The Arena is built on [OCAP® principles](/docs/sovereignty/data-sovereignty):

- We never collect or store your linguistic data on our servers
- Translation methods use the `api` architecture — all coaching data, dictionaries, and grammar rules stay on infrastructure you control
- You decide who can develop methods for your language
- Leaderboard scores prove a method works; they do not grant permission to deploy it

---

## See Also

- [Data Sovereignty](/docs/sovereignty/data-sovereignty) — the full OCAP, CARE, and Te Mana Raraunga framework
- [Ownership Transfer](/docs/sovereignty/ownership-transfer) — what happens when a method wins
- [The Economic Model](/docs/sovereignty/economic-model) — how scores become revenue
- [Support a Low-Resource Language](/docs/community/low-resource-languages) — technical context for researchers working alongside communities
