---
sidebar_position: 7
title: "統計的有意性検定"
slug: '/specifications/significance'
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "The scores these tests protect"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "Where significance gates what ranks"
---
# 統計的有意性検定 — 実装仕様

> **対象コードベース**: `arena`（特に `tester.py` および `compare.py`）
> **目的**: 2つの評価実行間の差異が統計的に有意なのか、それとも単なるノイズなのかを研究者が判断できるようにする。
> **優先度**: 高 — 発表可能な結果を得るために最も重要な未実装機能です。

---

## なぜこれが重要か

2つの実行結果を比較する場合（例：92件のエントリに対して Gemini 3.1 Pro の chrF++ が 42.96、Claude Sonnet の chrF++ が 41.80）、現状ではその差が実質的なものかノイズかを判断できません。テストエントリが約92件しかない場合、ランダムな変動によって1〜2ポイントの差が容易に生じます。専門家は有意性検定を求めるでしょう。それに答えられる必要があります。

---

## アルゴリズム：ペアードブートストラップリサンプリング

これは SacreBLEU、MT-Lens、および WMT shared task で使用されている標準的な手法です。MT 研究者にとって広く理解されており、信頼性の高い結果をもたらします。

### 仕組み

同一の N 件のテストエントリで評価された2つのシステム A と B が与えられた場合：

1. 実際のメトリクス差を計算する：`Δ = metric(A) - metric(B)`
2. `n_bootstrap` 回繰り返す（デフォルト 1000）：
   a. 共有テストセットから N 件のエントリを**復元抽出**でサンプリングする
   b. このブートストラップサンプルに対して A と B 両方のメトリクスを計算する
   c. ブートストラップ差を計算する：`Δ_boot = metric(A_boot) - metric(B_boot)`
3. p 値 = `Δ_boot` の符号が `Δ` と逆になるブートストラップサンプルの割合
4. p 値 < α（デフォルト 0.05）であれば、差は統計的に有意

### 主な特性

- **ペアード**：両システムを同一のブートストラップサンプルで評価することで、エントリレベルの相関を保持する
- **ノンパラメトリック**：スコアの分布に関する仮定を必要としない
- **標準的**：これは `sacrebleu --paired-bs` が内部で行っていることと全く同じ手法

---

## 重要：sacrebleu は必須依存関係

sacrebleu は現在 `[project.optional-dependencies]` に列挙されており、`tester.py` 内で `try/except` によってガードされています。**これは変更すべきです。** chrF++ や BLEU を計算できない MT 評価ハーネスは、MT 評価ハーネスとは言えません。sacrebleu は以下のようにすべきです：

1. `pyproject.toml` 内の `[project.dependencies]` に移動する
2. `tester.py` で直接インポートする（`try/except HAS_SACREBLEU` ガードを削除する）
3. 新しい `significance.py` モジュールで直接インポートする

`tester.py` 内の `HAS_SACREBLEU` 条件分岐パスは削除すべきです — サポートすべきでないシナリオ（sacrebleu なしでの実行）のためにコードが複雑になっています。

---

## 実装計画

### 1. sacrebleu を必須依存関係に昇格させる

**`pyproject.toml`**：`sacrebleu>=2.3` を `[project.optional-dependencies].metrics` から `[project.dependencies]` に移動する。

**`tester.py`**：以下を置き換える：
```python
# Optional: sacrebleu for chrF++ and BLEU
try:
    from sacrebleu.metrics import CHRF, BLEU
    HAS_SACREBLEU = True
except ImportError:
    HAS_SACREBLEU = False
```
以下に変更する：
```python
from sacrebleu.metrics import CHRF, BLEU
```

`tester.py` 全体から `if HAS_SACREBLEU:` ガードをすべて削除する。

---

### 2. 新規モジュール：`mt_eval_harness/significance.py`

```python
"""
Statistical significance testing via paired bootstrap resampling.

Standard method used by WMT shared tasks, SacreBLEU, and MT-Lens.
Compares two runs on the same corpus to determine if the performance
difference is statistically significant.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from sacrebleu.metrics import CHRF, BLEU


@dataclass
class SignificanceResult:
    """Result of a paired bootstrap significance test."""
    metric_name: str           # e.g., "corpus_chrf", "exact_match_rate"
    system_a_score: float      # Score for system A
    system_b_score: float      # Score for system B
    delta: float               # A - B
    p_value: float             # Two-sided p-value
    n_bootstrap: int           # Number of bootstrap iterations
    confidence_level: float    # 1 - alpha
    significant: bool          # p_value < alpha
    winner: str | None         # "A", "B", or None if not significant
    ci_lower: float            # Lower bound of 95% CI on the delta
    ci_upper: float            # Upper bound of 95% CI on the delta


def paired_bootstrap(
    entries_a: list[dict],
    entries_b: list[dict],
    metric_fn: callable,
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    seed: int = 12345,
    metric_name: str = "metric",
) -> SignificanceResult:
    """Run paired bootstrap resampling significance test.

    Args:
        entries_a: Per-entry results from system A (from TestReport["entries"])
        entries_b: Per-entry results from system B (must be same length, same IDs)
        metric_fn: Function(list[dict]) -> float that computes the corpus-level
                   metric from a list of entry dicts. Must handle the entry format
                   from TestReport.
        n_bootstrap: Number of bootstrap iterations (1000 is standard)
        alpha: Significance level (0.05 = 95% confidence)
        seed: RNG seed for reproducibility (12345 matches SacreBLEU default)
        metric_name: Human-readable name for the metric being tested

    Returns:
        SignificanceResult with all fields populated.

    Raises:
        ValueError: If entries_a and entries_b have different lengths or IDs.
    """
    ...
```

### 3. 組み込みメトリクス関数

```python
def exact_match_rate(entries: list[dict]) -> float:
    """Compute exact match rate from a list of entry dicts."""
    non_error = [e for e in entries if not e.get("error")]
    if not non_error:
        return 0.0
    exact = sum(1 for e in non_error if e.get("exact_match"))
    return exact / len(non_error)


def corpus_chrf(entries: list[dict]) -> float:
    """Compute corpus-level chrF++ from a list of entry dicts."""
    chrf = CHRF(word_order=2)
    refs = [e["expected"] for e in entries if e.get("expected", "").strip()]
    hyps = [e["predicted"] if e.get("predicted", "").strip() else "EMPTY"
            for e in entries if e.get("expected", "").strip()]
    if not refs:
        return 0.0
    return chrf.corpus_score(hyps, [refs]).score


def corpus_bleu(entries: list[dict]) -> float:
    """Compute corpus-level BLEU from a list of entry dicts."""
    bleu = BLEU()
    refs = [e["expected"] for e in entries if e.get("expected", "").strip()]
    hyps = [e["predicted"] if e.get("predicted", "").strip() else "EMPTY"
            for e in entries if e.get("expected", "").strip()]
    if not refs:
        return 0.0
    return bleu.corpus_score(hyps, [refs]).score
```

### 4. `compare.py` への統合

既存の `compare.py` はすでに複数の TestReport を並べて比較しています。有意性検定を追加します：

```python
# In compare_reports(), after computing deltas:
if len(reports) == 2:
    sig_results = run_significance_tests(reports[0], reports[1])
    comparison["significance"] = [asdict(r) for r in sig_results]
```

3つ以上のレポートを比較する場合は、すべてのペアに対してペアワイズ有意性検定を実行します。結果は `"(run_a_id, run_b_id)"` をキーとして格納します。

### 5. CLI への統合

`mt-eval compare` に `--significance` フラグを追加する：

```bash
# Compare two runs with significance testing
mt-eval compare report_a.json report_b.json --significance

# Custom bootstrap count
mt-eval compare report_a.json report_b.json --significance --n-bootstrap 5000
```

スタンドアロンコマンドも検討する：

```bash
# Quick significance check between two reports
mt-eval significance report_a.json report_b.json
```

### 6. 出力フォーマット

**コンソール出力：**
```
  Significance Tests (paired bootstrap, n=1000, α=0.05):

  Metric              A         B       Δ      p-value  Sig?
  ─────────────────── ──────── ──────── ─────── ──────── ────
  corpus_chrf         42.96    41.80    +1.16   0.142    No
  exact_match_rate     0.198    0.185   +0.013  0.381    No
  corpus_bleu          6.80     3.81    +2.99   0.018    Yes *
```

**JSON 出力**（比較レポートに追加）：
```json
{
  "significance": [
    {
      "metric_name": "corpus_chrf",
      "system_a_score": 42.96,
      "system_b_score": 41.80,
      "delta": 1.16,
      "p_value": 0.142,
      "n_bootstrap": 1000,
      "confidence_level": 0.95,
      "significant": false,
      "winner": null,
      "ci_lower": -0.85,
      "ci_upper": 3.12
    }
  ]
}
```

### 7. ダッシュボードへの統合

比較 JSON に有意性データが含まれている場合、ダッシュボードはそれを表示すべきです。比較テーブルに有意性インジケーターの行を表示します（例：p < 0.05 の場合は `*`、p < 0.01 の場合は `**`）。これは nice-to-have であり、ブロッカーではありません。

---

## エッジケースとバリデーション

1. **エントリの不一致**：2つの TestReport は同一のエントリ ID を持つ必要があります。そうでない場合（例：一方がサブセットで実行された場合）、共通部分のみで有意性を検定します。除外されたエントリについて警告を出します。

2. **エントリ数が少なすぎる場合**：N < 10 の場合、エントリ数が少なすぎるため有意性検定の信頼性が低い旨を警告します。それでも検定は実行しますが、警告を表示します。

3. **スコアが同一の場合**：両システムがエントリごとに同一の結果を出す場合、p_value は 1.0 になるべきです（差がまったくない）。

4. **プラグインメトリクス**：有意性モジュールは、両方のレポートに存在するプラグインメトリクスについても検定すべきです。汎用的なアプローチを使用します：両レポートに `plugin_metrics.crk_fst_validity.avg_fst_validity` が存在する場合は検定します。

5. **再現性**：RNG シードは出力にログとして記録し、結果を完全に再現できるようにする必要があります。デフォルトは 12345（SacreBLEU の慣例に合わせる）。

---

## 実装しないこと

- **COMET の個別有意性検定は不要**：COMET は現在 `metrics_comet.py` 経由でコーパスレベルのメトリクスとして統合されています。ブートストラップ信頼区間は chrF++/BLEU と同様に COMET スコアに対して計算されます。2つのシステム間のペアワイズ COMET 有意性検定には、Unbabel の `comet-compare` を使用してください。
- **ベイズ分析は不要**：頻度論的ブートストラップに留めます。MT コミュニティが期待し、理解している手法です。
- **多重検定補正は不要**：複数のメトリクスを検定する場合、Bonferroni 補正などは適用しません。MT 評価の慣例では、メトリクスごとの生の p 値を報告し、解釈は読者に委ねます。

---

## 変更対象ファイル

| ファイル | 変更内容 |
|---|---|
| `pyproject.toml` | sacrebleu をオプションから必須依存関係に移動 |
| `mt_eval_harness/tester.py` | `HAS_SACREBLEU` ガードを削除し、直接インポートに変更 |
| `mt_eval_harness/significance.py` | **[新規]** コア実装 |
| `mt_eval_harness/__init__.py` | `SignificanceResult`、`paired_bootstrap` をエクスポート |
| `mt_eval_harness/compare.py` | レポート比較に有意性検定を組み込む |
| `mt_eval_harness/cli.py` | `--significance` および `--n-bootstrap` フラグを追加 |
| `mt_eval_harness/dashboard.py` | 比較テーブルに有意性を表示（nice-to-have） |
| `tests/test_significance.py` | **[新規]** ユニットテスト |

---

## テスト要件

1. **シードによる決定論的動作**：同一の入力 + 同一のシード = 毎回同一の p 値
2. **既知の答えによるテスト**：2つの同一の結果セット → p_value = 1.0
3. **既知の有意差テスト**：一方が明らかに優れている2つの結果セットを構築する（例：すべて完全一致 vs すべて不一致）→ p_value ≈ 0.0
4. **ID の不一致**：ValueError を発生させるか、警告を出して共通部分で計算すべき
5. **空の入力**：適切に処理すること（p_value = 1.0 を返すか、例外を発生させる）

---

## 信頼区間（付随機能）

> **ステータス**：✅ `confidence.py` に実装済み

信頼区間（CI）は有意性検定とは異なる問いに答えます：

- **有意性検定**（`significance.py`）：「システム A とシステム B の差は実質的なものか？」
- **信頼区間**（`confidence.py`）：「このシステム単体のスコアはどの程度不確かか？」

### 実装：`confidence.py`

有意性検定と同じパーセンタイルブートストラップリサンプリング手法を使用します：

| パラメータ | 値 | 根拠 |
|---|---|---|
| `n_bootstrap` | 1000 | SacreBLEU のデフォルト、WMT 2024 の慣例 |
| `seed` | 12345 | 再現性のための SacreBLEU デフォルトシード |
| `alpha` | 0.05 | 標準的な 95% 信頼水準 |
| Method | Percentile bootstrap | Koehn (2004)、Efron (1979) |

### 信頼区間が計算されるもの

ハーネスが計算するすべてのコーパスレベルメトリクス：
- `corpus_chrf`（chrF++ スコア）
- `corpus_bleu`（BLEU スコア）
- `exact_match_rate`（0.0〜1.0）

### CLI フラグ

```bash
# Default: CIs are computed automatically
mt-eval test run_log.json

# Skip CI computation (faster, for quick iteration)
mt-eval test run_log.json --no-ci

# More bootstrap iterations (more precise, slower)
mt-eval test run_log.json --n-bootstrap-ci 2000
```

### 少数サンプルの警告

N < 30 件のエントリの場合、モジュールは信頼区間のカバレッジが不十分になる可能性がある旨の警告を出します。ブートストラップはサンプルに存在しない情報を生み出すことはできません — エントリ数が非常に少ない場合、区間は広くなりますが、これは高い不確実性を正しく反映しています。

### COMET の統合

COMET（`metrics_comet.py`）はファーストクラスのメトリクスとして統合されています：
- モデル：`Unbabel/wmt22-comet-da`（WMT 2022 優勝の参照ベースモデル）
- `unbabel-comet` がインストールされている場合に自動計算
- エントリごとのスコアが TestReport エントリに格納される
- XLM-R カバレッジテーブルによる低リソース言語の検出
- オプション依存関係：`pip install mt-eval-harness[comet]`

### Supabase マイグレーション

`run_cards` テーブルに追加された新しいカラム：
- `comet_score`（FLOAT8、nullable）
- `corpus_bleu`（FLOAT8、nullable）
- `chrf_ci_lower` / `chrf_ci_upper`（FLOAT8、nullable）
- `exact_match_ci_lower` / `exact_match_ci_upper`（FLOAT8、nullable）

マイグレーションスクリプトについては `migrations/001_add_comet_and_ci_columns.sql` を参照してください。