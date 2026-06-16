---
sidebar_position: 1
title: "手法を登録する"
related:
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
    note: "The contract your method implements"
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
    note: "What every published run must disclose"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Cookbook: Few-Shot Prompting"
    to: /docs/tutorials/few-shot-prompting
    kind: cookbook
    note: "The fastest first method to submit"
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
---
# メソッドを提出する

> **概要。** リーダーボードへの最初のベンチマーク実行を提出するためのステップバイステップのクイックスタートです。ハーネスをクローンし、データセットに対して実行し、ランカードを確認して提出します。APIキーがあれば10分で完了します。

このガイドでは、MT Eval Arena リーダーボードへの最初のベンチマーク実行を提出する手順を説明します。

---

## 前提条件

- **Python 3.10+**
- **OpenRouter APIキー**（またはご利用のモデルプロバイダーに対応するもの）
- **翻訳メソッド** — ソーステキストから翻訳を生成するものであれば何でも構いません

```bash
# Clone the eval harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install sacrebleu aiohttp
```

---

## ステップ 1: ハーネスを実行する

ハーネスは、標準化されたデータセットに対してメソッドをスコアリングします：

```bash
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model gemini-pro \
  --condition your-method-name \
  --temperature 0.2
```

| フラグ | 説明 |
|---|---|
| `--corpus` | 評価コーパスへのパス（`.json`、`.jsonl`、`.tsv`） |
| `--model` | モデルスラッグ — 短いエイリアス（例：`gemini-pro`）またはフル OpenRouter ID |
| `--condition` | メソッドのラベル（リーダーボードに表示されます） |
| `--temperature` | サンプリング温度（低いほど決定論的） |
| `--fst-retries` | オプション：FST リトライ試行回数 |
| `--submit` | ランカードをリーダーボードへ自動提出する |

ハーネスは**ランカード**を生成します。これは、スコア、データセットハッシュ、モデルスラッグ、および結果を正確な実験設定に紐付ける暗号学的フィンガープリントを含む自己完結型の JSON ファイルです。

---

## ステップ 2: ランカードを確認する

ランカードは `results/` に保存されます。提出前に内容を確認してください：

```bash
cat results/your-run-card.json | python -m json.tool
```

確認すべき主なフィールド：
- `scores.chrf_plus_plus` — 主要な品質メトリクス
- `scores.exact_match_rate` — 完全翻訳の割合
- `scores.fst_acceptance_rate` — 形態論的妥当性（FST を使用した場合）
- `totals.total_cost_usd` — 実行にかかったコスト
- `fingerprint` — 実験の再現性ハッシュ

完全なスキーマについては、[ランカード仕様](/docs/specifications/run-card)を参照してください。

---

## ステップ 3: 提出する

### 自動提出

ハーネス実行時に `--submit` を指定した場合、ランカードはすでにアップロードされています。

### 手動提出

API を使用して任意のランカードを提出できます：

```bash
curl -X POST https://mtevalarena.org/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @results/your-run-card.json
```

または [リーダーボード UI](https://champollion.dev/leaderboard) からアップロードすることもできます。

---

## 提出後の流れ

1. 提出内容が検証されます（データセットハッシュ、ランカードの整合性）
2. 結果が**Self-benchmarked**（信頼ティア 1）としてリーダーボードに表示されます
3. **GDS Verified** ステータスを取得するには、メンテナーが結果を再現できるよう、インストール可能なプラグインとしてメソッドを提出してください
4. 先住民言語のメソッドの場合：メソッドがトップに達した場合、[所有権移転](/docs/sovereignty/ownership-transfer)プロセスが開始されます

---

## 関連情報

- [ハーネスの使い方](/docs/specifications/harness) — 完全な CLI リファレンス
- [リーダーボードルール](/docs/leaderboard/rules) — 提出基準および不正防止ポリシー
- [メソッドの構築](/docs/specifications/methods) — TranslationMethod プロトコル
- [データセット](/docs/leaderboard/datasets) — 利用可能な評価データセット