---
sidebar_position: 5
title: "低リソース言語をサポートする"
related:
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "The first step for an uncovered language"
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
  - label: "Plains Cree, the trading card"
    to: https://champollion.dev/trading-cards?q=crk
    kind: card
    note: "The proof-of-concept language, as a card"
---
# 低リソース言語のサポート

> **要旨。** 低リソース言語および多合成語的言語のための機械翻訳を構築するための包括的なガイドです。これらの言語が難しい理由（形態論的複雑さ、データの希少性、幻覚）、既存の計算資源（ALTLab FST、GiellaLT、Apertium、UniMorph、EdTeKLA）、10以上のアプローチ戦略、champollion のコーチングシステム、および評価ループについて説明します。十分なサービスを受けていない言語のメソッドを貢献したい場合は、まずここから始めてください。

:::info ステータス：開発中
Plains Cree（nêhiyawêwin）のサポートは現在開発中です。ここで説明するツール、評価ハーネス、およびリーダーボードは実際に使用可能ですが、Cree の翻訳パイプラインはまだリリースされていません。リリースされた際には、FST インフラを持つ他の多合成語的言語および低リソース言語のための設計図として機能します。
:::

## 未解決の問題

Google Translate は約130言語をサポートしています。Meta の OMT-1600（2026年3月）は1,600言語のカバレッジを主張しており、これまでに公開された最大の MT システムです。しかし、最も低いリソース層にある約1,300言語については、品質は使用可能な閾値を下回り、学習データは聖書テキストが大半を占め、モデルの重みはダウンロードできず、独立した評価やコミュニティガバナンスの枠組みも存在しません。残りの約5,400言語については、事前学習済みモデルがまったく出力を生成しません。

状況は大きく変化しており、大手テクノロジー企業が低リソース言語（LRL）のカバレッジに投資するようになっています。しかし、カバレッジは品質ではなく、独立した検証のない品質は信頼ではありません。低リソース言語には、カバレッジを主張するモデル以上のものが必要です。形態論的検証を伴う独立した評価、コミュニティが管理するコーパス、そして主権を尊重するガバナンスが必要です。

**champollion はそれを変えるために構築されました。**

[メソッドリーダーボード](https://champollion.dev/leaderboard)はオープンなチャレンジです。十分なサービスを受けていない言語に対して最良の翻訳メソッドを構築し、再現可能な評価でそれを証明し、トップスコアを獲得してください。世界中の誰でも貢献できます。言語学者、ML 研究者、コミュニティの言語担当者、学生、愛好家など、誰でも参加できます。問題は未解決です。インフラは整っています。リーダーボードはあなたを待っています。

---

## なぜ難しいのか：多合成語的形態論

ほとんどの商用 MT システムは、英語、フランス語、中国語のような言語向けに設計されています。これらの言語では、単語は比較的短く、文は個別のトークンから構成されます。しかし、Plains Cree を含む多くの先住民言語は**多合成語的**です。つまり、英語では文全体で表現するものを、単一の単語でエンコードできます。

### Cree の例

Plains Cree の単語を考えてみましょう：

> **ê-kî-nitawi-kîskinwahamâkosiyân**
> *「私が学校に行ったとき」*

これは**1つの単語**です。時制（過去）、方向（行く）、語根（学ぶ）、態（受動/再帰）、人称（一人称単数）をエンコードしています。主に英語で学習した LLM は、このような形態論的密度に対する直感を持っていません。

課題は複合的です：

| 課題 | 意味 |
|-----------|--------------|
| **形態論的複雑さ** | 単一の動詞語根が、接頭辞付加、接尾辞付加、および接周辞付加によって何千もの有効な活用形を生成できる |
| **有生・無生の区別** | 名詞は文法的に有生または無生に分類され、これが動詞の活用、指示詞、および複数形に影響する。この分類は必ずしも生物学的な有生性に従わない（*askiy*「大地」は有生；*maskisin*「靴」も有生） |
| **遠称** | 三人称の参照は近接性・顕著性によってランク付けされる。「近称」と「遠称」の区別には英語に相当するものがない |
| **学習データの希少性** | LLM が見てきた Plains Cree のテキストは非常に少ない。見てきたものは方言（Y方言、TH方言）や正書法（SRO とシラビクス）が混在している可能性がある |
| **商用ベースラインの弱さ** | OMT-1600 は CRK を R1（非常に低リソース）層に含め、聖書ドメインの学習と標準 BPE トークン化を使用している。Google Translate は Cree をサポートしていない。形態論的メトリクスを用いた独立した評価こそが、これらのベースラインを意味のあるものにする。 |

多合成語的言語の翻訳は**未解決の研究課題**であり続けています。OMT-1600 は多合成語的言語を含んでいますが、形態論的認識のない標準 BPE トークン化（256K 語彙）を使用しており、合成的な単語を意味のないバイト断片に分解してしまいます。

---

## 先行研究：これまでのアプローチ

### ALTLab FST

Plains Cree に対する最も重要な計算資源は、ノルウェー北極大学 UiT の [Giellatekno](https://giellatekno.uit.no/) と協力して、アルバータ大学の [Alberta Language Technology Lab（ALTLab）](https://altlab.artsrn.ualberta.ca/)が開発した**有限状態トランスデューサ（FST）**です。

ALTLab FST は**形態論的アナライザーおよびジェネレーター**です。活用した Cree の単語が与えられると、その語根と文法タグに分解でき、語根とタグが与えられると、正しい活用形を生成できます。これは決定論的であり、ニューラルネットワークも幻覚も確率もありません。FST が単語を受け入れれば、その単語は形態論的に有効です。

これが、champollion リーダーボードが**FST 受理率**をメトリクスとして追跡する理由です。FST が拒否する単語を生成する翻訳メソッドは、chrF++ スコアが何を示していても、形態論的に無効な Cree を生成しています。

**主要な ALTLab リソース：**
- [itwêwina](https://itwewina.altlab.app/) — FST を活用したインテリジェントな Plains Cree–英語辞書
- [Morphodict](https://github.com/UAlbertaALTLab/morphodict) — オープンソースの形態論的認識辞書プラットフォーム
- [crk-db](https://github.com/UAlbertaALTLab/crk-db) — Plains Cree 語彙データベース
- [21st Century Tools for Indigenous Languages](https://21c.tools/) — より広いプロジェクトの文脈

### グローバル FST および形態論レジストリ

Plains Cree は高品質な FST インフラを持つ唯一の言語ではありません。他の低リソース言語や形態論的に複雑な言語の翻訳パイプラインを開発したい場合は、以下の確立されたグローバルハブを活用できます：

* **[GiellaLT / Giellatekno](https://giellalt.github.io/)（ノルウェー北極大学 UiT）：** 100以上の言語をカバーする、オープンソース FST 形態論的アナライザーおよびジェネレーターの最大のリポジトリです。重点分野はサーミ語（`sme`、`smj`、`sma`など）、ウラル語族（コミ語、エルジャ語、ウドムルト語など）、およびその他の少数・先住民言語です。[GitHub Organization](https://github.com/giellalt/) で公開処理済みテキストコーパス（`corpus-xxx`）をホストしています。
* **[The Apertium Project](https://www.apertium.org/)：** オープンソースのルールベース機械翻訳プラットフォームです。Apertium は、チュルク語族（カザフ語、タタール語、キルギス語など）や少数ヨーロッパ言語を含む数十の言語に対して、高度に最適化された FST 形態論的アナライザー（`lttoolbox` および `hfst` を使用）と二言語辞書を管理しています。すべてのリソースは [Apertium の GitHub](https://github.com/apertium) で公開されています。
* **[UniMorph（Universal Morphology）](https://unimorph.github.io/)：** 150以上の言語に対して標準化された形態論的パラダイムを提供する共同プロジェクトです。データセットは Hugging Face の [unimorph/universal_morphologies](https://huggingface.co/datasets/unimorph/universal_morphologies) でホストされています。ある言語のコンパイル済み FST バイナリが利用できない場合、UniMorph テーブルを静的データベースルックアップゲートとして使用できます。
* **[National Research Council Canada（NRC）](https://nrc-digital-repository.canada.ca/)：** カナダ先住民言語向けのツールを提供しており、**Uqailaut** イヌクティトゥット語 FST 形態論的アナライザーと、大規模な**ヌナブト・ハンサード並列コーパス**（英語-イヌクティトゥット語の130万アライメント文ペア）が含まれます。

### EdTeKLA コーパス

[EdTeKLA 研究グループ](https://spaces.facsci.ualberta.ca/edtekla/)（同じくアルバータ大学）は、教育資料、音声転写、およびコミュニティソースから Plains Cree 言語コーパスを構築しました。champollion の評価データセット [EDTeKLA Dev v1](/docs/leaderboard/datasets) はこの研究から派生しており、[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) でライセンスされています。

### その他の試みられた、または試みられ得るアプローチ

リーダーボードはメソッドに依存しません。以下は低リソース MT に対して探求された、または提案された戦略であり、いずれも提出可能です：

| アプローチ | 仕組み | 長所 | 短所 |
|----------|-------------|------|------|
| **[コーチング付き LLM プロンプティング](/docs/tutorials/coached-llm-prompting)** | 文法規則、辞書、例文ペアをシステムプロンプトに注入する | 反復が速く、学習不要 | 品質の上限は LLM の基礎知識に制限される |
| **[Few-shot プロンプティング](/docs/tutorials/few-shot-prompting)** | 検証済みの翻訳をインコンテキスト例として含める | 一貫したスタイルに有効 | コンテキストウィンドウが小さい；例は評価データから取得してはならない |
| **[FST ゲート付きパイプライン](/docs/tutorials/fst-gated-pipeline)** | LLM が生成 → FST が検証 → 無効な形態論を拒否して再試行 | 形態論的有効性を保証する | FST インフラが必要；再試行ループがレイテンシとコストを増加させる |
| **[辞書ルックアップ + LLM](/docs/tutorials/dictionary-augmented-llm)** | 二言語辞書から既知の用語を強制し、残りは LLM に任せる | 既知の用語の幻覚を減らす | 辞書のカバレッジは常に不完全 |
| **[ファインチューニング済みモデル](/docs/tutorials/fine-tuned-model)** | オープンモデル（Llama、Mistral）を並列テキストでファインチューニングする（評価データは除く） | 潜在的に最高品質 | 並列コーパスが必要（希少）；高コスト；過学習リスク |
| **[連鎖モデル](/docs/tutorials/chained-models)** | モデル A が粗訳を生成 → モデル B が後編集 → モデル C がスコアリング | 専門家の強みを組み合わせられる | 複雑；低速；高コスト |
| **[ルールベース + LLM ハイブリッド](/docs/tutorials/rule-based-hybrid)** | 既知のパターンには言語規則を使用し、それ以外は LLM に任せる | 規則が適用される箇所では正確 | 深い言語学的専門知識が必要 |
| **[バック翻訳拡張](/docs/tutorials/back-translation)** | Cree→英語の翻訳によって合成並列データを生成し、逆方向で学習する | 学習データを低コストで拡張できる | 既存のモデルエラーを増幅する |
| **[進化的アプローチ](/docs/tutorials/evolutionary-approach)** | 翻訳候補を生成し、スコアリングし、最良のものを変異させ、繰り返す | 新しい解を発見できる；並列化可能 | 計算コストが高い；良い適合度関数が必要 |
| **[部分翻訳](/docs/tutorials/partial-translation)** | 代表的なサンプルを手動で翻訳し、そのスタイルにメソッドが合致することを証明してから、残りの大量のテキストを自動翻訳する | 人間の品質と機械のスケールを組み合わせる | 初期の人的作業が必要 |
| **手動 JSON / 試験採点** | データセット JSON ファイルを手作りして言語試験の学生の回答をテストするか、人間の翻訳をゴールドスタンダードと照合して採点する | ML 不要；教育と QA に有効 | 継続的な翻訳ニーズにはスケールしない |

### JSON に過ぎない

ハーネスは JSON を受け取り、スコアリングされた JSON を出力します。[データセット形式](/docs/leaderboard/datasets)はシンプルです：

```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

これは手作業で構築できます。スプレッドシートからエクスポートできます。コーパスから生成できます。言語教師が学生の翻訳を採点するために使用できます。翻訳会社がフリーランサーのベンチマークに使用できます。研究室がモデルアーキテクチャを比較するために使用できます。ハーネスは JSON がどこから来たかを気にしません。ただスコアリングするだけです。

また、本番デプロイメントフレームワークは同じプラグインインターフェースを使用するため、ハーネスで高スコアを獲得したメソッドは、設定を1つ変更するだけでウェブサイトにデプロイできます。**証明して、使う。**

可能性は本当に無限です。**アイデアがあれば、構築し、ハーネスを実行し、スコアを提出してください。**

---

## champollion の役割

champollion はインフラ層を提供します。メソッドはあなたが持ち込みます。

### コーチングシステム

champollion の `llm-coached` メソッドを使用すると、言語知識を LLM プロンプトに直接注入できます：

```json title=".champollion/coaching/crk.json"
{
  "grammar_rules": [
    "Plains Cree is polysynthetic — a single word can express what English needs a full sentence for",
    "Animate/inanimate noun distinction affects verb conjugation, demonstratives, and pluralization",
    "Use SRO (Standard Roman Orthography) as the working script — syllabic conversion is handled by the deterministic converter",
    "Obviation: when two third-person referents appear, the less salient one takes obviative marking (-a suffix on nouns, -iyiwa on verbs)"
  ],
  "dictionary": {
    "home": "kīwēwin",
    "settings": "isi-nākatohkēwin",
    "search": "nānātawāpahtam",
    "welcome": "tānisi",
    "dashboard": "kīskinwahamākēwin-māsinahikan"
  },
  "style_notes": "Use formal register appropriate for educational and community contexts. Preserve English technical terms in parentheses when no Cree equivalent exists or is widely accepted."
}
```

コーチングデータは `en:crk` ペアのすべての LLM プロンプトに注入され、モデルに通常は持っていない構造化された言語コンテキストを提供します。完全な仕様については [コーチングデータ](https://champollion.dev/docs/concepts/coaching-data) を参照してください。

### レジスター

レジスターは、トーン、フォーマリティ、および正書法の規則を制御するシステムプロンプトの一部です。champollion には Plains Cree のレジスターが1つ付属しています：

```
nêhiyawêwin (Plains Cree). Use SRO (Standard Roman Orthography) as the working
script. Output will be converted to Syllabics via deterministic converter.
Professional register appropriate for educational and community contexts.
```

設定でこれをオーバーライドして、異なるプロンプティング戦略を試すことができます：

```json title="champollion.config.json"
{
  "languages": {
    "crk": {
      "register": "Casual Plains Cree (Y-dialect). Use SRO. Prefer everyday vocabulary over formal or archaic terms. Address the reader directly."
    }
  }
}
```

レジスターが異なれば翻訳スタイルも異なり、リーダーボードのスコアも異なります。各提出には使用された正確なレジスターとシステムプロンプトが記録されます（[ランカード](/docs/specifications/run-card) の SHA-256 ハッシュとして）。これにより実験の再現性が確保されます。

### スクリプト変換

Plains Cree は2つのスクリプトで書かれています：**標準ローマ字正書法（SRO）** と**カナダ先住民シラビクス**です。champollion のパイプライン：

1. LLM が SRO（LLM が扱いやすいラテン文字ベース）に翻訳する
2. 品質ゲートが SRO 出力を検証する
3. 決定論的コンバーターが SRO → シラビクスに変換する
4. 変換されたテキストがディスクに書き込まれる

コンバーターはすべての SRO 発音区別符号（長母音の ê、î、ô、â）を処理し、正しいシラビクス文字にマッピングします。技術的な詳細については [スクリプトコンバーター](https://champollion.dev/docs/concepts/script-converters) を参照してください。

### 評価ループ

[評価ハーネス](/docs/specifications/harness) は評価データセットに対してメソッドを実行し、スコアリングされた [ランカード](/docs/specifications/run-card) を生成します：

```bash
# Clone the harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install -e .

# Run a baseline experiment
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v7

# Run with FST validation (if you have an FST binary)
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --fst-analyzer ./bin/crk-analyzer \
  --condition fst-gated-v1
```

`--condition` フラグはあなたが選択するラベルです。リーダーボードに表示され、使用したプロンプト戦略を確認できます。ハーネスはランカードに完全なシステムプロンプトを記録するため、正確なアプローチが再現可能です。

:::tip 自由に実験し、最良のものを提出する
ハーネスは高速な反復のために設計されています。異なるモデル、コーチングデータ、レジスター、および条件で何十もの実験を実行してください。誇りに思えるものができたときだけリーダーボードに提出してください。
:::

---

## OCAP 原則

champollion は先住民データ主権をサポートするように設計されています。[OCAP 原則](https://fnigc.ca/ocap-training/)（所有権、管理、アクセス、占有）は、先住民コミュニティのための言語技術へのアプローチを導きます：

| 原則 | champollion のサポート方法 |
|-----------|------------------------|
| **所有権（Ownership）** | 言語コミュニティは自分たちの言語データを所有する。champollion はホームに電話したり、私たちのサーバーにデータを送信したりすることはない |
| **管理（Control）** | [API メソッド](https://champollion.dev/docs/guides/serving-a-method) により、コミュニティが独自の翻訳パイプラインをホストできる。インターフェースを提供するのは私たちで、実装を管理するのはコミュニティ |
| **アクセス（Access）** | コミュニティが自分たちのメソッドを誰が使用できるかを決定する。API は認証によってゲートできる |
| **占有（Possession）** | すべての翻訳データはプロジェクトのファイルシステムに保存される。[来歴システム](https://champollion.dev/docs/concepts/security) がすべての翻訳の出所を追跡する |

プラグインアーキテクチャにより、コミュニティは内部に神聖または制限された知識を組み込んだメソッドを構築し、翻訳 API のみを公開し、言語リソースの完全な管理を維持できます。

---

## ビジョン：次に来るもの

Plains Cree が最初のターゲットです。パイプラインが検証され、コミュニティが品質に満足したら、同じアーキテクチャが FST インフラを持つ他の多合成語的言語に拡張されます：

- **他のアルゴンキン語族**：Woods Cree、Swampy Cree、オジブウェー語、ブラックフット語
- **イヌイット語族**：イヌクティトゥット語、イヌイナクトゥン語（シラビクスも使用）
- **他の語族**：FST アナライザーを持つ言語であれば、FST ゲート付きパイプラインを使用できる

リーダーボードは言語ペアごとにスコープされています。言語コミュニティから新しい評価データセットが提供されると、新しいリーダーボードトラックが自動的に開設されます。

**これはオープンな招待です。** 研究者、コミュニティメンバー、学生、または単純に関心を持つ人として低リソース言語に携わっているなら、champollion は本物を構築し、誠実に測定し、世界と共有するためのツールを提供します。[メソッドリーダーボード](https://champollion.dev/leaderboard) はあなたの提出を待っています。

---

## 関連情報

- **[メソッドリーダーボード](https://champollion.dev/leaderboard)** — スコアを提出し、メソッドを比較する
- **[MT 評価](/docs/leaderboard/rules)** — 良いメソッドの条件と失格になる条件
- **[評価ハーネス](/docs/specifications/harness)** — 実験の実行方法
- **[評価データセット](/docs/leaderboard/datasets)** — EDTeKLA Dev v1 と FLORES+
- **[コーチングデータ](https://champollion.dev/docs/concepts/coaching-data)** — LLM のための言語知識の構造化方法
- **[スクリプトコンバーター](https://champollion.dev/docs/concepts/script-converters)** — SRO→シラビクスパイプライン
- **[API によるメソッドの提供](https://champollion.dev/docs/guides/serving-a-method)** — コミュニティ管理の翻訳のホスティング
- **[ALTLab](https://altlab.artsrn.ualberta.ca/)** — Alberta Language Technology Lab
- **[EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/)** — Educational Technology, Knowledge & Language 研究グループ
- **[itwêwina 辞書](https://itwewina.altlab.app/)** — FST を活用した Plains Cree–英語辞書