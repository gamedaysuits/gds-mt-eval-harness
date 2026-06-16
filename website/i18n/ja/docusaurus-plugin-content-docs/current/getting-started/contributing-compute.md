---
sidebar_position: 4
title: "コンピュートの提供"
description: "トークンを寄付する：自分のAPIキーを使って公開キューからオープンなベンチマークスイープを実行し、結果を公開します。"
related:
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
  - label: "Cookbook: Coached LLM Prompting"
    to: /docs/tutorials/coached-llm-prompting
    kind: cookbook
  - label: "Cookbook: FST-Gated Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "Method Interface & Dependency Classes"
    to: /docs/specifications/methods
    kind: spec
  - label: "Leaderboard Rules & Trust Tiers"
    to: /docs/leaderboard/rules
    kind: guide
---
# コンピュートの提供

> **基本的な考え方：** リーダーボードには空白のマス目があります。これは、誰もまだ計測していない（言語ペア、モデル、条件）の組み合わせです。私たちはそれらの公開キューを管理しています。ご自身のAPIキーを使ってアイテムを実行し、レポートを公開することで、マップが埋まっていきます。「トークンの提供」は、低リソース言語のMT評価に対する実際の、引用可能な貢献です。

## キュー

ライブキューは [champollion.dev/queue.json](https://champollion.dev/queue.json) で公開されており、インストール不要のターミナルビューアーも用意されています：

```bash
curl -fsSL champollion.dev/queue | bash
```

このビューアーはオープンなアイテムとその正確な `mt-eval run` コマンドを*表示する*だけで、何かを実行したりトークンを消費したりすることはありません。各アイテムには以下が含まれます：

- `run_command` — コピー＆ペーストですぐに使えます（コーパスを取得し、ハーネスを実行します）
- `est_cost_usd` および `est_basis` — 同じ（コーパス、モデル）に対して私たちが実施したベースライン実行の**実測**コスト、またはそのモデルのスイープ平均エントリーあたりコスト × コーパスエントリー数からの**外挿値**のいずれかです。根拠はアイテムごとに明記されており、実際のコストは実行時のプロバイダー料金によって異なります。
- `priority` — 未カバーの言語ペアを優先し、最も低リソースのペアを優先（コーパスサイズを代理指標として使用）、naiveの前にcoached、最も安価なモデルを優先します。

**クレームロックなし — オープンなアイテムであれば何でも選べます。** 同じアイテムを2人が実行しても、設計上問題ありません：すべての実行カードはフィンガープリント処理されており（データセットハッシュ + モデル + 条件 + システムプロンプトに対するSHA-256、[ベンチマーク仕様 §3.8](/docs/specifications/benchmark)）、同一の実行は公開時に重複排除され、同じ設定の独立した再現は無駄ではなく有用な証拠となります。

キューに登録されたコーパスはdev分割、CC-BYファミリー（Tatoeba派生）であり、`do_not_train` フラグが付いています。これらは評価セットであり、学習データではありません。非商用ライセンスおよび隔離されたコーパスはオープンキューから除外されています。

## セットアップ（初回のみ）

```bash
# 1. Install the harness (python3 + pipx, no sudo — read it first if you like)
curl -fsSL champollion.dev/harness | bash

# 2. Set your API key
export OPENROUTER_API_KEY="sk-or-..."     # or put it in a local .env file
```

### どのプロバイダーキーを使うか？

ハーネスはすべてのモデル呼び出しを [OpenRouter](https://openrouter.ai/keys) 経由でルーティングします。1つの `OPENROUTER_API_KEY` で、キューのラインナップにあるすべてのモデル（Anthropic Claude、OpenAI GPT、Google Geminiモデルなど）にアクセスできます。また、ハーネスのコスト追跡と料金スナップショットは同じOpenRouterのメタデータから取得されるため、報告される実行コストはキーに請求された金額と一致します。

クレジットがAnthropicやOpenAI、Googleに直接ある場合：ハーネスは現時点でプロバイダーの直接キーには対応していません。実行カードのスキーマには将来のために `api_provider` フィールドが予約されていますが、現在すべてのハーネス実行はOpenRouterの実行です。OpenRouterアカウントを作成してチャージするか（またはOpenRouterがサポートしている場合は自分のプロバイダーアカウントを紐付ける）ことが、サポートされている方法です。

### エージェントの高速パス

Claude Codeや他のコーディングエージェントを使用している場合、貢献全体を1つのプロンプトで完結できます：

```text
Install the Champollion mt-eval harness (curl -fsSL champollion.dev/harness | bash).
Fetch https://champollion.dev/queue.json and show me the top 3 open items.
Using my OpenRouter key (OPENROUTER_API_KEY), execute the run_command of the
item I pick, then run `mt-eval publish` on the generated report JSON and
show me the published run card.
```

## Tier 1 — ベンチマークを実行する

すべてのキューアイテムの `run_command` は自己完結しています。典型的な例：

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/eng-yor-dev-v1.json
mt-eval run --corpus eng-yor-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Yoruba"
```

実行すると合計コストが表示され、実行ログとスコア付きレポートが `eval/logs/` に書き込まれます。その後、公開します：

```bash
mt-eval publish eval/logs/harness/run_..._report.json
```

公開するとOAuth経由でサインインし（あなたの名前がリーダーボードの帰属表示になります）、実行カードがアップサートされます。コミュニティからの投稿は **self-benchmarked** 信頼ティアに分類され、「実行した本人が提出」と明示されます。これは降格ではなく、信頼モデルが機能している証です。実行カードには、誰でもあなたの正確な設定を再実行するために必要なすべての情報（データセットハッシュ、モデル、条件、完全なシステムプロンプト、コスト）が含まれています。上位ティア（verification、community validation）はレビューによって付与されます。詳細は[リーダーボードルール](/docs/leaderboard/rules)をご覧ください。

## Tier 2 — coached プロンプトを作成する

ハーネスは**coaching**をファーストクラスでサポートしています：naiveなシステムプロンプトを、実際の言語知識を含むものに置き換えます。`--coaching-file`（または短いプロンプトの場合は `--coaching "inline text"`）を渡すと、ハーネスはそのテキストをシステムプロンプトとして使用し、**全文とそのSHA-256**を実行ログのprovenanceブロックに記録し、実行の条件を **`coached`** とラベル付けします（`--prompt` を明示的に設定しない限り）。これにより、プロンプトの工夫が再現可能で帰属可能な実験となり、2つの異なるcoachingファイルが混同されることはなく、coached実行がリーダーボード上でnaiveベースラインと誤認されることもありません。

フェロー語を例に、その言語の[公開言語カード](https://champollion.dev/languages)にある類型論的事実と用語集エントリーを使用した実例：

```text title="coaching-fao.txt"
You are translating Danish into Faroese (føroyskt).

Grammar notes:
- Faroese is a North Germanic V2 language: the finite verb is the second
  constituent of a main clause.
- Nouns inflect for case (nominative, accusative, dative, genitive),
  gender (masculine, feminine, neuter), and number. Make adjectives and
  determiners agree.
- The skerping pattern applies before -gv/-ggj sequences; preserve
  standard orthography including ð (which is silent).

Glossary (use these exact equivalents):
- language -> mál
- island -> oyggj
- weather -> veður

Style: plain register, modern standard orthography. Output only the
Faroese translation, no commentary.
```

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/dan-fao-dev-v1.json
mt-eval run --corpus dan-fao-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Faroese" \
  --coaching-file coaching-fao.txt
```

（coaching の内容はご自身で作成してください。上記の事実は*形式*を示しています：影響の大きい文法規則をいくつか、モデルが誤訳しやすい用語の小さな用語集、レジスターの指示。[champollion.dev/languages](https://champollion.dev/languages) の言語カードには、参照できる類型論的情報源が掲載されています。）

`mt-eval compare <naive_log> <coached_log>` を使ってnaiveベースラインと比較し、反復して最良の実行を公開してください。実行は自動的に条件 `coached` で公開されます。汎用ラベルの代わりにリーダーボードに名前付きメソッドを表示したい場合は、公開時にメソッドカードを添付してください（公開フローにウィザードがあります）。プロンプトエンジニアリングだけで低リソース言語ペアのnaiveベースラインを上回ることは、真の、公表可能な知見です。設計ガイダンスについては、[Coached LLM Prompting クックブック](/docs/tutorials/coached-llm-prompting)全文をご覧ください。

## Tier 3 — メソッドを構築する

最も意欲的な貢献：`TranslationMethod` プロトコル（`translate(entries, config)`）を実装し、プロンプトではなく実際のシステムをベンチマークします。ハーネスは `--method <plugin-dir>` 経由でそれを実行し、メソッドカードを実行カードに埋め込みます。実例付きクックブックのあるパターン：

- **[FST-gated パイプライン](/docs/tutorials/fst-gated-pipeline)** — すべての候補単語が形態素解析器によってチェックされ、ゲートを通過するまでLLMが再生成します。半決定論的で、形態論的に保証された出力。
- **[辞書拡張生成](/docs/tutorials/dictionary-augmented-llm)** — 翻訳時にソース用語を対訳辞書で検索し、出力を制約します。
- [連鎖モデル](/docs/tutorials/chained-models)、[few-shot 検索](/docs/tutorials/few-shot-prompting)、[逆翻訳](/docs/tutorials/back-translation)、[ルールベースハイブリッド](/docs/tutorials/rule-based-hybrid)…

メソッドは**依存クラス**（S/O/A1/A2/X — [メソッド仕様](/docs/specifications/methods#method-validity-and-dependency-classes)を参照）を宣言します。これは実行と移転に何が必要かを示します：自己完結したパイプラインはクラスS、実行時にライセンス済み辞書APIを呼び出すものはA2です。正直に宣言してください。クラスによってメソッドが競合できる場所が決まり、マニフェストは監査されます。

## リーダーボードを超えた意義

公開されたすべての実行は、商用プロバイダーが計測していない言語ペアのMT品質に関する独立した証拠です。キューは*需要*の公開記録としても機能します：コミュニティが計測する価値があると考えているペア、現在のAPI価格でのカバレッジコスト、そして提供されたコンピュートがどこまで届くか。資金提供機関に体系的なスイープの支援を求める際、このキューとその充填率が需要の証拠となります。