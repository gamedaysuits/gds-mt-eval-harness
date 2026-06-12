---
sidebar_position: 2
title: "Cookbook: Ginabayang LLM Prompting"
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
# May Gabay na LLM Prompting

> **Ang ideya:** Direktang ipasok ang mga tuntunin sa gramatika, bilingual dictionaries, at mga tala sa estilo sa system prompt ng LLM. Walang training, walang fine-tuning — tanging nakabalangkas na kaalamang lingguwistiko na gumagabay sa output tungo sa wastong mga salin.

:::info Ito ay isang cookbook, hindi isang tapos na implementation
Binabalangkas ng gabay na ito ang diskarte at ang mahahalagang desisyon sa disenyo nito. Iangkop ito sa inyong pares ng wika, mga available na resource, at mga layunin sa evaluation.
:::

## Kailan Ito Gagamitin

- Mayroon kayong **kaalamang lingguwistiko** tungkol sa target na wika (mga tuntunin sa gramatika, mga entry sa dictionary, mga kagustuhan sa estilo) ngunit hindi sapat ang parallel data para sa fine-tuning
- Nais ninyong **mabilis na mag-iterate** — nade-deploy ang mga pagbabago sa prompt sa loob ng ilang segundo, nang walang retraining
- Ang target na wika ay may **kilalang mga pattern** na madalas magkamali ang LLM (gender agreement, mga kombensiyon sa script, mga antas ng pormalidad)
- Nais ninyong i-benchmark ang may gabay na prompting laban sa baseline at mag-iterate batay sa kung ano ang gumagana

## Paano Ito Gumagana

1. **Tipunin ang coaching data** — mga tuntunin sa gramatika, isang bilingual dictionary, at mga tala sa estilo sa isang nakabalangkas na JSON file
2. **I-configure ang rehistro** — isang system prompt prefix na nagtatakda ng wika, script, at tono
3. **Patakbuhin ang harness** — ipinapasok ang coaching data sa bawat LLM prompt
4. **Suriin ang mga failure** — tingnan kung ano ang nire-reject ng quality gate, magdagdag ng mga tuntunin upang tugunan ang mga pattern
5. **Mag-iterate** — bawat rebisyon ng coaching file ay isang bagong eksperimento; sinusubaybayan ng harness ang lahat ng ito

## Estruktura ng Coaching Data

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

## Mahahalagang Desisyon sa Disenyo

**Pagiging espesipiko ng tuntunin vs. context window:** Mas maraming tuntunin ang nagbibigay sa LLM ng mas maraming gabay, ngunit kumakain ito ng context window na available para sa aktuwal na pagsasalin. Magsimula sa 5–10 tuntuning may mataas na epekto at magdagdag lamang kapag may nakita kayong partikular na mga pattern ng failure.

**Saklaw ng dictionary:** Hindi ninyo kailangan ng kumpletong dictionary — magpokus sa mga terminong palagiang mali ang LLM. Kahit 20–30 forced terms ay maaaring lubos na magpahusay ng consistency.

**Mahalaga ang pagkakasunod-sunod ng mga tuntunin:** Ilagay muna ang pinakamahahalagang tuntunin. Mas malakas na binibigyang-pansin ng mga LLM ang mga naunang instruction.

## Pagpapatakbo ng Eksperimento

```bash
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v1 \
  --coaching-file coaching/crk.json
```

## Mga Kalamangan at Kahinaan

| | |
|---|---|
| ✅ Walang gastos sa training | ❌ Limitado ang quality ceiling ng base knowledge ng LLM |
| ✅ Agarang iteration (baguhin ang prompt → patakbuhin muli) | ❌ Nililimitahan ng context window kung gaano karaming coaching ang kasya |
| ✅ Gumagana sa anumang LLM provider | ❌ Maaaring magkasalungatan ang mga tuntunin — isang sining ang pag-debug ng prompt interactions |
| ✅ Transparent — mababasa ninyo nang eksakto kung ano ang nakikita ng LLM | ❌ Hindi lumilikha ng bagong kaalaman, ginagabayan lamang ang umiiral na kaalaman |

## Mainam Isama Sa

- **[FST-Gated Pipeline](./fst-gated-pipeline)** — nahuhuli ng coaching + morphological validation ang mga hindi nahuhuli ng coaching lamang
- **[Dictionary-Augmented LLM](./dictionary-augmented-llm)** — ang forced terminology ay isang anyo ng coaching
- **[Few-Shot Prompting](./few-shot-prompting)** — mas makapangyarihan ang mga halimbawa + tuntunin nang magkasama kaysa alinman sa mga ito nang nag-iisa

## Tingnan Din

- [Method Interface](/docs/specifications/methods) — format ng coaching data at ang TranslationMethod protocol
- [Support a Low-Resource Language](/docs/community/low-resource-languages) — ang buong konteksto
- [Eval Harness](/docs/specifications/harness) — kung paano magpatakbo ng mga eksperimento