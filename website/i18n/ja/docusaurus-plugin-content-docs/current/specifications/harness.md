---
sidebar_position: 2
title: "Eval Harness v2.0"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "What the harness metrics feed into"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: Translate 30 Languages"
    to: https://champollion.dev/docs/tutorials/translate-30-languages
    kind: champollion
    note: "Use the harness to audit registers in production"
---
# Eval Harness v2.0

> **エグゼクティブサマリー。** このページでは、MT評価ハーネスのインストール、設定、および使用方法について説明します。MT評価ハーネスは、翻訳手法を標準化されたコーパスに対してベンチマークし、スコア付きのランカードを生成するツールです。メトリクス、スキーマ、および評価プロトコルの正式な定義については、[ベンチマーク仕様](/docs/specifications/benchmark)を参照してください。

ハーネスは翻訳実験を実行し、ランカードを生成します。プロンプトの構築、API呼び出し、スコアリング、および結果のシリアライズを処理します。データセットとモデルはユーザーが用意します。

## インストール

**要件:** Python 3.10以上

```bash
pip install sacrebleu aiohttp
```

ハーネスのリポジトリをクローンします：

```bash
git clone https://github.com/gamedaysuits/arena.git
cd arena
```

## 使用方法

```bash
mt-eval run --corpus path/to/dataset.json
```

これにより、コーパス内のすべてのエントリが設定済みのモデル（またはメソッドプラグイン）を通じて処理され、出力がスコアリングされ、ランカードのJSONファイルが出力ディレクトリに書き込まれます。

## CLIフラグ

### `mt-eval run`

| フラグ | 必須 | デフォルト | 説明 |
|------|----------|---------|-------------|
| `--corpus` | ✅ | — | コーパスファイルへのパス（`.json`、`.jsonl`、`.tsv`） |
| `--source-file` / `--reference-file` | — | — | 対訳テキストファイル（FLORES+、WMT形式） |
| `-m, --model` | — | `gemini-pro` | モデルスラッグ（短縮名またはOpenRouterのフルID）。`shared/model-aliases.json`を通じて解決されます。マルチモデル実行の場合はカンマ区切り |
| `-d, --dataset` | — | `all` | データセットフィルター：`all`、セグメント名、またはIDの範囲 |
| `--ids` | — | — | 評価するエントリIDのカンマ区切りリスト |
| `--source-lang` | — | `English` | ソース言語名 |
| `--target-lang` | — | — | ターゲット言語名 |
| `-p, --prompt` | — | `naive` | プロンプトバージョン（`naive`、`custom`、`champollion`） |
| `--coaching-file` | — | — | コーチングプロンプトテキストファイルへのパス |
| `--coaching` | — | — | インラインコーチングテキスト（引用文字列） |
| `--method` | — | — | メソッドプラグインディレクトリへのパス（`method.json`とPythonモジュールを含む） |
| `--method-card` | — | — | リーダーボードメタデータ用のメソッドカードJSONへのパス |
| `--fst-retries` | — | `0` | FSTリトライ試行回数（デフォルトLLMメソッドのみ） |
| `--skip-fst` | — | `false` | FSTクオリティゲートを完全にスキップする |
| `--tools` | — | `false` | ツール呼び出しモードを有効にする |
| `--tools-list` | — | — | ツール名のカンマ区切りリスト |
| `--max-tool-rounds` | — | `8` | エントリごとのツール呼び出しの最大ラウンド数 |
| `--hooks` | — | — | 翻訳後フック名 |
| `--style-profile` | — | — | スタイルプロファイルJSONへのパス。文章スタイルの一貫性メトリクスを有効にします（情報提供のみ — コンポジットスコアには含まれません。[§ 文章スタイルおよびレジスターメトリクス](#writing-style-and-register-metrics-informational)を参照） |
| `-b, --batch-size` | — | `25` | API呼び出しごとのエントリ数 |
| `-c, --concurrency` | — | `8` | 並列API呼び出し数 |
| `--max-tokens` | — | `32768` | API呼び出しごとの最大トークン数 |
| `--temperature` | — | `0.0` | サンプリング温度（0.0 = 決定論的） |
| `--no-cache` | — | `false` | レスポンスキャッシュを無効にする |
| `--cache-dir` | — | `eval/cache/harness` | キャッシュディレクトリのパス |
| `-o, --output-dir` | — | `eval/logs/harness` | ランカードとログの出力ディレクトリ |
| `-n, --name` | — | — | 人間が読めるラン名 |
| `--dry-run` | — | `false` | API呼び出しを行わずに設定を検証する |
| `--champollion-config` | — | — | `champollion.config.json`へのパス |
| `--champollion-cards-dir` | — | — | 言語カードのディレクトリ |
| `--target-lang-code` | — | — | BCP-47言語コード |

### その他のサブコマンド

| サブコマンド | 説明 |
|------------|-------------|
| `mt-eval test <log_path>` | 完了したランログを分析する |
| `mt-eval publish <report_path>` | ランカードをリーダーボードに提出する |
| `mt-eval compare <logs...>` | 複数のランを並べて比較する |
| `mt-eval dashboard <logs...>` | ランログからHTMLダッシュボードを生成する |
| `mt-eval list models\|prompts\|datasets` | 利用可能なリソースを一覧表示する |
| `mt-eval export` | 現在のセットアップをchampollionメソッドプラグインとしてパッケージ化する |
| `mt-eval export-config` | 解決済みのMethodConfig（全8つの正規フィールド）をJSONとしてエクスポートする |

### 使用例

```bash
# Run with defaults (gemini-pro alias → google/gemini-3.1-pro-preview, naive prompt)
mt-eval run --corpus data/edtekla-dev-v1.json

# Coached experiment with coaching file
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model google/gemini-3.1-pro \
  --coaching-file prompts/crk-coaching-v8.txt \
  --temperature 0.0

# Run a custom method plugin with FST retries
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --method ./methods/fst-gated-pipeline \
  --fst-retries 3
```

---

## ランカードスキーマ

すべての実験は**ランカード**（自己完結型のJSONドキュメント）を生成します。トップレベルの構造：

```json
{
  "run_id": "uuid-v4",
  "harness_version": "2.0",
  "model_slug": "google/gemini-3.1-pro",
  "model_id": "gemini-3.1-pro-001",
  "condition": "baseline",
  "timestamp": "2026-06-01T03:22:41Z",
  "elapsed_seconds": 142.7,
  "dataset": { ... },
  "config": { ... },
  "method_card": { ... },
  "system_prompt_sha256": "abc123...",
  "system_prompt_used": "You are a translator...",
  "fingerprint": { ... },
  "scores": { ... },
  "totals": { ... },
  "environment": { ... },
  "results": [ ... ],
  "run_card_hash": "sha256-of-entire-card"
}
```

すべてのフィールドが文書化された完全なスキーマについては、[ランカード仕様](/docs/specifications/run-card)を参照してください。

:::info 正式なスキーマ
[ベンチマーク仕様](/docs/specifications/benchmark)はランカードスキーマの唯一の信頼できる情報源です。メトリクスの定義、コンポジットの重み、および品質ティアについては、[スコアリング仕様](/docs/specifications/scoring)を参照してください。このページではハーネスの使用方法を説明しており、出力の意味は仕様書で定義されています。
:::

### 主要ブロック

**`dataset`** — 使用されたデータセットを識別します。コンテンツハッシュを含み、結果が特定のバージョンに紐付けられます：

```json
// Example using master_corpus.json (62 gold + 342 textbook = 404)
{
  "id": "edtekla-dev-v1",
  "version": "1.0",
  "language_pair": "EN→CRK",
  "sha256": "...",
  "entry_count": 404
}
```

**`scores`** — ランの集計メトリクス：

```json
// Counts reflect the dataset used (here: master_corpus.json, 404 entries)
{
  "total": 404,
  "exact_matches": 12,
  "exact_match_rate": 0.0968,
  "fst_accepted": 87,
  "fst_acceptance_rate": 0.7016,
  "chrf_plus_plus": 42.31,
  "errors": 0,
  "avg_latency_seconds": 1.15,
  "median_latency_seconds": 1.02,
  "p95_latency_seconds": 2.34,
  "by_difficulty": { ... },
  "by_provenance": { ... }
}
```

**`totals`** — トークン使用量とコストの追跡：

```json
{
  "prompt_tokens": 48200,
  "completion_tokens": 3100,
  "reasoning_tokens": 0,
  "cached_tokens": 12000,
  "total_cost_usd": 0.42,
  "cost_per_entry_usd": 0.0034,
  "reasoning_ratio": 0.0
}
```

---

## 文章スタイルおよびレジスターメトリクス（情報提供のみ）

ハーネスは、`WritingStyleConsistency`メトリクスプラグイン（`mt_eval_harness/plugins/writing_style.py`）を通じて、翻訳がターゲットの**レジスター**および**文章スタイル**に一致しているかどうかを評価できます。翻訳は言語的に正確であっても、レジスターが誤っている場合があります。たとえば、法律文書でのくだけた表現や、マーケティングコピーでの堅苦しい定型文などです。文字列メトリクスではこれを検出できませんが、これらのメトリクスは検出できます。

**測定内容（エントリごと）：**

| メトリクス | スケール | 意味 |
|--------|-------|---------|
| `style_register_match` | boolean | 出力が期待されるレジスターと一致しているか？ターゲットはコーパスエントリの`register`フィールド（[ベンチマーク仕様 §2.6](/docs/specifications/benchmark)を参照）またはスタイルプロファイルから取得されます |
| `style_sentence_length_ratio` | float | 予測値と参照値の平均文長の比較（1.0 = 一致；乖離 = スタイルドリフト） |
| `style_formality_score` | 0.0–1.0 | 丁寧語・くだけた表現のマーカーの存在（T–V代名詞、短縮形など）。言語ごとのマーカーリソースを使用 |

**集計：** `style_consistency_rate` — レジスターの不一致が検出されなかったエントリの割合。

`--style-profile path/to/profile.json`でカスタムターゲットを有効にします（例：ブランドボイスプロファイル）。指定がない場合、プラグインは各コーパスエントリの`register`メタデータ（存在する場合）にフォールバックします。

:::caution 適用範囲について
これらのメトリクスは**情報提供のみ**です。コンポジットスコアには含まれず、フォーマリティ検出はマーカーベース（ヒューリスティック）であり、学習済みの判断ではありません。スタイル品質の判定としてではなく、レジスター遵守のドリフト検出器として扱ってください。
:::

---

## フィンガープリントとランカードハッシュ

ハーネスは2つの異なるハッシュを生成します。それぞれ異なる目的を持っています。

### フィンガープリント

**フィンガープリント**が答える問い：*「このランは再現可能か？」*

出力ではなく、実験設定を定義する入力の組み合わせをハッシュ化します：

- データセットのSHA-256
- モデルスラッグ
- 条件ラベル
- システムプロンプトのSHA-256
- 温度
- ハーネスバージョン

フィンガープリントが同一の2つのランは、同じセットアップを使用しています。その結果は比較可能なはずです（APIの非決定性を除く）。

### ランカードハッシュ

**ランカードハッシュ**が答える問い：*「この特定の結果ファイルは改ざんされていないか？」*

ランカードJSON全体のSHA-256です（`run_card_hash`フィールド自体を除く）。スコア、タイムスタンプ、単一の出力など、いずれかのフィールドが変更されるとハッシュが壊れます。

:::info どちらを使うべきか
比較可能なランをグループ化する場合（同じ実験、異なる実行）は**フィンガープリント**を使用してください。特定の結果ファイルの整合性を検証する場合は**ランカードハッシュ**を使用してください。
:::

---

## リーダーボードへの公開

ランが完了したら、`mt-eval publish`を使用してランカードを提出します：

```bash
mt-eval publish eval/logs/harness/your-run-card.json
```

ランの実行時に`--method-card`が指定されていない場合、`mt-eval publish`はインタラクティブウィザード（`method_card_wizard.py`）を起動し、メソッドの説明（名前、クラス、使用ツールなど）を順を追って入力できます。ウィザードの出力は提出前にランカードに埋め込まれます。

### 手動提出

ランカードはJSONファイルとして出力ディレクトリに保存されます。[/leaderboard](https://champollion.dev/leaderboard)のリーダーボードUIから任意のランカードファイルを提出することも、APIを通じて提出することもできます：

```bash
curl -X POST https://champollion.dev/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @eval/logs/harness/your-run-card.json
```

:::warning リーダーボードの検証
リーダーボードは提出されたランカードをデータセットレジストリに対して検証します。未知のデータセットを参照している提出や、`run_card_hash`が壊れている提出は拒否されます。
:::

:::danger 評価データでのトレーニング禁止
評価データセットを開発中に見たことがある場合（トレーニングデータ、few-shotの例、辞書エントリ、またはプロンプトエンジニアリング素材として）、提出は**失格**となります。良いメソッドと悪いメソッドについては、[MT Evaluation](/docs/leaderboard/rules)を参照してください。
:::

---

## 関連情報

- [MT Evaluation](/docs/leaderboard/rules) — 概要、リーダーボードの価値提案、良いメソッドと悪いメソッドのガイダンス
- [評価データセット](/docs/leaderboard/datasets) — データセット形式、EDTeKLA、FLORES+
- [ランカード仕様](/docs/specifications/run-card) — 完全なJSONスキーマ
- [メソッドの構築](/docs/specifications/methods) — 評価可能なメソッドを作成するためのメソッドインターフェース
- [メソッドリーダーボード](https://champollion.dev/leaderboard) — ライブベンチマークスコア
- [ベンチマーク仕様](/docs/specifications/benchmark) — 評価プロトコル、コーパス形式、ランカードスキーマ
- [スコアリング仕様](/docs/specifications/scoring) — メトリクス、コンポジットの重み、および品質ティアのSSoT