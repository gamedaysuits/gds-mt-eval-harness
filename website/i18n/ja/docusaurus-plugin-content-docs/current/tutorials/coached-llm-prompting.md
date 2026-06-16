---
sidebar_position: 2
title: "クックブック：コーチング付きLLMプロンプティング"
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
# コーチング付きLLMプロンプティング

> **アイデア:** 文法規則、バイリンガル辞書、スタイルノートをLLMのシステムプロンプトに直接注入します。トレーニングもファインチューニングも不要 — 構造化された言語知識だけで、出力を有効な翻訳へと誘導します。

:::info これはクックブックであり、完成した実装ではありません
このガイドはアプローチとその主要な設計上の判断を概説するものです。対象言語ペア、利用可能なリソース、および評価目標に合わせて適宜調整してください。
:::

## 使用すべき場面

- 対象言語に関する**言語的知識**（文法規則、辞書エントリ、スタイルの好み）はあるが、ファインチューニングに十分な対訳データがない場合
- **高速なイテレーション**を求めている場合 — プロンプトの変更は数秒でデプロイでき、再トレーニングは不要
- LLMが誤りやすい対象言語の**既知のパターン**がある場合（性の一致、文字表記の慣習、丁寧さのレベルなど）
- コーチング付きプロンプティングをベースラインと比較してベンチマークし、効果的な手法を繰り返し改善したい場合

## 仕組み

1. **コーチングデータを準備する** — 文法規則、バイリンガル辞書、スタイルノートを構造化されたJSONファイルにまとめる
2. **レジスターを設定する** — 言語、文字、トーンを指定するシステムプロンプトのプレフィックスを作成する
3. **ハーネスを実行する** — コーチングデータがすべてのLLMプロンプトに注入される
4. **失敗例を確認する** — 品質ゲートで棄却されたものを確認し、パターンに対処するための規則を追加する
5. **イテレーションを繰り返す** — コーチングファイルを改訂するたびに新しい実験となり、ハーネスがすべてを追跡する

## コーチングデータの構造

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

## 主要な設計上の判断

**規則の詳細度とコンテキストウィンドウのトレードオフ:** 規則が多いほどLLMへの誘導は強まりますが、実際の翻訳に使えるコンテキストウィンドウが削られます。影響の大きい規則を5〜10個から始め、特定の失敗パターンが見られた場合にのみ追加してください。

**辞書のカバレッジ:** 完全な辞書は必要ありません — LLMが一貫して誤る用語に絞って対応してください。20〜30語の強制用語だけでも、一貫性を大幅に向上させることができます。

**規則の順序が重要:** 最も重要な規則を先頭に置いてください。LLMは早い段階の指示により強く注目します。

## 実験の実行

```bash
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v1 \
  --coaching-file coaching/crk.json
```

## メリットとデメリット

| | |
|---|---|
| ✅ トレーニングコストがゼロ | ❌ 品質の上限はLLMの基礎知識に制限される |
| ✅ 即座のイテレーション（プロンプトを変更して再実行するだけ） | ❌ コンテキストウィンドウにより注入できるコーチング量が制限される |
| ✅ あらゆるLLMプロバイダーで動作する | ❌ 規則が競合する可能性があり、プロンプトの相互作用のデバッグは経験が必要 |
| ✅ 透明性が高い — LLMが受け取る内容をそのまま確認できる | ❌ 新しい知識を生み出すのではなく、既存の知識を誘導するだけ |

## 組み合わせると効果的な手法

- **[FSTゲート付きパイプライン](./fst-gated-pipeline)** — コーチングと形態論的バリデーションを組み合わせることで、コーチング単独では見逃すものを検出できる
- **[辞書拡張LLM](./dictionary-augmented-llm)** — 用語の強制はコーチングの一形態
- **[Few-Shotプロンプティング](./few-shot-prompting)** — 例示と規則を組み合わせると、それぞれ単独よりも効果が高い

## 関連情報

- [メソッドインターフェース](/docs/specifications/methods) — コーチングデータのフォーマットとTranslationMethodプロトコル
- [低リソース言語のサポート](/docs/community/low-resource-languages) — 全体的なコンテキスト
- [評価ハーネス](/docs/specifications/harness) — 実験の実行方法