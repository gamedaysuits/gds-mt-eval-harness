---
sidebar_position: 3
title: "評価データセット"
related:
  - label: "Corpus Design Framework"
    to: /docs/specifications/corpus-design
    kind: spec
    note: "How evaluation corpora are constructed"
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "Build a corpus for your language"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
---
# 評価データセット

> **概要。** このページでは、ベンチマークに使用できる評価データセットについて説明します。コーパスエントリのスキーマ、難易度ティア（1〜5）、および出典要件が含まれます。現在利用可能なデータセット：EDTeKLA Dev v1（Plains Cree、合計548エントリ：テキストブック486件＋ゴールドスタンダード62件）および FLORES+ Devtest（39言語、各1,012エントリ）。

データセットは、ハーネスが実行する固定のターゲットです。各データセットは、ソース→ターゲットのペアとゴールドスタンダード参照訳を含む JSON ファイルです。ハーネスはモデルの出力をこれらの参照訳と照合してスコアを算出します。参照訳を変更することはありません。

:::danger 評価データでの学習は禁止です

⚠️ **これらのデータセットは評価専用です。** 評価データを使って学習・ファインチューニング・フューショットプロンプト、またはその他の方法で評価データにさらされたメソッドは、スコアが人為的に高くなり、**リーダーボードから失格となります。**

学習には別のコーパスを使用してください。評価セットは、開発中にモデルが参照しない状態を維持する必要があります。
:::

---

## データセットの形式

すべてのデータセットは同一の JSON スキーマに従います：

```json
{
  "dataset": {
    "id": "dataset-slug",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "description": "Human-readable description of the dataset",
    "source_language": "en",
    "target_language": "crk",
    "created": "2025-05-01",
    "license": "CC-BY-NC-4.0",
    "provenance": ["gold_standard", "textbook"]
  },
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "tânisi",
      "difficulty": 1,
      "provenance": "gold_standard",
      "register": "conversational",
      "context": "greeting",
      "notes": "Common greeting, SRO orthography"
    }
  ]
}
```

:::info 標準スキーマ
[ベンチマーク仕様](/docs/specifications/benchmark)では、標準的なコーパスおよびエントリのスキーマを定義しています。このページでは、利用可能なデータセットと新しいデータセットの作成方法について説明します。
:::

### トップレベルの `dataset` ブロック

| フィールド | 型 | 説明 |
|-------|------|-------------|
| `id` | `string` | データセットの一意な識別子（ランカードおよびリーダーボードで使用） |
| `version` | `string` | セマンティックバージョン。インクリメントすると、以前のランカードとの比較が無効になります |
| `language_pair` | `string` | 表示ラベル（例：`EN→CRK`） |
| `description` | `string` | 任意。人間が読める概要 |
| `source_language` | `string` | BCP 47 ソース言語コード |
| `target_language` | `string` | BCP 47 ターゲット言語コード |
| `created` | `string` | ISO 8601 作成日 |
| `license` | `string` | SPDX ライセンス識別子 |
| `provenance` | `string[]` | エントリ全体で使用される出典タグのリスト |

### エントリフィールド

| フィールド | 型 | 必須 | 説明 |
|-------|------|----------|-------------|
| `id` | `integer` | ✅ | コーパス内でのエントリの一意な識別子 |
| `source` | `string` | ✅ | 翻訳対象のソーステキスト |
| `reference` | `string` | ✅ | ゴールドスタンダードの参照訳 |
| `difficulty` | `integer` | ✅ | 難易度ティア 1〜5（下記参照） |
| `provenance` | `string` | ✅ | エントリの出典（例：`gold_standard`、`textbook`、`elicited`） |
| `register` | `string` | ✅ | レジスター／丁寧さのレベル（例：`conversational`、`formal`、`ceremonial`） |
| `context` | `string` | ✅ | コミュニケーション機能（例：`greeting`、`declaration`、`instruction`） |
| `notes` | `string` | ❌ | 人間のレビュアー向けの任意のコンテキスト |
| `morphological_analysis` | `string` | ❌ | ゴールドスタンダードの形態素解析 |
| `variant_class` | `string` | ❌ | 許容される翻訳バリアントをグループ化するクラスラベル |

---

## 利用可能なデータセット

### EDTeKLA 開発セット v1

英語→Plains Cree（SRO）翻訳のために構築された最初の評価データセットです。アルバータ大学の [EdTeKLA 研究グループ](https://spaces.facsci.ualberta.ca/edtekla/)によって作成されました。

| プロパティ | 値 |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **バージョン** | `1.0` |
| **言語ペア** | EN → CRK（Plains Cree、SRO 正書法） |
| **エントリ数** | 合計548件（テキストブック486件＋ゴールドスタンダード62件）。標準的な開発コーパスは `textbook_dev.json`（436エントリ — テキストブック開発分割の全体：486件中436件の開発用＋50件の保留テスト） |
| **難易度分布** | 易・中・難 |
| **出典** | `gold_standard`（話者による検証済み）、`textbook`（公開された教育教材） |
| **ライセンス** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |

**テスト対象の内容：**

- 基本的な挨拶と一般的なフレーズ
- 名詞の有生性と遠称
- 人称・時制にわたる動詞活用
- 場所格の構文
- 所有格のパラダイム
- 複雑な文構造

:::tip コーパスの構成
EdTeKLA コレクション全体には、厳選された548エントリが含まれています：テキストブックコーパスから486件（開発用436件＋保留50件）、itwêwina ゴールドスタンダードから62件です。標準的な開発コーパスは `textbook_dev.json` で、436エントリ — テキストブック開発分割の全体です。各エントリは、流暢な話者によって検証されているか、公開された Cree 語テキストブックから取得されています。大規模でノイズの多いデータセットよりも、検証済みのゴールドスタンダードを持つ小規模で高品質なデータセットの方が有用です。特に、「ほぼ正確」な翻訳が形態論的に無効となることが多い低リソース言語においては、なおさらです。
:::

---

## 新しいデータセットの作成

新しい言語ペアまたはドメイン向けのデータセットを作成するには：

### 1. JSON を構造化する

[データセットの形式](#データセットの形式)のスキーマに従ってください。すべてのエントリには `source`、`reference`、`difficulty`、`provenance`、`register`、および `context` が必要です。

### 2. 一意な ID を割り当てる

説明的なスラッグを使用してください：`{project}-{split}-v{version}`（例：`edtekla-dev-v1`、`quechua-test-v1`）。

### 3. ゴールドスタンダードを検証する

すべての `reference` の値は、流暢な話者によって検証されているか、公開された査読済みリソースから取得されている必要があります。機械生成の参照訳は評価の目的を損ないます。

### 4. 難易度ティアを設定する

各エントリに整数の難易度レベルを割り当てます：

| ティア | 説明 | 例 |
|------|-------------|----------|
| 1 — 基本語彙 | 単語、一般的な挨拶、数字 | "hello" → "tânisi" |
| 2 — 単純な文 | 主語-動詞または SVO、現在時制 | "I see the dog" |
| 3 — 中程度の複雑さ | 過去・未来時制、所有格、有生性 | "I saw his dog yesterday" |
| 4 — 複雑な形態論 | 遠称、受動態、接続形語順 | "the woman whose son went to the store" |
| 5 — 上級 | 複数節、フォーマルなレジスター、儀礼的表現、慣用句 | レジスターに適したトーンを持つ完全な段落 |

### 5. 出典にタグを付ける

各エントリには、その出典を示す必要があります。一般的なタグ：

- `gold_standard` — 流暢な話者によって検証済み
- `textbook` — 公開された教育教材から取得
- `elicited` — 構造化されたエリシテーションセッションを通じて作成
- `corpus` — 対訳コーパスから抽出

### 6. ファイルを検証する

任意のモデルを使用してデータセットに対してハーネスを実行し、JSON が正しい形式であり、すべての必須フィールドが存在することを確認します：

```bash
python eval/baseline_experiment.py --dataset path/to/your-dataset.json
```

ハーネスは、フィールドの欠落、インデックスの重複、またはスキーマ違反があるとエラーを出力します。

### 7. 収録申請を提出する

データセットファイルを `data/` ディレクトリに配置した状態で、[eval ハーネスリポジトリ](https://github.com/gamedaysuits/arena)に対してプルリクエストを作成してください。検証方法論と出典の文書を含めてください。

---

## FLORES+ Devtest

[Open Language Data Initiative (OLDI)](https://huggingface.co/datasets/openlanguagedata/flores_plus) が管理する、広範囲をカバーする多言語ベンチマークです。champollion のマルチモデルフロンティアベンチマークに使用されます。

| プロパティ | 値 |
|----------|-------|
| **ID** | `flores-plus-devtest` |
| **言語ペア** | EN → 39言語（champollion に登録されたすべての自然言語） |
| **エントリ数** | 言語ごとに1,012文 |
| **ライセンス** | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| **出典** | 元は Meta FLORES-200、現在は OLDI が管理 |
| **場所** | champollion メインリポジトリの `test/benchmark/fixtures/` に事前抽出済みのフィクスチャ |

:::danger 評価専用
FLORES+ は評価のみを目的としています。キュレーターは、**学習データとして使用しないよう**明示的に求めています。学習コーパスからその内容を除外してください。
:::

---

## 関連情報

- [MT 評価](/docs/leaderboard/rules) — 評価フレームワークとリーダーボードの概要
- [Eval ハーネス](/docs/specifications/harness) — これらのデータセットに対して評価を実行する方法
- [ランカード仕様](/docs/specifications/run-card) — 結果を記録するための JSON スキーマ
- [メソッドリーダーボード](https://champollion.dev/leaderboard) — ライブベンチマークスコア
- [EdTeKLA プロジェクト](https://spaces.facsci.ualberta.ca/edtekla/) — Cree データセットを作成したアルバータ大学の研究グループ