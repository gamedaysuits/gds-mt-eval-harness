---
sidebar_position: 4
title: "メソッドインターフェース"
related:
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
    note: "Put this interface on the leaderboard"
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
    note: "A full method, built end-to-end"
---
# 共有メソッドインターフェース

> **要約。** このページでは、Arenaのすべてのメソッドが実装しなければならない`TranslationMethod`プロトコル、6つのメソッドクラス（`raw-llm`、`coached-llm`、`pipeline`、`custom-plugin`、`api`、`human`）、メソッドプラグインの形式、そして**依存クラス**（S/O/A1/A2/X）について規定します。依存クラスは、メソッドが評価サンドボックスで実行可能かどうか、および賞の対象となるかどうかを決定します。このプロトコルを実装したあらゆるアプローチをベンチマーク対象にできます。何に依存しているかによって、どのレーンで競えるかが決まります。

evalハーネスとchampollionは、**翻訳メソッド**という共通の概念を持っています。メソッドとは、ソーステキストを受け取り翻訳テキストを生成する任意の手続きを指します。直接的なLLM呼び出し、多段階パイプライン、サードパーティAPI、人間による翻訳など、あらゆる形態が含まれます。

## アーキテクチャ

```
Method Plugin (v2 Spec)
├── method.json           ← Manifest (name, class, entry_point, dependencies, metadata)
├── method_card.json      ← Leaderboard description (what, not how)
├── pipeline.py           ← Python module implementing TranslationMethod
└── (optional helpers)    ← Additional Python modules
```

`--method path/to/dir`経由で読み込まれます。ハーネスは自動的に何も検出しません。

## 2つのシステム、1つのインターフェース

| | Eval Harness | champollion |
|---|---|---|
| **言語** | Python | Node.js |
| **エントリーポイント** | `translate.py` | `translate.js` |
| **インターフェース** | `TranslationMethod`プロトコル | `methodPlugin`設定 |
| **目的** | スコアリングを伴うバッチ評価 | 開発/CIにおけるライブローカライゼーション |
| **出力** | メトリクス付きランカード | 翻訳済みロケールファイル |

両方のシステムをサポートするメソッドは、各言語ランタイム用に1つずつ、合計2つのエントリーポイントを提供します。**メソッドカード**はその橋渡し役であり、両システムが理解できる形式でメソッドを記述します。

## メソッドカード

メソッドカードは、完全なシステムプロンプトなどの独自情報を開示することなく、翻訳メソッドが*何であるか*を記述します。以下の問いに答えます。

- これはどのクラスのメソッドか？（生のLLM、コーチ付きLLM、パイプライン、APIなど）
- どのツールを使用しているか？（FSTアナライザー、辞書など）
- 実装はオープンソースか？
- どの言語ペアをサポートしているか？

完全なJSONスキーマについては、[メソッドカード仕様](/docs/specifications/methods#method-card)を参照してください。

### 例

```json
{
  "method_id": "fst-gated-v8",
  "name": "FST-Gated Coached Translation v8",
  "class": "pipeline",
  "description": "LLM translation with morphological validation. Failed words are retried with FST feedback.",
  "author": "Curtis Forbes",
  "tools_used": ["HFST morphological analyzer", "Wolvengrey dictionary"],
  "open_source": false,
  "dependency_class": "A2",
  "supported_pairs": ["eng>crk"]
}
```

`dependency_class`フィールドは、メソッドの実行と転送に必要なものを要約します。詳細は後述の[メソッドの有効性と依存クラス](#method-validity-and-dependency-classes)を参照してください。

### メソッドクラス

| クラス | 説明 |
|-------|-------------|
| `raw-llm` | 最小限の指示による直接LLM呼び出し |
| `coached-llm` | 構造化プロンプト、例示、制約を伴うLLM |
| `pipeline` | 決定論的コンポーネントを含む多段階パイプライン |
| `custom-plugin` | `TranslationMethod`プロトコルを実装した外部プロセス |
| `api` | サードパーティ翻訳API（Google Translate、DeepLなど） |
| `human` | 人間による翻訳（ベースライン確立用） |

## メソッドの有効性と依存クラス

メソッドの実行可能性と転送可能性は、その依存関係の中で最も利用しにくいものによって決まります。Arenaには、メソッドが何を必要とするかを正確に把握することに依存する2つのメカニズムがあります。

1. **サンドボックス評価**（[ベンチマーク仕様 §8.2](/docs/specifications/benchmark)）— 公式のゴールドスタンダードスコアは、ネットワークポリシーが**デフォルト拒否**のサンドボックスから生成されます。外部サービスを暗黙的に必要とするメソッドは、公式スコアを生成できません。
2. **賞の転送**（[賞仕様](/docs/specifications/prizes)）— 受賞メソッドは言語コミュニティのガバナンス組織に転送されます。提出者が権利を持たないコンテンツを含むメソッドは、合法的に転送できません。提出者は、パッケージ内のすべてのものについて権利を保有している（または付与されている）必要があります。

両方のチェックをアドホックではなく機械的に行うために、すべてのメソッドは`method.json`内の**依存マニフェスト**から導出される**依存クラス**を宣言します。

> **命名に関する注記。** *メソッドクラス*（前節：`raw-llm`、`pipeline`、…）は*メソッドがどのように翻訳するか*を表します。*依存クラス*（本節）は*メソッドの実行と転送に何が必要か*を表します。これらは独立した軸です。`pipeline`メソッドはいずれの依存クラスにもなり得ます。

### 5つの依存クラス

| クラス | 名称 | 定義 | サンドボックス実行可能？ | 賞の対象？ |
|-------|------|-----------|-------------------|-----------------|
| **S** | 自己完結型 | すべてのコード、データ、モデル、重みがメソッドディレクトリ内に含まれており、再配布およびコミュニティ転送を許可するライセンスの下にある。 | ✅ そのまま実行可能 | ✅ 可 |
| **O** | オープン外部依存 | 再配布を許可するオープンライセンス（AGPLなどのコピーレフトライセンスを含む）の下で外部ホストされたアーティファクトに依存する（例：インストール時にダウンロードされるFST）。 | ✅ 可 — アーティファクトはピン留めされ、**提出物にミラーリング**される | ✅ 可（ライセンス互換性条件あり：コピーレフト条項は転送を通じて保持され、コミュニティはライセンスが全員に付与するのと同じ権利を受け取る） |
| **A1** | API依存・代替可能 | ランタイムLLM推論を必要とし、モデルが**代替可能な設定**である場合 — 十分な能力を持つモデルであれば差し替え可能。メソッドの価値はプロンプト、コーチングデータ、コードにあり、特定プロバイダーのモデルには依存しない。 | ⚠️ サンドボックス仕様が定義する**LLMゲートウェイ**経由のみ（🔲 計画中 — 後述） | ⚠️ 条件付き — 後述 |
| **A2** | API依存・代替不可 | ミラーリングや代替が不可能な外部データまたはサービスAPIへのランタイム呼び出しを必要とする — 通常、提供されるコンテンツが独自仕様または無ライセンスであるため（例：基盤となる辞書に公開ライセンスがない辞書API）。 | ❌ 不可 — 権利者の許可なしにサンドボックス内に依存関係を置くことはできない | ❌ 権利者がサンドボックスへの組み込み**および**転送許可を付与するまで不可。オープン（開発セグメント）リーダーボードでは**「外部依存」**フラグ付きで掲載可能 |
| **X** | クローズド | 提出者が再配布する権利を持たないコンテンツを含む — 無ライセンスのデータセット、スクレイピングされた独自コンテンツ、ライセンス非互換のコンポーネント。 | ❌ | ❌ すべてのレーンで不受理。権利なしにコンテンツをバンドルすることは、メソッドの実行場所に関わらずライセンス違反となる |

**実効クラス。** メソッドの依存クラスは、宣言されたすべての依存関係の中で S < O < A1 < A2 < X の順で*最も制限の厳しい*クラスとなります。無ライセンスの辞書が1つあるだけで、それ以外は自己完結型のパイプラインがクラスA2（ランタイムアクセスの場合）またはクラスX（権利なしでバンドルされた場合）になります。

### A1/A2の区別：代替可能性

ほとんどのメソッドはLLMを呼び出します。Arenaはそれを否定しませんが、2種類のAPI依存を明確に区別します。

- **A1（代替可能）：** APIはコモディティなLLM推論を提供します。モデル識別子は設定であり、メソッドはコミュニティがホストするオープンウェイトモデルを含む任意の互換推論エンドポイントに対してエンドツーエンドで動作しなければなりません。モデルによって出力品質は異なる場合がありますが、それは開発者のリスクであり、公式スコアは評価で使用されたピン留めモデルに紐付けられます。**プロバイダー側の状態**（プロバイダーのみでホストされるファインチューン、プロバイダーのファイルストア、プロバイダー固有のアシスタント）に依存するメソッドは代替可能ではありません。その状態は差し替えられないため、基盤となる重みやデータが提出物に含まれていない限り、依存関係はA2となります。
- **A2（代替不可）：** APIは固有のもの — 通常は独自仕様または無ライセンスのデータ — を提供します。代替エンドポイントはそれを提供できず、権利者の許可なしにコンテンツをサンドボックスにミラーリングすることもできません。メソッドはオープンリーダーボードでは（フラグ付きで）動作しますが、許可が得られるまで公式サンドボックススコアの生成や賞の対象にはなれません。

**A1賞転送で実際に何が移転するか。** コミュニティはモデルを受け取りません — AnthropicやGoogle、OpenAIの重みを誰も転送することはできません。転送の対象はモデルを*取り巻く*完全なレシピです。すべてのプロンプト、コーチングデータ、パイプラインコード、リトライロジック、設定、および文書化されたモデル要件が含まれます。モデルは設計上代替可能であるため、コミュニティは開発者の関与なしに、転送されたメソッドを任意のプロバイダー、または自前のハードウェア上のオープンウェイトモデルに向けることができます。レシピは所有され、エンジンは賃借されており、交換可能です。

### 依存マニフェスト（`method.json`）

すべてのメソッドは`method.json`マニフェストで依存関係を宣言します。各エントリーには、アーティファクトの内容、出所、適用ライセンス、およびメソッドがどのようにアクセスするかが記録されます。

```json
{
  "name": "FST-Gated Coached Translation v8",
  "method_id": "fst-gated-v8",
  "class": "pipeline",
  "entry_point": "pipeline:PipelineMethod",
  "supported_pairs": ["eng>crk"],
  "dependency_class": "A2",
  "dependencies": [
    {
      "id": "giellalt-lang-crk-fst",
      "kind": "software",
      "license": "AGPL-3.0-or-later",
      "access": "mirrored",
      "source": "https://github.com/giellalt/lang-crk",
      "pin": "sha256:3f1a…",
      "redistributable": true,
      "transferable": true
    },
    {
      "id": "llm-inference",
      "kind": "model",
      "license": "proprietary",
      "access": "gateway",
      "source": "openrouter:google/gemini-2.5-flash",
      "substitutable": true,
      "redistributable": false,
      "transferable": false,
      "notes": "Any compatible chat-completions endpoint works; the model slug is configuration."
    },
    {
      "id": "crk-dictionary-api",
      "kind": "service",
      "license": "none",
      "access": "external-api",
      "source": "https://itwewina.altlab.app/",
      "redistributable": false,
      "transferable": false,
      "notes": "Dictionary content has no public license; runtime lookups only. Class A2 until the rights holders grant permission."
    }
  ]
}
```

| フィールド | 必須 | 説明 |
|-------|----------|-------------|
| `id` | ✅ | 依存関係の安定した識別子 |
| `kind` | ✅ | `data`、`model`、`software`、または`service` |
| `license` | ✅ | SPDX識別子、`proprietary`、または`none`。`none`は公開ライセンスが存在しないことを意味し、全権留保として扱われる |
| `access` | ✅ | `bundled`（メソッドディレクトリに同梱）、`mirrored`（インストール時に取得、ピン留めされ提出物にベンダリング）、`gateway`（評価ゲートウェイ経由のランタイムLLM推論）、`external-api`（その他のランタイムネットワーク呼び出し） |
| `source` | ✅ | 正規URLまたは`provider:slug`識別子 |
| `pin` | `mirrored`の場合 | 正確なアーティファクトをピン留めするバージョン、コミット、またはコンテンツハッシュ |
| `substitutable` | `gateway`/`external-api`の場合 | この依存関係を提供できる互換エンドポイントが存在するかどうか |
| `redistributable` | ✅ | ライセンスがアーティファクトの再配布を許可しているかどうか |
| `transferable` | ✅ | アーティファクト（またはその権利）が賞転送条件の下でコミュニティに移転できるかどうか |
| `notes` | ❌ | 自由記述のコンテキスト |

**クラスの導出。** 各依存関係がクラスに寄与し、メソッドの`dependency_class`は最も制限の厳しいものとなります。

| 依存プロファイル | 寄与クラス |
|--------------------|-------------|
| `bundled` + ライセンスが再配布と転送を許可 | S |
| `mirrored` + 再配布を許可するオープンライセンス（コピーレフト含む） | O |
| `gateway` + `substitutable: true`（LLM推論） | A1 |
| `external-api`、または`gateway`かつ`substitutable: false` | A2 |
| `bundled` + `license: none`または再配布非互換ライセンス | X |

宣言された`dependency_class`は、ハーネスがマニフェストから導出するクラスと一致しなければなりません。不一致はバリデーションエラーとなります。

外部依存関係が**ない**メソッドは`"dependency_class": "S"`と`"dependencies": []`を宣言します。空の配列は肯定的な宣言であり、他と同様に監査されます。

### 有効性の検証方法

コストの低い順から最も権威ある順に、3つの層があります。

1. **マニフェスト監査。** ハーネスはマニフェストから実効クラスを導出し、不一致を拒否します。レビュアーは宣言された各依存関係をその記載ライセンスおよびソースと照合します — `redistributable: true`と宣言されているが上流ライセンスがそれを否定している依存関係はレビューで不合格となります。
2. **静的解析。** 提出されたコードは、マニフェストに記載されていないネットワーク呼び出し、動的ダウンロード、ファイルシステムアクセスについてスキャンされます。レビューで発見された*未宣言の*依存関係は、それがどのクラスに該当するかに関わらず拒否の根拠となります — マニフェストは正確であるだけでなく、完全でなければなりません。
3. **サンドボックスネットワークポリシー。** サンドボックス仕様は**デフォルト拒否のエグレス**を要求します。メソッドコンテナは、パスが明示的に許可リストに登録されていない限りネットワークアクセスを持ちません。仕様が定義する唯一のエグレスパスは**LLMゲートウェイ**です — 評価インフラが運用する推論プロキシで、ピン留めされたモデルの明示的な許可リストに制限され、すべてのリクエストとレスポンスが実行後の監査のためにログに記録されます。許可リストにないものはポリシー層ではなくネットワーク層で失敗します。ネットワークポリシーとゲートウェイ設計については[ベンチマーク仕様 §8.6](/docs/specifications/benchmark)を参照してください。

> 🔲 **計画中。** サンドボックスとそのLLMゲートウェイは仕様として定義されていますが、まだ構築されていません。ゲートウェイが稼働するまで、サンドボックスで評価できるのはクラスSおよびクラスOのメソッドのみです。クラスA1のメソッドは*原則として*賞の対象ですが、現時点では公式のゴールドスタンダードスコアを生成できません。このページは現在動作しているものではなく、仕様が要求するものを説明しています。

### リーダーボードの表示

- リーダーボードには、各メソッドの依存クラスがメソッドクラスバッジとともに表示されます。
- オープンリーダーボード上のクラスA2メソッドには、**「外部依存」**フラグが表示されます。これらのスコアは変更または消滅する可能性のあるサードパーティサービスに依存しており、現時点では賞の対象ではありません。
- クラスXのメソッドは掲載されません。

## Eval Harness：TranslationMethodプロトコル

evalハーネスはプラグインにPythonの構造的型付け（`Protocol`）を使用します。正しいメソッドシグネチャを持つクラスであれば動作します — 継承は不要です。

```python
class MyMethod:
    async def translate(self, entries: list[dict], config: RunConfig) -> list[dict]:
        results = []
        for entry in entries:
            translation = await self.do_translation(entry["source"])
            results.append({
                "id": entry["id"],
                "predicted": translation,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                "error": None,
                "tool_calls": [],
                "tool_call_count": 0,
                "metadata": {},
            })
        return results
```

非Pythonメソッドのラッパー例を含む完全なドキュメントについては、[プラグインプロトコル](/docs/specifications/methods#eval-harness-translationmethod-protocol)を参照してください。

## champollion：methodPlugin設定

champollionでは、メソッドは`champollion.config.json`で言語ペアごとに登録されます。

```json
{
  "version": 3,
  "pairs": {
    "en:crk": {
      "methodPlugin": "crk-coached-v1"
    }
  }
}
```

champollion側のインターフェースについては、[プラグイン仕様](https://champollion.dev/docs/reference/plugin-spec)を参照してください。

## リーダーボード統合

メソッドカードがランに添付されると（`--method-card`経由）、ランカードに埋め込まれ、リーダーボードに表示されます。

```bash
# Run with method card attached
mt-eval run \
  --method path/to/my-method \
  --corpus data/edtekla-dev-v1.json \
  --method-card method_card.json

# Publish to the leaderboard
mt-eval publish eval/logs/harness/your-run-card.json
```

`--method-card`が提供されていない場合、`mt-eval publish`はメソッドの説明を案内するインタラクティブウィザードを起動します。

リーダーボードに表示される情報：
- **クラスバッジ** — 視覚的インジケーター（例：「pipeline」、「coached-llm」）
- **依存クラス** — S/O/A1/A2（[メソッドの有効性と依存クラス](#method-validity-and-dependency-classes)を参照）。A2メソッドには「外部依存」フラグが付く
- **メソッド名** — メソッドカードより
- **使用ツール** — メソッドカードより一覧表示
- **オープンソースインジケーター**

メソッドカードが添付されていない場合、リーダーボードにはハーネスネイティブの設定（モデル、プロンプトバージョン、温度、有効ツール）が表示されます。

:::danger 評価データでのトレーニング禁止
開発プロセスにおいて評価データセットへの露出があったメソッド — トレーニングデータ、few-shotの例示、辞書エントリー、プロンプトチューニング素材としての使用を含む — はリーダーボードから**失格**となります。良いメソッドと悪いメソッドを区別するものについては、[MT評価](/docs/leaderboard/rules)を参照してください。
:::

---

## 関連情報

- [MT評価](/docs/leaderboard/rules) — 概要、リーダーボードの価値、良いメソッド・悪いメソッドのガイダンス
- [Eval Harness](/docs/specifications/harness) — 評価の実行方法
- [評価データセット](/docs/leaderboard/datasets) — 利用可能なデータセット（EDTeKLA、FLORES+）
- [ランカード仕様](/docs/specifications/run-card) — ランカードのJSONスキーマ
- [プラグイン仕様](https://champollion.dev/docs/reference/plugin-spec) — champollion側のプラグインインターフェース
- [メソッドリーダーボード](https://champollion.dev/leaderboard) — ライブベンチマークスコア
- [ベンチマーク仕様](/docs/specifications/benchmark) — 評価プロトコル、コーパス形式、ランカードスキーマ
- [スコアリング仕様](/docs/specifications/scoring) — メトリクス、複合ウェイト、品質ティアのSSOT