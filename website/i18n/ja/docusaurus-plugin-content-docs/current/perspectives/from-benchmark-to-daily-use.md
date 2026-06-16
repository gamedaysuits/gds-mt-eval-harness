---
sidebar_position: 3
title: "ベンチマークから日常利用へ：ポストエディットの道筋"
slug: '/perspectives/from-benchmark-to-daily-use'
description: "ベンチマーク評価済みの翻訳手法がコミュニティ翻訳ワークフローへと発展するまでの流れを解説します。機械翻訳による下訳、流暢な話者によるポストエディット、そして公開テキストへ——各ステップで明確な品質基準を設けています。"
related:
  - label: "Deploy to Production"
    to: /docs/getting-started/deploy-to-production
    kind: guide
    note: "From proven method to live translation"
  - label: "Cookbook: Partial Translation (Human + Machine)"
    to: /docs/tutorials/partial-translation
    kind: cookbook
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "The quality thresholds behind the path"
  - label: "Translation Is Not Revitalization"
    to: /docs/perspectives/translation-is-not-revitalization
    kind: position
---
# ベンチマークから日常利用へ：ポストエディットという道筋

> **要点。** リーダーボードのスコアは製品ではありません。「このメソッドのスコアは0.78だ」から「バンドオフィスが毎週その言語で文書を公開している」に至る道筋は、ただ一つのワークフローを通ります。機械がドラフトを生成し、流暢な話者がそれを修正し、修正済みのテキストだけが公開される、というものです。私たちの仕様におけるすべての品質閾値は、このワークフローを基準に設定されています。監督なしの機械出力を基準にしているのではありません。本プラットフォームに掲載されているいかなる言語においても、監督なしの機械出力を推奨しません。

「翻訳メソッドはいつ『そのまま使えるほど十分』になるのか」と問われることがあります。このArenaが対象とする言語においては、その問いには落とし穴があります。正直に答えるなら、目指すべき基準は「レビューなしで公開できるほど十分」ではなく、**「ドラフトをレビューする方がゼロから翻訳するより効率的になるほど十分」**です。この基準ははるかに低く、測定可能であり、それを超えることでコミュニティの翻訳オフィスが一週間に生産できる成果が変わります。

---

## ワークフロー全体像

```
 English source document
        │
        ▼
 Machine draft  ←  a benchmarked, community-owned method
        │
        ▼
 Fluent-speaker post-edit  ←  the human gate; nothing skips it
        │
        ▼
 Published text  ←  carries human approval, not a machine score
        │
        ▼
 (Optional, community-controlled) corrections become
 data that improves the next version of the method
```

注目すべき点が三つあります。

1. **機械は公開しません。** 出力の単位はドラフトです。話者による修正作業は、最後に付け足す品質保証ではなく、ワークフローそのものです。
2. **最適化すべきリソースは話者の時間です。** あるメソッドが別のメソッドより優れているのは、まさに話者が修正すべき箇所を少なくする限りにおいてです。リソースが豊富な言語におけるポストエディットの研究では、中程度のMT品質であればゼロから翻訳するより速いという結果が一貫して示されています（Plitt & Masselot 2010; Green, Heer & Manning 2013、いずれも[Translation Is Not Revitalization](/docs/perspectives/translation-is-not-revitalization)にリンク付きで引用）。これが多合成語的な言語にも当てはまるかどうかを検証するためにこそ、このベンチマークが存在します。私たちはそれを前提ではなく、言語ごとに検証すべき仮説として扱っています。
3. **フィードバックループはコミュニティが所有します。** 修正済みの文書はすべて、訓練データやコーチングデータとなり得ます。そしてそれはコミュニティに帰属し、[データ主権](/docs/sovereignty/data-sovereignty)のルールのもと、コミュニティ自身の判断でフィードバックするかどうかを決めます。フィードバック機構はプラットフォームの設計目標であり、まだ実装された機能ではありません。修正と出所がどのように機能する予定かについては、[Reporting Errors and Owning Corrections](/docs/perspectives/reporting-errors-and-owning-corrections)をご覧ください。

## 品質ティアが実際の利用に意味すること

リーダーボードは自動化メトリクスの複合スコアでメソッドを評価し（[Scoring Specification](/docs/specifications/scoring)）、スコアは名称付きのティアに対応します。以下は、それらのティアを日常利用の観点から正直に解説したものです。

| ティア（複合スコア） | ポストエディットの道筋における意味 |
|---|---|
| **Baseline**（0.00–0.30） | いかなる用途にも使用不可。出力の大部分がターゲット言語になっていません。研究上の下限値としてのみ有用です。 |
| **Emerging**（0.30–0.50） | まだドラフト作成ツールとしては使えません。正しい断片は現れますが、話者がゼロから書くより修正に時間がかかります。 |
| **Functional**（0.50–0.70） | 平易なテキストに限り、ポストエディットがゼロからの翻訳を*上回る可能性*がある最初のティアです。話者と試験運用する価値はありますが、依存するには早計です。形態論的な誤りが頻繁に残ります。 |
| **Deployable**（0.70–0.85） | 上記ワークフローの目標ティアです。形態論の大部分が正確で、流暢な話者が再翻訳より明らかに速く修正できるドラフトが得られます。**「Deployable」とはポストエディットワークフローへの*投入*が可能という意味であり、「レビューなしで公開可能」という意味では決してありません。** |
| **Fluent**（0.85–1.00） | 有能な人間の翻訳に近づいており、誤りはまれで軽微です。レビュー作業は残りますが、より速くなります。 |

この表の上に、[Benchmark Specification §5 および §7](/docs/specifications/benchmark#5-quality-tiers)から直接導かれる、構造的な誠実さに関する二つのルールがあります。

- **自動化ティアは暫定的なラベルであり、最終判定ではありません。** それらは人間によるレビューへの推薦です。閾値は話者による検証データが蓄積されるにつれて再調整され、言語によって異なる結果になる可能性があります。
- **コミュニティレビューなしにDeployable以上を主張できるメソッドはありません。** 出力の層化サンプルがバイリンガルの話者に送られ、各翻訳を*reject / gist / acceptable / excellent*で評価します。メソッドが昇格するかどうかを決定するのは、リーダーボードではなくガバナンス組織です。

参考として、[Founder's Prize](/docs/specifications/prizes)の閾値（複合スコア ≥ 0.80、形態論的に有効な語が ≥ 99%、話者評価でacceptable以上が ≥ 70%）は、残存する誤りが*実際の言語上の誤り*（架空の語形ではなく、誤った活用形）であるメソッドを表しています。「話者の時間に値するドラフト」を数値で表すとこうなります。

## 優勝メソッドから機能するオフィスへ

あるメソッドがこれらの関門を通過したとします。残りのステップは組織的なものであり、即興ではなく仕様として定められています。

1. **所有権が移転します。** メソッドのコードはコミュニティのガバナンス組織の財産となります。開発者は帰属表示と公開の権利を保持します（[Ownership Transfer](/docs/sovereignty/ownership-transfer)）。
2. **メソッドはサービスになります。** プラグインとしてパッケージ化され、デプロイメントプラットフォームを通じて提供されます。コミュニティがアクセス、価格設定、許可される用途を管理します（[Deploy to Production](/docs/getting-started/deploy-to-production)）。
3. **翻訳者が日常業務に組み込みます。** 翻訳オフィスは既存の文書ワークフローをメソッドのAPIに接続します。ソーステキストを入力し、ドラフトを受け取り、ポストエディットして公開します。公開されたテキストには翻訳者の名前と権威が付与されます。機械は辞書と同様、翻訳者の手元にあるツールです。
4. **収益は利用に応じて生まれます。** メソッドを利用する外部の開発者は従量制の料金を支払い、その収益の90%がガバナンス組織に還元されます（[The Economic Model](/docs/sovereignty/economic-model)）。これにより翻訳者の稼働時間を増やす資金が生まれ、ループが閉じます。

## 現状について

率直に申し上げます。全体の道筋は端から端まで仕様として定められており、部分的に構築されています。評価ハーネス、メトリクス、実行カード、公開リーダーボードは存在します。Plains Creeの開発コーパスとアクティブなプライズも存在します。デプロイメントプラットフォームも存在します。コミュニティレビューインターフェース、評価サンドボックス、修正済みテキストのフィードバックループは仕様として定められていますが、まだ稼働していません。仕様書ではそれらを「計画中」と明記しており、私たちも同様に明記します。ベンチマークから日常的なコミュニティ利用まで、全行程を完了したメソッドはまだ存在しません。その行程こそがこのプロジェクトの成功の定義であり、だからこそ私たちは早まってそれを主張しません。

---

## あなたにとっての意味

:::info コミュニティメンバーの方へ
リーダーボードの「Deployable」バッジは、機械があなたの言語で監督なしに公開するという意味では決してありません。ドラフト生成ツールが、あなたの翻訳者に対して、あなたの条件で、あなたの話者を審査員として（有償で——[How Speakers Get Paid](/docs/perspectives/how-speakers-get-paid)参照）*オーディション*を受ける準備ができているかもしれない、という意味です。コミュニティが翻訳オフィスを運営している場合、私たちに持ちかけるべき問いは「パイロットはどのような形になるか、誰が出力をレビューするか」です。
:::

:::info 研究者の方へ
ポストエディットという枠組みは、何を測定する価値があるかを変えます。複合スコアだけでなく、話者がループに入った状態での許容可能なテキストへの到達時間が重要です。Arenaのメトリクスはその代理指標です（[Scoring Specification §1](/docs/specifications/scoring)）。形態論的に複雑な言語における言語ごとのポストエディット研究は、このインフラが支援するために設計されたオープンな研究上の空白です。
:::

:::info 開発者の方へ
メトリクスではなく、編集者のために最適化してください。実在する語を生成しつつ時折誤った活用形を含むメソッドは、話者が数秒で修正できます。一方、もっともらしい語形を幻覚するメソッドはワークフロー全体を汚染します。だからこそ、ここでは形態論的妥当性が厳しく管理されています。[Submit a Method](/docs/getting-started/submit-a-method)から始め、優勝した場合に引き渡すものについては[Method Interface](/docs/specifications/methods)をお読みください。
:::

## 関連情報

- [Translation Is Not Revitalization](/docs/perspectives/translation-is-not-revitalization) — 人間による関門が制約ではなく本質である理由
- [Reporting Errors and Owning Corrections](/docs/perspectives/reporting-errors-and-owning-corrections) — 公開されたテキストに誤りがあった場合の対処
- [Benchmark Specification §7](/docs/specifications/benchmark#7-human-validation) — 人間による検証の関門（正式仕様）