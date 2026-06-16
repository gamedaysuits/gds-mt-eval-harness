---
sidebar_position: 2
title: "Kookboek: Coached LLM Prompting"
related:
  - label: "Cookbook: Few-Shot Prompting"
    to: /docs/tutorials/few-shot-prompting
    kind: cookbook
  - label: "Cookbook: Fine-Tuned Model"
    to: /docs/tutorials/fine-tuned-model
    kind: cookbook
  - label: "Coaching Data"
    to: https://champollion.dev/docs/concepts/coaching-data
    kind: champollion
    note: "How coaching data ships to production"
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
---
# Coached LLM Prompting

> **Het idee:** Injecteer grammaticaregels, tweetalige woordenboeken en stijlnotities rechtstreeks in de systeemprompt van het LLM. Geen training, geen fine-tuning — alleen gestructureerde taalkundige kennis die de uitvoer stuurt naar geldige vertalingen.

:::info Dit is een kookboek, geen kant-en-klare implementatie
Deze gids schetst de aanpak en de belangrijkste ontwerpbeslissingen. Pas het aan uw taalpaar, beschikbare bronnen en evaluatiedoelen aan.
:::

## Wanneer Dit Te Gebruiken

- U beschikt over **taalkundige kennis** over de doeltaal (grammaticaregels, woordenboekitems, stijlvoorkeuren), maar niet over voldoende parallelle data voor fine-tuning
- U wilt **snel itereren** — promptwijzigingen zijn in seconden uitgerold, zonder hertraining
- De doeltaal heeft **bekende patronen** die een LLM fout maakt (geslachtsovereenkomst, schriftconventies, formaliteitsniveaus)
- U wilt coached prompting benchmarken ten opzichte van een basislijn en itereren op wat werkt

## Hoe Het Werkt

1. **Stel coachingdata samen** — grammaticaregels, een tweetalig woordenboek en stijlnotities in een gestructureerd JSON-bestand
2. **Configureer het register** — een systeempromptprefix die de taal, het schrift en de toon instelt
3. **Voer de harness uit** — de coachingdata wordt in elke LLM-prompt geïnjecteerd
4. **Bekijk de fouten** — kijk naar wat de kwaliteitspoort afwijst en voeg regels toe om patronen aan te pakken
5. **Itereer** — elke revisie van het coachingbestand is een nieuw experiment; de harness houdt ze allemaal bij

## Structuur van de Coachingdata

```json title="coaching/<locale>.json"
{
  "grammar_rules": [
    "Adjectives agree in gender and number with the noun they modify",
    "Use formal register (vous) for all UI text",
    "Preserve interpolation variables exactly: {{name}}, {count}"
  ],
  "dictionary": {
    "dashboard": "tableau de bord",
    "settings": "paramètres",
    "deploy": "déployer"
  },
  "style_notes": "Prefer active voice. Avoid anglicisms where a native term exists. Keep sentences concise for UI readability."
}
```

## Belangrijkste Ontwerpbeslissingen

**Regelspecificiteit versus contextvenster:** Meer regels geven het LLM meer sturing, maar nemen ruimte in van het contextvenster dat beschikbaar is voor de eigenlijke vertaling. Begin met 5–10 regels met grote impact en voeg er meer toe alleen wanneer u specifieke foutpatronen ziet.

**Woordenboekdekking:** U hebt geen volledig woordenboek nodig — focus op termen die het LLM consequent fout maakt. Zelfs 20–30 afgedwongen termen kunnen de consistentie aanzienlijk verbeteren.

**Volgorde van regels is belangrijk:** Zet de belangrijkste regels eerst. LLM's hechten meer gewicht aan vroege instructies.

## Een Experiment Uitvoeren

```bash
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v1 \
  --coaching-file coaching/crk.json
```

## Voor- en Nadelen

| | |
|---|---|
| ✅ Geen trainingskosten | ❌ Kwaliteitsplafond beperkt door de basiskennis van het LLM |
| ✅ Directe iteratie (prompt wijzigen → opnieuw uitvoeren) | ❌ Contextvenster beperkt hoeveel coaching er past |
| ✅ Werkt met elke LLM-provider | ❌ Regels kunnen conflicteren — het debuggen van promptinteracties is een kunst |
| ✅ Transparant — u kunt exact lezen wat het LLM ziet | ❌ Creëert geen nieuwe kennis, stuurt alleen bestaande kennis |

## Combineert Goed Met

- **[FST-Gated Pipeline](./fst-gated-pipeline)** — coaching + morfologische validatie vangt wat coaching alleen mist
- **[Dictionary-Augmented LLM](./dictionary-augmented-llm)** — afgedwongen terminologie is een vorm van coaching
- **[Few-Shot Prompting](./few-shot-prompting)** — voorbeelden en regels samen zijn krachtiger dan elk afzonderlijk

## Zie Ook

- [Method Interface](/docs/specifications/methods) — indeling van coachingdata en het TranslationMethod-protocol
- [Support a Low-Resource Language](/docs/community/low-resource-languages) — de volledige context
- [Eval Harness](/docs/specifications/harness) — hoe u experimenten uitvoert