---
sidebar_position: 5
title: "スコアリング仕様"
slug: '/specifications/scoring'
related:
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
    note: "When a score difference actually means something"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
    note: "The tool that computes these metrics"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "These scores, live"
---
# スコアリング仕様

> **エグゼクティブサマリー。** 本文書は、Champollion MT評価エコシステムにおけるすべての評価指標、複合スコアリング、品質ティア、およびコスト分析に関する唯一の信頼できる情報源です。言語固有の評価指標（FST形態論的妥当性、リンター等価クラス、決定論的意味検証）は、総称して**LYSS**（Linguistically-informed Yield & Structural Scoring）と呼ばれます。ハーネスが算出するすべての指標、複合式のすべての重み、およびすべてのティア閾値は、本文書においてのみ定義されます。コード、ドキュメント、およびデータベーススキーマは本文書から派生します。それらが矛盾する場合、本文書が権威を持ちます。
>
> **スコープ。** 本文書は、*何を*測定し、*どのようにスコアリングするか*を定義します。ランカードスキーマ（BENCHMARK_SPEC §3参照）、ベンチマークプロトコル（BENCHMARK_SPEC §6）、またはリーダーボードルール（アリーナドキュメント参照）は定義しません。それらの文書は、指標定義とスコアリングロジックについて本文書を参照します。
>
> 最終更新：2026-06-07

---

## 1. スコアリングの哲学

### 1.1 マイクロ評価の哲学

> *「汎化するものだけに注目すれば、汎化しない部分を必ず見落とし、それらの言語とそのすべての知識・知恵を失うことになる。」*

本プロジェクトは**マイクロ評価開発**を実践しています。これは、有限状態トランスデューサー、バイリンガル辞書、形態素解析器、言語学者が精選した等価ルールなど、利用可能な最良の言語ツールを用いて、特定の言語に合わせた評価指標を構築するアプローチです。これは、すべての言語にわたって機能する普遍的な指標を追求するMT評価の主流パラダイムとは対照的です。普遍的な指標は有用ですが、最も必要とされる場面でこそ最も弱くなります。すなわち、複雑な形態論を持ち、学習データが限られており、ニューラル指標の学習セットに表現されていない言語においてです。

世界の多くの言語において機械翻訳が進歩していない理由は、コーパスが不足しているからだけではありません。**進歩がどのようなものかさえわからない**のです。翻訳システムが改善しているかどうかを測定する自動評価ツールが不足しています。LYSSは、存在する言語リソースを活用しながら、言語ごとにそれらのツールを構築しようとする試みです。

### 1.2 自動指標はプロキシである

ここで定義されるすべての指標は機械的に算出されます。これらは、迅速なイテレーション、体系的な比較、および回帰の検出に有用です。しかし、**人間の判断の代替にはなりません**。§5の品質ティアはヒューリスティックなラベルであり、実際の使用可能性を確認できるのは人間によるレビューのみです。

### 1.3 マルチシグナル設計

単一の指標で翻訳品質を捉えることはできません。chrF++の重複が完璧でも形態論的検証に失敗することがあります。FST検査を通過しても意味が誤っていることがあります。意味的に正確でも、対象言語にとって文体的に不自然なことがあります。§4の複合スコアは、品質の異なる次元をそれぞれ捉える複数の独立したシグナルを集約します。

### 1.4 拡張性

この指標インベントリは閉じていません。新しい言語は新たな要件をもたらします。声調言語のトーン精度、セム語系文字の発音区別符号の精度、クリー語の音節文字の正確さなどです。アーキテクチャ（MetricPluginプロトコル、再正規化を伴う重み付き複合）は、既存のスコアを壊すことなく指標を追加できるよう設計されています。言語固有の指標（例：CRKのリンターと意味検証器）は、`evalMetrics`の言語カードで宣言され、`eval_standards/`から読み込まれます。ハーネスには汎用的な動作指標（コードスイッチング、幻覚、用語）のみが同梱されています。

### 1.5 評価の3つの次元

すべてのランカードは3つの独立した次元を測定します：

```
Quality   — How good is the translation?   (composite score, §4)
Cost      — How much does it cost?          (cost metrics, §6)
Speed     — How fast does it run?           (speed metrics, §7)
```

これらは独立した軸です。高品質でも高コストな手法、高速でも不正確な手法、またはその他の組み合わせが存在します。リーダーボードでは任意の次元でソートできます。コスト調整スコア（§6.3）は、次元を組み合わせる唯一の指標です。

### 1.6 検証ステータス

本仕様のすべての指標には、実装ステータス（§3）とは別の**検証ステータス**があります。実装ステータスはコードが存在するかどうかを追跡します。検証ステータスは、指標が人間の品質判断と相関することが示されているかどうかを追跡します。

| 検証レベル | 意味 | 現在の指標 |
|------------------|---------|----------------|
| **✅ 外部検証済み** | 人間との相関研究が公開されている（WMT、学術論文） | `chrf_plus_plus`、`bleu`、`comet_score` |
| **⚡ プロキシ検証済み** | 高リソース言語では検証済み；対象LRLでは未検証 | `comet_score`（EUペアでは検証済み、CRKでは未検証） |
| **🔶 エンジニアリングヒューリスティック** | 言語的原則または観察された失敗モードから設計；人間との相関データなし | `fst_acceptance_rate`、`equivalent_match_rate`、`semantic_score`、`code_switching_rate`、`hallucination_rate`、`terminology_adherence` |
| **🔲 未検証** | いかなるデータでもまだテストされていない | `morphological_accuracy`、`orthographic_accuracy`、`consistency_score` |

> **実際の意味。** 複合スコア（§4）はすべての検証レベルの指標を集約します。これは明示的な設計上の選択です。構造的に根拠のあるエンジニアリングヒューリスティック（FST受理）は、ヨーロッパ言語ペアのみで検証されたニューラル指標（COMET）よりも、多合成語的言語にとって有益であると考えています。ただし、これは証明されていません。複合スコアは、各対象言語について人間との相関研究が完了するまで、検証された品質測定ではなく**エンジニアリング上の推定値**として扱うべきです。
>
> **必要な検証実験**（`mt-evaluation-landscape.md` §6および`speaker-validation.md`参照）：
> 1. 人間の判断との相関研究：3名以上のバイリンガル話者が評価した200文以上の文ペア
> 2. 代表的なコーパスにおけるFSTの誤棄却率の測定
> 3. 汎化性をテストするための第2言語ポート（北サーミ語）
> 4. 同一データでのCOMETとの直接比較


---

## 2. 指標インベントリ

指標は4つのカテゴリに整理されています。各指標には実装ステータス、スケール、およびレベル（エントリ単位、コーパス単位、またはその両方）があります。

### 2.1 表層指標

表層指標は、予測された翻訳を文字列レベルで参照翻訳と比較します。言語ツールは不要で、文字列比較のみを使用します。

| ID | 指標 | ステータス | スケール | レベル | 実装 |
|----|--------|--------|-------|-------|---------------|
| `exact_match_rate` | 完全一致 | ✅ 実装済み | 0.0–1.0 | 両方 | バイナリ：予測値 == 参照値か？コーパス率 = 一致数 / 総数。 |
| `equivalent_match_rate` | 等価一致 | ⚡ 部分的 | 0.0–1.0 | 両方 | 予測出力は受理された変形のいずれかと一致するか？CRKの場合：`eval_standards/crk/`内の`CrkLinterMetric`を通じてCRK評価標準の決定論的変形クラスルール（語順、正書法、任意助詞、補題同義語、進行形曖昧性）で実装済み。CRK言語カードの`evalMetrics`宣言を通じて自動的に読み込まれます。汎用的な言語横断実装には、コーパス内のエントリごとの`variants[]`が必要です。 |
| `chrf_plus_plus` | chrF++ | ✅ 実装済み | 0–100 | 両方 | 文字n-gram Fスコア（sacrebleu）。形態論的変形に対してロバスト。膠着語的・多合成語的言語の主要な表層指標。エントリ単位では`sentence_chrf`を使用；コーパスでは`corpus_chrf`を使用。 |
| `bleu` | BLEU | ✅ 実装済み | 0–100 | コーパス | 単語レベルのn-gram精度（sacrebleu）。**複合から除外** — 単語レベルのスコアリングは形態論的変形を不当にペナルティ化します。MT文献との互換性のために算出・報告されます。 |
| `ter` | Translation Edit Rate | ✅ 実装済み | 0–∞（低いほど良い） | 両方 | 予測値と参照値の間の最小編集距離を参照長で正規化（sacrebleu `corpus_ter`）。chrF++およびBLEUと並行して算出されます。複合から除外 — ほとんどのユースケースでchrF++と相関するため、両方を含めると表層類似性を二重にカウントすることになります。 |
| `length_ratio` | 長さ比率 | ✅ 実装済み | 0–∞（1.0が理想） | 両方 | 文字数での`len(predicted) / len(reference)`。切り捨て（<0.5）と膨張・幻覚（>2.0）を検出します。コーパスレベルではエントリ全体で平均化されます。 |

### 2.2 構造指標

構造指標は翻訳の言語的整形性を検証します。言語固有のツール（FST解析器、形態素解析器）が必要であり、形態論的に豊かな言語にとって最も強力なシグナルです。

| ID | 指標 | ステータス | スケール | レベル | 実装 |
|----|--------|--------|-------|-------|---------------|
| `fst_acceptance_rate` | FST受理 | ✅ 実装済み | 0.0–1.0 | 両方 | 有限状態トランスデューサー（GiellaLT）によって受理された出力単語の割合。FSTが少なくとも1つの形態論的分析を返す場合、その単語は「有効」です。GiellaLTの`.hfstol`解析器を持つ任意の言語で利用可能です。 |
| `morphological_accuracy` | 形態論的精度 | 🔲 計画中 | 0.0–1.0 | 両方 | 単語はFST有効でも誤った活用形を持つ場合があります（正しい語根、誤った接尾辞）。この指標は、予測単語のFST分析を期待される形態論的特徴と比較します。コーパスエントリごとの形態論的アノテーションが必要です。 |
| `orthographic_accuracy` | 正書法的精度 | 🔲 計画中 | 0.0–1.0 | 両方 | スクリプト固有の正確さを検証します：クリー語のSROマクロン・サーカムフレックス使用、イヌクティトゥット語の発音区別符号、オジブウェー語の母音長マーカー。言語ごとのルールセット。 |

> **構造指標が重要な理由。** MetaのOMT-1600（これまでに公開された最大のMTシステム、1,600言語）は、ChrF++、xCOMET、MetricX、およびBLASER 3で評価しています。これらのいずれも形態論的正確さを検証しません。ChrF++は文字n-gramの重複を測定します。つまり、対象言語に*見える*文字列を報酬として与えます。多合成語的言語では、参照と多くの文字を共有する形態論的に無効な単語が高いスコアを得ることになります。FST受理指標はバイナリの構造テストです。その単語は言語内の有効な形式であるか、そうでないかのどちらかです。他のMT評価フレームワークはこれを大規模に提供していません。

### 2.3 意味指標

意味指標は、埋め込みまたは学習済みモデルを使用して意味の保存を測定します。表層的には異なるが意味的に等価な翻訳を捉え、表層的には類似しているが意味的に誤った翻訳にフラグを立てます。

| ID | 指標 | ステータス | スケール | レベル | 実装 |
|----|--------|--------|-------|-------|---------------|
| `semantic_score` | 意味的類似性 | ⚡ 部分的 | 0.0–1.0 | 両方 | CRK：`eval_standards/crk/`内のCRK評価標準の`CrkSemanticMetric`からの判定重み付きスコア（プロキシ）。汎用：文埋め込みのコサイン類似度（ソース＋予測値 vs ソース＋参照値）。モデルは未定 — 低リソース言語をサポートする必要があり、ほとんどの英語中心の埋め込みモデルは除外されます。 |
| `comet_score` | COMET | ✅ 実装済み | ~0.0–1.0 | 両方 | 学習済みMT評価指標（Unbabel）。人間の品質判断で学習済み。**複合から除外** — 学習データは高リソースのヨーロッパ言語に偏っており、LRLのスコアは信頼性が低い。`unbabel-comet`がインストールされている場合に算出されます。低リソース警告フラグ付きで報告されます。35のアフリカ言語については、ハーネスは`resolve_comet_model()`を通じてAfriCOMET（`masakhane/africomet-mtl`）を自動選択します。これらの言語では人間の判断との相関がより良好です。 |

> **COMETが複合から除外される理由。** COMETはWMTの人間評価データで学習されており、そのデータは圧倒的に高リソースのヨーロッパ言語ペアです。プレーンズ・クリー語やその他のLRLに適用した場合、モデルの内部表現はそれらの言語への露出がなく、根本的に異なる形態論的システムを持つ言語から外挿しています。スコアは方向性として有用（COMETが高い ≈ 一般的により流暢に聞こえる出力）ですが、絶対値は較正されていません。透明性のためにCOMETを報告しますが、各対象言語について人間の判断に対して検証できるまで、複合スコアに影響させません。

> **アフリカ言語のAfriCOMET。** 各言語カードには`metricModelSupport`フィールド（言語カード仕様§9参照）があり、その言語向けに学習された専門的なCOMETモデルを宣言します。35のアフリカ言語（yor、hau、ibo、amh、swa等）については、カードはAfriCOMET（`masakhane/africomet-mtl`）を宣言します。これはMasakhaneコミュニティによってアフリカ言語MTの人間の判断でファインチューニングされたCOMETモデルです。ハーネスは言語カードから読み込む`resolve_comet_model()`を通じて推奨モデルを自動選択しますが、`--comet-model`でオーバーライドできます。新しい言語→モデルのマッピングの追加は、言語カードを充実させることで行います（Pythonコードの編集ではありません）。

### 2.4 動作指標

動作指標は翻訳出力における特定の失敗モードを検出します。品質を直接測定するのではなく、問題を検出します。

| ID | 指標 | ステータス | スケール | レベル | 実装 |
|----|--------|--------|-------|-------|---------------|
| `code_switching_rate` | コードスイッチング率 | ✅ 実装済み | 0.0–1.0（低いほど良い） | 両方 | ソース言語（通常は英語）にある出力単語の割合。Unicodeスクリプト分析および/またはソース言語単語リストで検出されます。非常に一般的なLLMの失敗モード：モデルが対象言語の等価語を知らない場合に英語の単語を挿入します。 |
| `hallucination_rate` | 幻覚率 | ✅ 実装済み | 0.0–1.0（低いほど良い） | 両方 | 対応するソースコンテンツを持たない出力コンテンツの割合。単語アライメントまたは言語横断埋め込みの重複で検出されます。もっともらしく聞こえるが捏造された翻訳を生成するモデルを捉えます。 |
| `terminology_adherence` | 用語遵守 | ✅ 実装済み | 0.0–1.0 | 両方 | コーチング手法の場合：出力に現れる規定用語の割合。コーチング辞書データが必要です。モデルが専門家が提供した語彙を尊重するかどうかを測定します。 |
| `consistency_score` | エントリ間一貫性 | 🔲 計画中 | 0.0–1.0 | コーパスのみ | モデルは同じソース用語をエントリ全体で同じように翻訳するか？一貫性が低い場合、モデルは学習したパターンを適用するのではなく推測していることを示唆します。コーパスエントリ全体で繰り返される用語が必要です。 |

### 2.5 コンプライアンス指標

コンプライアンス指標は、翻訳がプレースホルダー、フォーマット、および表記規則などの構造的整合性を保持しているかを検証します。これらは品質スコアではなく、品質ゲートチェックです。

| ID | 指標 | ステータス | スケール | レベル | 実装 |
|----|--------|--------|-------|-------|---------------|
| `compliance_index` | ダブルパスコンプライアンス | ✅ 実装済み | 0.0–1.0 | 両方 | 重み付き複合：60%変数整合性（`{placeholder}`変数は保持されているか？）+ 20%引用符コンプライアンス（言語カードごとの正しい引用符文字）+ 20%大文字小文字コンプライアンス（大文字小文字のない言語でのラテン文字漏れなし）。生の出力と後処理済み出力の両方で算出されます。`DoublePassCompliancePlugin`を通じて。 |
| `repair_effectiveness` | 修復有効性 | ✅ 実装済み | 0.0–1.0 | コーパス | 翻訳後フックによって自動修復されたコンプライアンス違反の割合。品質ゲートが生の出力をどれだけ改善したかを測定します。 |

> **コンプライアンスが複合に含まれない理由。** コンプライアンス指標は構造的保存（プレースホルダー、引用符）を測定するものであり、翻訳品質ではありません。翻訳が言語的に完璧でも、`{name}`変数を削除したためにコンプライアンスに失敗することがあります。これらは品質ゲートです。不良な出力の出荷をブロックしますが、翻訳品質をランク付けするものではありません。

---

## 3. 指標ステータスティア

§2のすべての指標は、4つの実装ティアのいずれかに分類されます：

| ティア | 意味 | ランカードの動作 |
|------|---------|-------------------|
| **✅ 実装済み** | コードが存在し、テスト済みで、現在ランカードで値を生成している | ランカードに数値 |
| **⚡ 部分的** | 言語固有のプロキシが存在する（例：CRK）が、汎用実装は保留中 | プロキシが適用される場合は数値、それ以外は`null` |
| **🔲 計画中** | 仕様化されているが未実装 | ランカードに`null`（フィールドは存在するが値なし） |
| **💡 提案中** | 議論中で、まだ仕様化されていない | ランカードに含まれない |

指標が計画中 → 部分的に移行するのは：
1. 言語固有の実装がマージされテスト済みになった場合
2. 少なくとも1つの言語ペアで値を生成する場合
3. 汎用実装が保留中のまま（本仕様に文書化）の場合

指標が部分的 → 実装済みに移行するのは：
1. 言語非依存の実装がマージされテスト済みになった場合
2. 言語固有のプラグインなしで任意の言語ペアで値を生成する場合
3. 本文書が✅ステータスを反映するよう更新された場合

指標が計画中 → 実装済みに移行するのは：
1. 実装がマージされテスト済みになった場合
2. 少なくとも1つの実際の評価ランで検証された場合
3. 本文書が実装の詳細とともに更新された場合

指標が提案中 → 計画中に移行するのは：
1. その定義、スケール、および算出方法が合意された場合
2. `🔲 Planned`ステータスで本文書に追加された場合
3. ランカードスキーマにnullプレースホルダーが追加された場合

---

## 4. 複合スコア

### 4.1 式

複合スコアは、利用可能なすべての指標の重み付き平均であり、利用可能な指標の重みの合計が1.0になるよう再正規化されます：

```
composite = Σ (weight_i × value_i)    for all available metrics
             ─────────────────────
             Σ weight_i               (re-normalization denominator)
```

指標は、ランカード内の値が数値（`null`でない）の場合に「利用可能」です。言語にFSTがない場合や指標がまだ実装されていない場合など、指標が利用できない場合、その重みは残りの指標に比例して再配分されます。

**これはランド内で複合スコアが常に比較可能であることを意味します：** 利用可能な指標を使用し、それに応じて正規化します。ランをまたいだ比較は、同じ利用可能な指標セットを使用するランで有効です。

> [!WARNING]
> **ランをまたいだ比較可能性。** 異なる指標の利用可能性を持つランを比較する場合（例：一方のランにFSTスコアがあり、もう一方にない場合）、複合スコアは**直接比較できません**。5つの指標から算出された0.72の複合スコアは、2つの指標から算出された0.72の複合スコアよりも多くの情報を持ちます。リーダーボードは、比較されるランの間で指標カバレッジが異なる場合に警告を表示します。厳密な比較には、共有指標のみでペアードブートストラップ有意性検定（§8.2）を使用してください。

### 4.2 入力の正規化

複合式に入力する前に、すべての指標は1.0 = 完璧な**0.0–1.0スケール**でなければなりません：

| 指標 | ネイティブスケール | 正規化 |
|--------|-------------|---------------|
| `exact_match_rate` | 0.0–1.0 | なし（すでに正規化済み） |
| `equivalent_match_rate` | 0.0–1.0 | なし |
| `fst_acceptance_rate` | 0.0–1.0 | なし |
| `morphological_accuracy` | 0.0–1.0 | なし |
| `chrf_plus_plus` | 0–100 | **100で除算** |
| `semantic_score` | 0.0–1.0 | なし |
| `code_switching_rate` | 0.0–1.0（低いほど良い） | **`1.0 - value`**（反転：コードスイッチング0% = 1.0） |
| `hallucination_rate` | 0.0–1.0（低いほど良い） | **`1.0 - value`**（反転） |
| `terminology_adherence` | 0.0–1.0 | なし |

複合から除外された指標（`bleu`、`comet_score`、`ter`、`length_ratio`、`consistency_score`）はこの目的のために正規化されません。

### 4.3 重みテーブル

#### プロファイルA：FSTカバレッジがある言語

GiellaLT有限状態トランスデューサーが利用可能な言語向け。構造指標は複合の40%を占めます（FST 0.25 + 形態論的精度 0.15）。これは多合成語的・膠着語的言語における形態論的正確さの優位性を反映しています。

| 指標 | 目標重み | 根拠 |
|--------|--------------|-----------|
| `fst_acceptance_rate` | **0.25** | 最高重み。FSTが単語を棄却した場合、他の指標が何を言おうとも、それは言語内の有効な形式ではありません。バイナリで構造的に根拠があります。 |
| `morphological_accuracy` | **0.15** | 単語はFST有効でも形態論的に誤っている場合があります（正しい語根、誤った活用形）。FSTと合わせて、構造指標は40%を占めます。 |
| `chrf_plus_plus` | **0.15** | 文字n-gramの重複：多合成語的言語の最良の表層レベルプロキシ。膠着語的形態論を単語レベルの指標よりもうまく処理します。 |
| `semantic_score` | **0.15** | 表層形式が異なる場合の意味保存。構造チェックを通過した意味的に誤った翻訳を捉えます。 |
| `equivalent_match_rate` | **0.10** | 1つの参照翻訳だけでなく、受理可能な変形を報酬として与えます。語順が柔軟な言語にとって重要です。 |
| `code_switching_rate` | **0.05** | ソース言語の漏れにペナルティを与えます。反転：コードスイッチング0% = 1.0。 |
| `terminology_adherence` | **0.05** | 規定された語彙を尊重するコーチング手法を報酬として与えます。コーチングデータが存在する場合のみ有効。 |
| `hallucination_rate` | **0.05** | 捏造されたコンテンツにペナルティを与えます。反転：幻覚0% = 1.0。 |
| `exact_match_rate` | **0.05** | 最低重み。多合成語的言語には厳しすぎます — 複数の正しい翻訳が存在します。上限チェックとして保持されます。 |

> **合計：1.00。** 指標が利用できない場合、その重みは利用可能な指標に比例して再配分されます。現在、`morphological_accuracy`（重み0.15）はプロファイルAでまだ算出されていない唯一の指標です — エントリごとのゴールドスタンダード形態論的アノテーションが必要です。この指標がない場合、残りの8つの指標（合計重み0.85）はそれぞれ1/0.85 ≈ 1.176でスケーリングされます。例えば：
> - FST：0.25/0.85 = 0.294
> - chrF++：0.15/0.85 = 0.176
> - 意味的：0.15/0.85 = 0.176

#### プロファイルB：FSTカバレッジがない言語

形態論的検証ツールのない言語向け。意味指標と表層指標が等しい重みを持ちます。

| 指標 | 目標重み | 根拠 |
|--------|--------------|-----------|
| `semantic_score` | **0.25** | 構造的検証なしでは、意味保存が最も強力な利用可能なシグナルです。 |
| `chrf_plus_plus` | **0.25** | FSTなしでは、文字レベルの重複が主要な表層チェックになります。 |
| `equivalent_match_rate` | **0.15** | 変形マッチングは形態論的ツールを必要とせずに構造化された品質評価を提供します。 |
| `exact_match_rate` | **0.10** | FSTなしでは、完全一致が唯一の構造的検証プロキシとしてより大きな重みを持ちます。 |
| `code_switching_rate` | **0.10** | FSTが不良な出力を捉えられない場合、ソース言語の漏れはより重要になります。 |
| `terminology_adherence` | **0.05** | コーチング語彙コンプライアンス。 |
| `hallucination_rate` | **0.05** | 捏造されたコンテンツの検出。 |
| `orthographic_accuracy` | **0.05** | スクリプト固有の正確さが、FSTの不在によって生じたギャップの一部を埋めます。 |

> **合計：1.00。** `orthographic_accuracy`（重み0.05）は計画中ですが、まだ算出されていません。これがない場合、残りの7つの指標（合計重み0.95）は1/0.95 ≈ 1.053でスケーリングされます — 複合への影響は無視できる程度です。

> **重みの進化に関する注記。** これらの重みは暫定的であり、人間の検証データが蓄積されるにつれて再較正されます。長期的な目標は、重みを経験的に導出することです：どの自動指標が各言語ファミリーの人間の品質判断を最もよく予測するか？

### 4.4 複合に新しい指標を追加する

複合に新しい指標を追加するには：

1. §2で`🔲 Planned`ステータスで**定義します**。スケール、レベル、および算出方法を含めます。
2. MetricPlugin（またはコア指標の場合は`tester.py`）として**実装します**。
3. ランカードのスコアブロックに**nullプレースホルダーを追加します**。
4. 既存の重みを下方調整することで§4.3で**目標重みを割り当てます**。重みの合計は1.00でなければなりません。
5. ランカードスキーマが変更される場合は**BENCHMARK_SPEC.md** §3を**更新します**。
6. **`scoring.py`**の重みテーブルを**更新します**（コードは本文書を反映しなければなりません）。
7. 指標が実際のデータで合理的な値を生成することを確認するために**検証ベンチマークを実行します**。
8. ステータスを`🔲`から`✅`に変更するために**本文書を更新します**。

---

## 5. 品質ティア

これらのティアは、自動複合スコアに対するヒューリスティックなラベルです。各レベルの出力の人間によるレビューに基づいて、スコアが実際に何を意味するかを説明します。**これらは検証された品質判断ではありません** — 実際の使用可能性を確認できるのは人間によるレビューのみです。

> [!IMPORTANT]
> **自動ティアは暫定的です。** これらのラベルはレビューのための候補であり、品質の宣言ではありません。自動指標で「Deployable」に達した手法はコミュニティ評価の候補です — 出荷する製品ではありません。実際の使用可能性を確認できるのは、バイリンガル話者による人間のレビューのみです（[BENCHMARK_SPEC §7](/docs/specifications/benchmark#7-human-validation)参照）。話者が出力を使用可能と同意するコミュニティレビューなしに、いかなる手法もDeployable以上を主張することはできません。ティア境界は、人間の検証データが蓄積されるにつれて言語によって異なる場合があります。

| ティア | 複合範囲 | 話者が通常目にするもの |
|------|----------------|-------------------------------|
| **Baseline** | 0.00–0.30 | 言語固有のサポートなしの生のLLM出力。形態論はほぼ幻覚。 |
| **Emerging** | 0.30–0.50 | 一部の正しいパターンが現れ始めている。コーチングは助けているが、出力は信頼できない。 |
| **Functional** | 0.50–0.70 | 出力は話者に認識可能。主要な文法カテゴリは通常正しい。形態論的エラーが頻繁。 |
| **Deployable** | 0.70–0.85 | 人間によるレビューを伴うドラフト翻訳に適している。ほとんどの形態論は正しい。 |
| **Fluent** | 0.85–1.00 | 有能な人間翻訳に近づいている。エラーはまれで軽微。 |

これらのティアは暫定的です。人間の検証データが蓄積され、「話者がこれを有用と感じる」閾値が各言語で実際にどこにあるかを学ぶにつれて再較正されます。バイリンガル話者が出力を使用可能と同意するコミュニティレビューなしに、いかなる手法も**Deployable**以上を主張することはできません。

### 5.1 ティア閾値（機械可読）

コード実装では、閾値は次のとおりです（上から下に評価し、最初の一致が優先）：

```
composite >= 0.85  →  "fluent"
composite >= 0.70  →  "deployable"
composite >= 0.50  →  "functional"
composite >= 0.30  →  "emerging"
composite >= 0.00  →  "baseline"
composite is null  →  "unscored"
```

---

## 6. コスト指標

コスト指標は翻訳手法の財務効率を測定します。品質とは別に報告されます — コストは複合スコアに影響しません（コスト調整二次ランキングを除く）。

### 6.1 トークン指標

| ID | 指標 | 算出 |
|----|--------|-------------|
| `prompt_tokens` | 総入力トークン | すべてのAPI呼び出しにわたる`usage.prompt_tokens`の合計 |
| `completion_tokens` | 総出力トークン | `usage.completion_tokens`の合計 |
| `reasoning_tokens` | 思考連鎖トークン | `usage.completion_tokens_details.reasoning_tokens`の合計（ほとんどのモデルでは0） |
| `cached_tokens` | プロバイダーキャッシュトークン | `usage.prompt_tokens_details.cached_tokens`の合計 |
| `total_tokens` | 消費総トークン | `prompt_tokens + completion_tokens` |
| `tokens_per_entry` | 翻訳あたりの平均トークン | ✅ `total_tokens / entry_count` |

### 6.2 コスト指標

| ID | 指標 | 算出 | ユースケース |
|----|--------|-------------|----------|
| `total_cost_usd` | 総ラン費用 | プロバイダー報告価格 × トークン数 | 「このベンチマークにいくらかかったか？」 |
| `cost_per_entry_usd` | コーパスエントリあたりのコスト | `total_cost_usd / entry_count` | 同じコーパスでの手法の比較 |
| `cost_per_1k_tokens` | 1,000トークンあたりのコスト | ✅ `total_cost_usd / total_tokens × 1000` | 汎用LLM効率 — コーパスをまたいで比較可能 |
| `cost_per_source_char` | ソース文字あたりのコスト | `total_cost_usd / total_source_chars` | 異なるトークン化を持つ言語をまたいで比較可能 |

> **複数のコスト指標がある理由？** 「エントリ」は長さが異なります — 3語のフレーズは段落よりもコストが低くなります。`cost_per_entry_usd`は*同じ*コーパスでの手法の比較に有用です（同じエントリ = 同じ長さ = 公平な比較）。`cost_per_1k_tokens`は標準的なLLM効率指標であり、コーパスを*またいで*比較可能です。`cost_per_source_char`はトークン化の違いを正規化します — 同じ文がモデルの語彙によって異なる数のトークンにトークン化される場合があります。

### 6.3 コスト調整スコア

有料APIを使用する手法については、二次ランキングを算出します：

```
cost_adjusted = composite / log2(1 + cost_per_entry_usd × 1000)
```

これは効率的に良いスコアを達成する手法を報酬として与えます。コスト調整スコアは常に単一のベンチマーク内（同じコーパス）で算出されるため、エントリあたりの比較が公平であることから、`cost_per_entry_usd`（トークンあたりではなく）を使用します。

コスト調整スコアは**二次ランキング**です — 主要なリーダーボードは複合スコアでランク付けします。これは異なる質問に答えます：「予算が与えられた場合、どの手法が最良の結果をもたらすか？」

---

## 7. 速度指標

速度指標は翻訳手法のレイテンシとスループットを測定します。コストと同様に、速度は複合スコアに影響しません。

| ID | 指標 | 算出 | レベル |
|----|--------|-------------|-------|
| `elapsed_seconds` | ウォールクロック実行時間 | `time_end - time_start` | ラン |
| `avg_latency_seconds` | エントリあたりの平均レイテンシ | `Σ latency_s / n_entries` | コーパス |
| `median_latency_seconds` | エントリあたりの中央値レイテンシ | `latency_s`の第50パーセンタイル | コーパス |
| `p95_latency_seconds` | 第95パーセンタイルレイテンシ | `latency_s`の第95パーセンタイル | コーパス |
| `tokens_per_second` | スループット | `total_tokens / elapsed_seconds` | ラン |
| `entries_per_minute` | 翻訳レート | `entry_count / (elapsed_seconds / 60)` | ラン |

---

## 8. 信頼区間と有意性

### 8.1 ブートストラップ信頼区間

すべての主要指標はブートストラップ信頼区間をサポートします（パーセンタイル法、n=1000リサンプル、α=0.05）：

| 指標 | 報告されるCI |
|--------|------------|
| `chrf_plus_plus` | ✅ `chrf_ci_lower`、`chrf_ci_upper` |
| `exact_match_rate` | ✅ `exact_match_ci_lower`、`exact_match_ci_upper` |
| `fst_acceptance_rate` | ✅ `fst_ci_lower`、`fst_ci_upper`（FSTデータが存在する場合のみ算出） |
| `comet_score` | ✅ `comet_ci_lower`、`comet_ci_upper`（キャッシュされたエントリごとのスコアからブートストラップ — 冗長なニューラル推論なし） |
| `composite` | ✅ `composite_ci_lower`、`composite_ci_upper`（chrF++とexact_matchが利用可能な場合に算出） |
| ティアごとのCI | ✅ `confidence_intervals_by_tier` — 難易度レベル（ティア1-5）ごとのchrF++とexact_matchのCI |

### 8.2 ペアードブートストラップ有意性検定

2つの手法を比較するために、ハーネスはペアードブートストラップリサンプリング検定を算出します：

```
H₀: The two methods perform equally on this corpus.
H₁: One method is significantly better.
```

p値 < 0.05かつ差の信頼区間がゼロを除外する場合、差は95%レベルで統計的に有意です。

---

## 9. ランカードスコアスキーマ

このセクションでは、ランカード内の`scores`ブロックの階層構造を定義します。このスキーマは§2–§7で定義された指標から派生しており、同期を保つ必要があります。

```jsonc
{
  "scores": {
    // §2.1 Surface metrics
    "exact_match_rate":       0.6613,       // 0.0–1.0
    "exact_matches":          41,           // count
    "equivalent_match_rate":  0.7258,       // ⚡ partial (CRK: eval_standards/crk CrkLinterMetric)
    "equivalent_matches":     45,           // ⚡ partial (CRK: eval_standards/crk CrkLinterMetric)
    "chrf_plus_plus":         80.65,        // 0–100 (sacrebleu native scale)
    "bleu":                   54.78,        // 0–100, NOT in composite
    "ter":                    42.3,         // ✅ implemented, 0–∞ (lower=better)
    "length_ratio":           1.03,         // ✅ implemented, ideal=1.0

    // §2.2 Structural metrics
    "fst_acceptance_rate":    1.0,          // 0.0–1.0
    "fst_accepted":           74,           // count
    "morphological_accuracy": null,         // 🔲 planned
    "orthographic_accuracy":  null,         // 🔲 planned

    // §2.3 Semantic metrics
    "semantic_score":         0.6842,       // ⚡ partial (CRK: eval_standards/crk CrkSemanticMetric)
    "comet_score":            null,         // nullable, NOT in composite
    "comet_model":            "",           // model ID used for COMET

    // §2.4 Behavioral metrics
    "code_switching_rate":    0.03,         // ✅ implemented (lower=better)
    "hallucination_rate":     0.01,         // ✅ implemented (lower=better)
    "terminology_adherence":  null,         // ✅ implemented (null when no glossary)
    "consistency_score":      null,         // 🔲 planned

    // §4 Composite
    "composite":              0.8988,       // 0.0–1.0
    "quality_tier":           "fluent",     // §5 tier label
    "cost_adjusted":          null,         // §6.3 secondary ranking

    // §7 Speed metrics (merged into scores block)
    "tokens_per_second":      4462.5,       // ✅ total_tokens / elapsed
    "entries_per_minute":     82.30,        // ✅ entry_count / (elapsed/60)
    "avg_latency_seconds":    0.234,
    "median_latency_seconds": 0.190,
    "p95_latency_seconds":    0.415,

    // §8.1 Confidence intervals
    "confidence_intervals": {
      "chrf_plus_plus":     { "ci_lower": 78.2, "ci_upper": 83.1 },
      "exact_match_rate":   { "ci_lower": 0.54, "ci_upper": 0.78 },
      "corpus_comet":       { "ci_lower": 0.71, "ci_upper": 0.76 }
    },
    "confidence_intervals_by_tier": {
      "1": { "corpus_chrf": { "ci_lower": 68.1, "ci_upper": 76.5 } },
      "3": { "corpus_chrf": { "ci_lower": 36.2, "ci_upper": 47.0 } }
    },

    // Breakdowns
    "by_difficulty":          {},           // scores grouped by difficulty tier
    "by_provenance":          {},           // scores grouped by entry provenance

    // Counts
    "total":                  62,
    "evaluated":              62,
    "errors":                 0
  },

  "totals": {
    // §6.1 Token metrics
    "prompt_tokens":          13985,
    "completion_tokens":      187822,
    "reasoning_tokens":       175726,
    "cached_tokens":          0,
    // §6.2 Cost metrics
    "total_cost_usd":         1.7114,
    "cost_per_entry_usd":     0.027603,
    "cost_per_source_char":   null          // 🔲 needs source char counting
  }
}
```

> **スキーマの歴史。** 以前の仕様草案では、別々の`cost`、`speed`、および`tokens`ブロックが提案されていました。これらはシンプルさのために`scores`と`totals`にそれぞれマージされました。速度指標（`tokens_per_second`、`entries_per_minute`、レイテンシ）は`scores`に存在し、トークン数とコスト数値は`totals`に存在します。

### 9.1 スキーマ–データベースマッピング

ランカードJSONはSupabaseの`jsonb`カラムに完全に保存されます。主要な指標はソート・フィルタのパフォーマンスのためにトップレベルのカラムにも非正規化されます：

| ランカードフィールド | Supabaseカラム | 型 | インデックス |
|---------------|----------------|------|-------|
| `scores.composite` | `composite_score` | `real` | `idx_composite` |
| `scores.quality_tier` | `quality_tier` | `text` | — |
| `scores.chrf_plus_plus` | `chrf_plus_plus` | `real` | `idx_leaderboard` |
| `scores.exact_match_rate` | `exact_match_rate` | `real` | — |
| `scores.fst_acceptance_rate` | `fst_acceptance_rate` | `real` | — |
| `scores.bleu` | `corpus_bleu` | `real` | — |
| `scores.comet_score` | `comet_score` | `real` | — |
| `totals.total_cost_usd` | `total_cost_usd` | `real` | — |
| `totals.cost_per_entry_usd` | `cost_per_entry_usd` | `real` | — |
| `totals.cost_per_source_char` | `cost_per_source_char` | `real` | — |
| `scores.avg_latency_seconds` | `avg_latency_seconds` | `real` | — |
| `model_slug` | `model_slug` | `text` | `idx_model` |
| `condition` | `condition` | `text` | — |
| `dataset.id` | `dataset_id` | `text` | `idx_leaderboard` |
| `dataset.language_pair` | `language_pair` | `text` | — |
| `fingerprint.hash` | `fingerprint_hash` | `text` | `idx_fingerprint` |
| `scores.equivalent_match_rate` | `equivalent_match_rate` | `real` | — |
| `scores.semantic_score` | `semantic_score` | `real` | — |
| `scores.ter` | `ter` | `real` | — |
| `scores.length_ratio` | `length_ratio` | `real` | — |
| `scores.code_switching_rate` | `code_switching_rate` | `real` | — |
| `scores.hallucination_rate` | `hallucination_rate` | `real` | — |
| `scores.terminology_adherence` | `terminology_adherence` | `real` | — |
| `scores.tokens_per_second` | `tokens_per_second` | `real` | — |
| `scores.entries_per_minute` | `entries_per_minute` | `real` | — |
| `elapsed_seconds` | `elapsed_seconds` | `real` | — |
| *（完全なカード）* | `run_card` | `jsonb` | — |

新しい指標が実装される場合、対応するカラムは`arena/migrations/`の番号付きマイグレーションを通じて追加する必要があります。

---

## 10. コード–仕様の同期

### 10.1 正規ソース

本文書（`arena/website/docs/specifications/scoring.md`）は以下の正規ソースです：
- 指標定義（§2）
- 複合重みテーブル（§4.3）
- 品質ティア閾値（§5.1）
- コスト指標式（§6.2）
- ランカードスコアスキーマ（§9）

### 10.2 コードミラー

ファイル`arena/mt_eval_harness/scoring.py`は本文書の重みテーブルとティア閾値を反映します。これは§4.3と§5.1の**コード実装**です。本文書が更新される場合：

1. `scoring.py`を一致するよう更新する
2. `pytest tests/test_scoring_ssot.py`を実行してアライメントを検証する
3. 重みを要約するFAQとウェブサイトドキュメントを更新する

### 10.3 本仕様を参照するドキュメント

| ドキュメント | 参照内容 | 同期を保つ方法 |
|----------|-------------------|---------------------|
| `arena/website/docs/specifications/benchmark-spec.md` §4–§5 | 複合式、重みテーブル、ティア閾値 | 本文書を相互参照；テーブルを複製しない |
| `website/docs/getting-started/faq.md` | 簡略化された重みサマリー | §4.3と一致しなければならない；本文書にリンクバック |
| `arena/website/docs/how-it-works.md` | Deployable閾値 | §5と一致しなければならない |
| `publish.py`（`scoring.py`経由） | 重み辞書 + ティア関数 | 自動テストが一致を検証 |

---

## 付録A：複合に含まれない指標（およびその理由）

| 指標 | 除外理由 |
|--------|-------------|
| **BLEU** | 単語レベルのスコアリングは多合成語的言語における形態論的変形を不当にペナルティ化します。軽微な活用形の違い（正しい意味、わずかに異なる接尾辞）が完全なミスとしてカウントされます。chrF++は文字レベルでこれをより適切に処理します。 |
| **COMET** | WMTデータ（高リソースのヨーロッパ言語ペア）で学習済み。LRLのスコアは信頼性が低く、モデルは根本的に異なる形態論的システムを持つ言語から外挿しています。透明性のために報告されますが、スコアリングには使用されません。 |
| **TER** | 編集距離はほとんどのユースケースでchrF++と相関します。両方を含めると表層類似性を二重にカウントすることになります。TERは参照のために報告されます。 |
| **長さ比率** | 診断であり、品質シグナルではありません。1.02の比率と0.98の比率はどちらも問題ありません。極端な値のみが問題を示します。 |
| **一貫性スコア** | コーパスレベルのみ — 集約するエントリごとの値がありません。また、一部の不一致は正当です（同じ英語の単語 → 文脈によって異なる対象言語の翻訳）。 |
| **コンプライアンスインデックス** | 品質シグナルではなく品質ゲート。構造的保存（プレースホルダー、引用符）を測定するものであり、翻訳精度ではありません。 |

## 付録B：LYSS — 言語固有の指標実装

**LYSS**フレームワーク（Linguistically-informed Yield & Structural Scoring）は、表層レベルの文字列比較を超えた言語固有の指標を提供します。LYSSには3つのコアコンポーネントがあります：

- **LYSS-fst** — 形態論的妥当性（`fst_acceptance_rate`）：各単語は対象言語の有効な形式か？
- **LYSS-eq** — 言語的等価性（`equivalent_match_rate`）：出力は参照の受理可能な変形か？
- **LYSS-sem** — 意味検証（`semantic_score`）：出力はソースの意味を保持しているか？

> **検証ステータス：🔶 エンジニアリングヒューリスティック。** LYSS指標は人間の品質判断に対して検証されていません。言語的原則（UAlberta ALTLabの言語学者が構築したFST、辞書、文法ルール）から設計されていますが、LYSSスコアと実際の翻訳品質の相関は測定されていません。必要な検証実験については[話者検証プロトコル](/docs/specifications/speaker-validation)を参照してください。

| 言語 | プラグイン | 場所 | LYSSコンポーネント | 指標キー | 注記 |
|----------|--------|----------|----------------|------------|-------|
| CRK（プレーンズ・クリー語） | `CrkLinterMetric` | `eval_standards/crk/metrics.py` | **LYSS-eq** | `equivalent_match_rate` | 決定論的変形クラスルール：語順、正書法、任意助詞、補題同義語、進行形曖昧性、包括/排他。エントリごとの`lint_verdict`（EXACT/EQUIVALENT/MISS/NO_OUTPUT）を生成します。 |
| CRK | `CrkSemanticMetric` | `eval_standards/crk/metrics.py` | **LYSS-sem** | `semantic_score` | 決定論的：FST補題抽出 + 辞書グロス + spaCy内容語重複。判定（EXACT_MATCH/VALID/GRAMMAR_ISSUES/PARTIAL/INCOMPLETE/WRONG/NO_OUTPUT）を生成します。 |
| GiellaLT言語 | `GiellaLTFSTMetric` | `plugins/giellalt_fst.py` | **LYSS-fst** | `fst_acceptance_rate` | 汎用：CRK、SME、SMA、SMJ、SMN、SMS、FIN、NOB、IKU — `.hfstol`解析器を持つ任意の言語で動作します。 |

> **アーキテクチャ注記（2026年6月）。** 言語固有のLYSS指標は、`evalMetrics`の言語カードで宣言され、`plugin_discovery.py`によって`eval_standards/<lang>/`から読み込まれるようになりました。これらは**評価標準**（審判）であり、手法プラグイン指標（競技者）ではありません。つまり、CRKを対象とする任意の翻訳手法は自動的にLYSSでスコアリングされます — 手法固有の設定は不要です。`CrkFSTMetric`は削除されました；その機能は汎用`GiellaLTFSTMetric`によって完全にカバーされています。

## 付録C：検討中の指標

これらはまだ§2に仕様化するほど具体化されていないアイデアです：

| アイデア | 測定対象 | ブロッカー |
|------|----------------------|----------|
| 流暢さ（LMパープレキシティ） | 出力は対象言語として整形された散文か？ | 対象言語のLMが必要。ほとんどのLRLには良いモデルが存在しない。 |
| レジスターマッチ | 翻訳は期待される形式レベルと一致するか？ | 社会言語学的分類器が必要。研究上の問題。 |
| 文化的適切さ | 文化的参照は正しく処理されているか？ | 自動化できない — 本質的に人間によるレビューが必要。 |
| 談話一貫性 | 連続した翻訳は一貫したパッセージを形成するか？ | 文レベルではなく文書レベルの評価が必要。 |

---

## 参考文献

本仕様全体で引用された学術論文、ツール、および言語リソース。

### 表層指標

1. Popović, M. (2017). "chrF++: words helping character n-grams." *Proceedings of the Second Conference on Machine Translation (WMT 2017)*, pp. 612–618. Copenhagen, Denmark.

2. Papineni, K., Roukos, S., Ward, T., & Zhu, W.-J. (2002). "BLEU: a method for automatic evaluation of machine translation." *Proceedings of the 40th Annual Meeting of the Association for Computational Linguistics (ACL 2002)*, pp. 311–318. Philadelphia, PA.

3. Post, M. (2018). "A Call for Clarity in Reporting BLEU Scores." *Proceedings of the Third Conference on Machine Translation (WMT 2018)*, pp. 186–191. Belgium, Brussels. Reference implementation: [sacrebleu](https://github.com/mjpost/sacrebleu).

4. Snover, M., Dorr, B., Schwartz, R., Micciulla, L., & Makhoul, J. (2006). "A Study of Translation Edit Rate with Targeted Human Annotation." *Proceedings of the 7th Conference of the Association for Machine Translation in the Americas (AMTA 2006)*, pp. 223–231. Cambridge, MA.

### ニューラル指標

5. Rei, R., Stewart, C., Farinha, A. C., & Lavie, A. (2020). "COMET: A Neural Framework for MT Evaluation." *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP 2020)*, pp. 2685–2702. Online.

6. Juraska, J., Finkelstein, M., Deutsch, D., Siddhant, A., Miber, D., & Markl, A. (2023). "MetricX-23: The Google Submission to the WMT 2023 Metrics Shared Task." *Proceedings of the Eighth Conference on Machine Translation (WMT 2023)*. Singapore.

7. Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y. (2020). "BERTScore: Evaluating Text Generation with BERT." *Proceedings of the Eighth International Conference on Learning Representations (ICLR 2020)*. Addis Ababa, Ethiopia.

8. Sellam, T., Das, D., & Parikh, A. (2020). "BLEURT: Learning Robust Metrics for Text Generation." *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020)*, pp. 7881–7892. Online.

### 形態論的・言語的ツール

9. Lindén, K., Silfverberg, M., Axelson, E., Hardwick, S., & Pirinen, T. (2011). "HFST—Framework for Compiling and Applying Morphologies." *Systems and Frameworks for Computational Morphology (SFCM 2011)*, Communications in Computer and Information Science, vol. 100, pp. 67–85. Springer, Berlin, Heidelberg.

10. Sánchez-Cartagena, V. M., & Toral, A. (2024). "MorphEval: Automatic Evaluation of Morphological Capabilities of Machine Translation Systems." *Machine Translation*, vol. 38, pp. 1–28.

### エラー分類と診断評価

11. Popović, M. (2011). "Hjerson: An Open Source Tool for Automatic Error Classification of Machine Translation Output." *The Prague Bulletin of Mathematical Linguistics*, no. 96, pp. 59–68.

12. Dreyer, M. & Marcu, D. (2012). "HyTER: Meaning-Equivalent Semantics for Translation Evaluation." *Proceedings of the 2012 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2012)*, pp. 162–171. Montréal, Canada.

13. Reiter, E. & Belz, A. (2009). "An Investigation into the Validity of Some Metrics for Automatically Evaluating Natural Language Generation Systems." *Computational Linguistics*, vol. 35, no. 4, pp. 529–558. (Related work on feature-based evaluation metrics, including FUSE.)

### 幻覚検出

14. Raunak, V., Menezes, A., & Junczys-Dowmunt, M. (2021). "The Curious Case of Hallucinations in Neural Machine Translation." *Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2021)*, pp. 1172–1183. Online.

15. Guerreiro, N. M., Voita, E., & Martins, A. F. T. (2023). "Looking for a Needle in a Haystack: A Comprehensive Study of Hallucinations in Neural Machine Translation." *Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2023)*, pp. 1059–1075. Dubrovnik, Croatia.

### クリー語リソース

16. Wolfart, H. C. (1973). "Plains Cree: A Grammatical Study." *Transactions of the American Philosophical Society*, vol. 63, no. 5, pp. 1–90.

17. Wolvengrey, A. (2001). *nêhiyawêwin: itwêwina / Cree: Words.* Canadian Plains Research Center, University of Regina.

### データガバナンス

18. First Nations Information Governance Centre. "The First Nations Principles of OCAP®." [https://fnigc.ca/ocap-training/](https://fnigc.ca/ocap-training/). (OCAP® is a registered trademark of the First Nations Information Governance Centre.)

19. Carroll, S. R., Garba, I., Figueroa-Rodríguez, O. L., Holbrook, J., Lovett, R., Materechera, S., Parsons, M., Raseroka, K., Rodriguez-Lonebear, D., Rowe, R., Sara, R., Walker, J. D., Anderson, J., & Hudson, M. (2020). "The CARE Principles for Indigenous Data Governance." *Data Science Journal*, vol. 19, no. 1, p. 43.