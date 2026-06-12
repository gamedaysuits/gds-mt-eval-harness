---
sidebar_position: 10
title: "Cookbook: Bahagyang Pagsasalin (Tao + Makina)"
---
> **Ang ideya:** Manu-manong isalin ang isang representatibong sample, patunayang tumutugma ang inyong machine method sa istilo ng tao sa sample na iyon, pagkatapos ay awtomatikong isalin ang natitirang malaking bahagi. Pinagsasama nito ang kalidad ng tao at ang saklaw ng makina — ang tao ang nagtatakda ng pamantayan, at sinusundan ito ng makina.

:::info Ito ay cookbook, hindi tapos na implementasyon
Binabalangkas ng gabay na ito ang hybrid na workflow ng tao at makina. Lalo itong mahalaga para sa mga ahensiya ng pagsasalin, mga manggagawang pangkomunidad sa wika, at mga kontekstong pang-edukasyon.
:::

## Kailan Ito Gamitin

- Mayroon kayong **access sa matatas na tagapagsalita** ngunit limitado ang kanilang oras
- Kailangan ninyong magsalin ng **malaking volume** ngunit maliit na bahagi lamang ang kailangang maging perpekto
- Nais ninyong **magtatag ng batayang antas ng kalidad** gamit ang pagsasaling-tao, pagkatapos ay palawakin gamit ang MT
- Nagtatrabaho kayo sa isang **kontekstong pang-edukasyon o pangkomunidad** kung saan posible ang human review ng isang subset

## Paano Ito Gumagana

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

1. **Pumili ng representatibong sample** — saklawin ang iba’t ibang uri ng pangungusap, haba, at paksa
2. **Ipasalin sa tao ang sample** — itatag ang gold standard para sa istilo, rehistro, at terminolohiya
3. **I-configure ang inyong machine method** — gamitin ang mga pagsasaling-tao bilang coaching data, few-shot examples, o fine-tuning data
4. **I-score ang makina sa human sample** — tumutugma ba ang makina sa istilo ng tao?
5. **Awtomatikong isalin ang natitira** — kung katanggap-tanggap ang kalidad ng makina sa sample
6. **Opsyonal na human review** — markahan ang mga output na mababa ang kumpiyansa para sa pagsusuri ng tagapagsalita

## Quality Assurance: Ang Style Match Test

```bash
# Translate the human-translated sample with your machine method
python eval/baseline_experiment.py \
  --dataset data/human-sample.json \
  --condition coached-v3

# Compare: does the machine match the human translator's choices?
# Look at: chrF++ (similarity), FST acceptance (validity),
# and qualitative patterns (register, formality, terminology)
```

## Pagpili ng Sample

**Saklawin ang distribusyon.** Dapat isama ng inyong 100 entry ang:
- Maiikling parirala (1–3 salita) at buong pangungusap
- Karaniwang bokabularyo at mga terminong partikular sa domain
- Payak na estruktura at mas komplikadong estruktura
- Maramihang katangiang gramatikal (mga tanong, pautos, kondisyunal)

**Huwag piliin lamang ang madadali.** Dapat isama sa sample ang mga entry na malamang mahihirapan ang inyong method — doon pinakamahalaga ang kalidad ng tao.

## Ang Workflow ng Pagsusuring Pangkomunidad

Para sa mga komunidad ng Indigenous language, iginagalang ng pamamaraang ito ang oras ng tagapagsalita:

1. **Isinasalin ng tagapagsalita ang 50–100 entry** (2–4 na oras ng nakatuong gawain)
2. **Isinasalin ng makina ang natitirang 900** gamit ang gawa ng tagapagsalita bilang coaching data
3. **Sinusuri ng tagapagsalita ang mga minarkahang entry** — yaon lamang mga hindi gaanong kinumpiyansahan ng makina (karagdagang 1–2 oras)
4. **Resulta:** 1,000 pagsasalin sa kalidad na halos kapantay ng tao, gamit ang ~5 oras ng tagapagsalita sa halip na ~50

## Mga Kalamangan at Kahinaan

| | |
|---|---|
| ✅ Pinagsasama ang kalidad ng tao at ang saklaw ng makina | ❌ Nangangailangan ng paunang puhunan ng tao |
| ✅ Iginagalang ang limitadong availability ng tagapagsalita | ❌ Maaaring hindi makuha ng makina ang lahat ng estilistikong nuance |
| ✅ Natural na workflow ng quality assurance | ❌ Naaapektuhan ng pagpili ng sample ang kabuuang kalidad |
| ✅ Mahusay para sa mga kontekstong pangkomunidad/pang-edukasyon | ❌ Nagiging bottleneck ang human review para sa mga minarkahang entry |

## Mahusay Isama Sa

- **[Coached LLM Prompting](./coached-llm-prompting)** — ginagabayan ng mga pagsasaling-tao ang coaching data
- **[Few-Shot Prompting](./few-shot-prompting)** — mga pagsasaling-tao bilang in-context examples
- **[Corpus Creation](./corpus-creation)** — ang human sample AY corpus creation

## Tingnan Din

- [Para sa Mga Komunidad ng Wika](/docs/community/for-language-communities) — modelo ng pakikilahok ng komunidad
- [Data Sovereignty](/docs/sovereignty/data-sovereignty) — pagmamay-ari ng datos ng pagsasalin
- [Suportahan ang Isang Low-Resource Language](/docs/community/low-resource-languages)