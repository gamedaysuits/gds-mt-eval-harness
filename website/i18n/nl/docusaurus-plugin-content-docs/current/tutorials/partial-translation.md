---
sidebar_position: 10
title: "Kookboek: Gedeeltelijke Vertaling (Mens + Machine)"
---
# Gedeeltelijke Vertaling (Mens + Machine)

> **Het idee:** Vertaal handmatig een representatief steekproef, bewijs dat uw machinale methode de menselijke stijl op dat steekproef evenaart, en vertaal vervolgens automatisch de resterende bulk. Combineert menselijke kwaliteit met machinale schaal — de mens stelt de norm, de machine volgt die.

:::info Dit is een kookboek, geen afgeronde implementatie
Deze gids schetst de hybride mens-machine-workflow. Hij is bijzonder relevant voor vertaalbureaus, gemeenschapstaalwerkers en educatieve contexten.
:::

## Wanneer Dit Te Gebruiken

- U heeft **toegang tot vloeiende sprekers**, maar hun tijd is beperkt
- U moet een **groot volume** vertalen, maar slechts een klein deel hoeft perfect te zijn
- U wilt een **kwaliteitsbasislijn vaststellen** met menselijke vertaling en vervolgens opschalen met MT
- U werkt in een **educatieve of gemeenschapscontext** waar menselijke beoordeling van een deelverzameling haalbaar is

## Hoe Het Werkt

```
[Full corpus: 1,000 entries]
        │
        ├── [100 entries] ──→ Human translator ──→ Gold translations
        │                                              │
        │                                              ▼
        │                                    Train / prompt machine
        │                                    method to match style
        │                                              │
        └── [900 entries] ──→ Machine method ──→ Auto translations
                                                       │
                                                       ▼
                                              [Optional: human review
                                               of flagged entries]
```

1. **Selecteer een representatief steekproef** — dek verschillende zinstypen, lengtes en onderwerpen af
2. **Vertaal het steekproef handmatig** — stel de gouden standaard vast voor stijl, register en terminologie
3. **Configureer uw machinale methode** — gebruik de menselijke vertalingen als coachingdata, few-shot-voorbeelden of fijnafstemmingsdata
4. **Beoordeel de machine op het menselijke steekproef** — evenaart de machine de stijl van de mens?
5. **Vertaal de rest automatisch** — als de machinekwaliteit op het steekproef acceptabel is
6. **Optionele menselijke beoordeling** — markeer uitvoer met lage betrouwbaarheid voor beoordeling door sprekers

## Kwaliteitsborging: De Stijlovereenkomsttest

```bash
# Translate the human-translated sample with your machine method
python eval/baseline_experiment.py \
  --dataset data/human-sample.json \
  --condition coached-v3

# Compare: does the machine match the human translator's choices?
# Look at: chrF++ (similarity), FST acceptance (validity),
# and qualitative patterns (register, formality, terminology)
```

## Het Steekproef Selecteren

**Dek de verdeling af.** Uw 100 vermeldingen moeten bevatten:
- Korte zinsdelen (1–3 woorden) en volledige zinnen
- Gangbare woordenschat en domeinspecifieke termen
- Eenvoudige structuren en complexe structuren
- Meerdere grammaticale kenmerken (vragen, imperatieve zinnen, conditionele zinnen)

**Kies niet alleen de gemakkelijke gevallen.** Het steekproef moet vermeldingen bevatten waarmee uw methode waarschijnlijk moeite zal hebben — daar is menselijke kwaliteit het meest van belang.

## De Gemeenschapsbeoordelingsworkflow

Voor inheemse taalgemeenschappen respecteert deze aanpak de tijd van sprekers:

1. **De spreker vertaalt 50–100 vermeldingen** (2–4 uur geconcentreerd werk)
2. **De machine vertaalt de resterende 900** met het werk van de spreker als coachingdata
3. **De spreker beoordeelt gemarkeerde vermeldingen** — alleen de vermeldingen waarbij de machine het minst zeker was (nog eens 1–2 uur)
4. **Resultaat:** 1.000 vertalingen van bijna-menselijke kwaliteit, met ~5 uur sprekersinzet in plaats van ~50

## Voor- en Nadelen

| | |
|---|---|
| ✅ Combineert menselijke kwaliteit met machinale schaal | ❌ Vereist een initiële menselijke investering |
| ✅ Respecteert beperkte beschikbaarheid van sprekers | ❌ De machine vangt mogelijk niet alle stilistische nuances op |
| ✅ Natuurlijke kwaliteitsborgingsworkflow | ❌ Steekproefselectie beïnvloedt de algehele kwaliteit |
| ✅ Uitstekend voor gemeenschaps-/educatieve contexten | ❌ Menselijke beoordelingsbottleneck voor gemarkeerde vermeldingen |

## Combineert Goed Met

- **[Coached LLM Prompting](./coached-llm-prompting)** — menselijke vertalingen voeden de coachingdata
- **[Few-Shot Prompting](./few-shot-prompting)** — menselijke vertalingen als in-context-voorbeelden
- **[Corpus Creation](./corpus-creation)** — het menselijke steekproef ÍS corpuscreatie

## Zie Ook

- [Voor Taalgemeenschappen](/docs/community/for-language-communities) — gemeenschapsbetrokkenheidsmodel
- [Data Sovereignty](/docs/sovereignty/data-sovereignty) — eigenaarschap van vertaaldata
- [Ondersteuning van een Taal met Weinig Middelen](/docs/community/low-resource-languages)