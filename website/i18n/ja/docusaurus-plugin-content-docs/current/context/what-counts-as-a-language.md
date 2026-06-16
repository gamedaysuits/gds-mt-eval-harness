---
sidebar_position: 2
title: "ここでは何が言語としてカウントされますか？"
---
# ここでは何を「言語」と見なすか？

> **要旨。** Arena は ISO 639-3 によって言語を分類し、マクロ言語の傘ではなく個別言語を対象にベンチマークを行います。手話をそれが本来そうであるような自然言語として含め、ISO が認定する人工言語を含め、プログラミング言語を除外し、分類上の論争については立場を取らずに表示します。このページでは各選択の理由とリーダーボードへの影響を説明します。

数千の言語にわたる翻訳をベンチマークするプロジェクトは、古くから答えの難しい問いに向き合わなければなりません。「言語」とは何か、という問いです。言語学者はずっと以前から、「言語」と「方言」の境界は構造的なものである以上に社会的・政治的なものだと認識してきました。*「言語とは軍隊と海軍を持つ方言である」* という有名な言葉は、イディッシュ語の言語学者 Max Weinreich が 1945 年に広めたものです（彼自身は自分の講演の聴衆の一人から聞いたと述べています）。この問いを避けることはできないため、私たちの答えとその根拠を以下に示します。

---

## 手話は言語である。それ以上でも以下でもない。

手話は自然言語です。完全な文法を持ち、子どもが母語として習得し、生きた言語共同体を持っています。このことは、William Stokoe が 1960 年にアメリカ手話（ASL）が音声言語と同種の内部構造を持つことを示して以来、言語学において決着のついた問題であり、その後 60 年にわたる研究（Klima & Bellugi 1979; Sandler & Lillo-Martin 2006）によってさらに深く裏付けられています。ISO 639-3 は手話に個別の言語コードを割り当てており、Glottolog は手話を音声言語の系統と並べて分類しています。私たちのカタログには 160 以上の手話が含まれており、`modality: signed` のタグが付いています。

その中には、危機に瀕した先住民言語も含まれます。北米全域でかつて部族間の主要な共通語として機能していた Plains Indian Sign Language（`psd`）は、今日では深刻な危機状態にあります（Davis 2010, *Hand Talk*）。手話の消滅は先住民言語の消滅であり、このプロジェクトの使命の範囲内にある問題です。

**スコープに関する正直な注記。** Arena が現在ベンチマークしているのは*テキストベース*の機械翻訳です。手話の機械翻訳——映像、空間文法、広く普及した書記形式を持たない言語を扱うこと——は、異なる、そしていまだ大部分が未解決の技術的問題です（Yin et al. 2021, "Including Signed Languages in Natural Language Processing," ACL を参照）。私たちはまだそれを提供していません。カタログ内の手話エントリにはそのことが明記されています。**未対応（not yet served）——「言語ではない（not a language）」では決してありません。**

## モダリティは二つある。書記はその一つではない。

言語には二つの主要なモダリティがあります。**音声**と**手話**です。書記は第三のモダリティではありません。書記は言語の上に重ねられた技術であり、世界の言語の大部分は標準化された書記体系なしに存在しています。そのため、私たちの言語カードでは書記を別途記録しています（その言語が使用する文字体系、あるいは標準化された正書法を持たないかどうか）。そして正直に記録しています。テキストベースの機械翻訳プラットフォームにとって、ある言語が書かれているかどうかは脚注ではなく重要な情報です。そして書記を持たない言語は、劣った言語ではありません。

## 人工言語：含む。プログラミング言語：除く。

私たちは ISO 639-3 自身の基準に従います。この規格が人工言語を認定するのは、それが完全な言語であり、人間のコミュニケーションのために設計され、文学を持ち、第二世代のユーザーに受け継がれたコミュニティを持つ場合に限られます。そしてコンピュータのプログラミング言語は明示的に除外されています。母語話者を持つ Esperanto は条件を満たしますが、Python は満たしません。誰も Python を親から第一言語として習得しないからです。私たちのカタログには ISO が認定する約 24 の人工言語が含まれており、そのように分類されています。プログラミング言語は含まれません。

## ベンチマークの単位は個別言語であり、傘カテゴリではない

ISO 639-3 は*個別言語*と*マクロ言語*を区別しています。マクロ言語とは、`cre`（クリー語）、`ara`（アラビア語）、`zho`（中国語）のように、密接に関連する複数の個別言語をまとめた傘コードです。Arena のベンチマーク単位は**個別言語**です。その理由は実用的なものです。翻訳リソースは変種ごとに固有のものだからです。Plains Cree（`crk`）向けに構築された形態素解析器は Moose Cree（`crm`）を処理できません。エジプト・アラビア語のコーパスは、モロッコ・アラビア語における手法の品質についてほとんど何も語りません。マクロ言語コードに紐付けられたスコアは、実際には評価されていない変種についての主張になってしまいます。そのため、私たちはそれを行いません。

マクロ言語はカタログ内に**ハブページ**として引き続き表示されます。傘としてのアイデンティティをその個別メンバーにリンクするナビゲーションであり、両レベルのアイデンティティが実在するという ISO 自身の見解を反映しています。個別言語の下位には、Glottolog の languoid ツリー（Hammarström & Forkel 2022）から方言および系統情報を表示します。このツリーは語族、言語、方言を一つのナビゲート可能な階層として構造化しています。

## 権威ある機関の見解が異なる場合は、両方を示す

ISO 639-3 と Glottolog は分割・統合の判断が異なる場合があり、コミュニティが両者と異なる見解を持つこともあります。私たちはどちらが正しいかを裁定しません。言語カードには*分類に関する注記*の欄があり、出典とともに見解の相違を表示します。名称については、コミュニティが選好を表明している場合はそれに従います。ある変種が「言語」であるかどうかは、最終的にはアイデンティティの問題でもあります。そしてアイデンティティに関する問いはコミュニティ自身に帰属するという原則を、私たちは OCAP® のような先住民データガバナンスの枠組みから採用しています。

## 研究の方向性：ベンチマークを測定手段として

このような Arena が副産物としてもたらすものの一つは、言語変種が*実用上*どれほど近いかについての新たな種類の証拠です。一つの翻訳手法を固定したまま複数の関連変種に対して実用的な品質を達成できるなら、それらの変種は実用上クラスターを形成しています。逆に、別々のコーパスと別々の手法を必要とするなら、命名の政治がどうあれ、それらは実用上異なるものです。これは、録音テキストによる了解度テストから自動語彙距離測定まで、従来の実証的な伝統に似ており、デプロイメントに根ざした視点が加わっています。

私たちはこれを、主張としてではなく研究の方向性として慎重に提示します。手法の転用結果はコーパスサイズ、ドメイン、正書法、訓練データの汚染によって交絡しており、クラスタリングは常に特定の手法と品質閾値に相対的なものです。何より重要なのは、このシグナルは言語と方言に関する議論を*補完する*ことはできますが、コミュニティ自身が自らの言語をどのように認識するかを決して上書きするものではないということです。

---

## 参考文献

- Davis, Jeffrey E. (2010). *Hand Talk: Sign Language among American Indian Nations.* Cambridge University Press.
- Dryer, Matthew S. & Martin Haspelmath, eds. (2013). *The World Atlas of Language Structures Online.* https://wals.info
- Hammarström, Harald & Robert Forkel (2022). "Glottocodes: Identifiers Linking Families, Languages and Dialects to Comprehensive Reference Information." *Semantic Web* 13(6).
- Haugen, Einar (1966). "Dialect, Language, Nation." *American Anthropologist* 68(4).
- ISO 639-3 Registration Authority. "Scope of denotation" and "Types of individual languages." https://iso639-3.sil.org/about/scope · https://iso639-3.sil.org/about/types
- Klima, Edward S. & Ursula Bellugi (1979). *The Signs of Language.* Harvard University Press.
- Sandler, Wendy & Diane Lillo-Martin (2006). *Sign Language and Linguistic Universals.* Cambridge University Press.
- Stokoe, William C. (1960). *Sign Language Structure.* Studies in Linguistics, Occasional Papers 8.
- Weinreich, Max (1945). "Der YIVO un di problemen fun undzer tsayt." *YIVO Bleter* 25(1).
- Yin, Kayo, Amit Moryossef, Julie Hochgesang, Yoav Goldberg & Malihe Alikhani (2021). "Including Signed Languages in Natural Language Processing." *Proc. ACL-IJCNLP 2021.* https://aclanthology.org/2021.acl-long.570/
- First Nations Information Governance Centre. *The First Nations Principles of OCAP®.* https://fnigc.ca/ocap-training/