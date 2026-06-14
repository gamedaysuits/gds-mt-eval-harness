"""Anti-collision spread for the community compute queue.

The public queue is a static, ranked JSON file with no claim-locking. When
many contributors run the donate flow (`mt-eval queue --budget`) at the same
moment, strict top-order selection hands every worker the identical items —
wasting donated compute on redundant runs of one (model, corpus) pair. The
spread layer (`_spread_order`) gives each worker a priority-weighted random
permutation so simultaneous workers fan out across the queue.

These tests pin three properties:
  1. Default (spread=False) behavior is byte-for-byte the old top-order
     selection — the shared selection vectors and the JS port depend on it.
  2. Spread still favors high-priority items (they run most often).
  3. Under mass concurrency, no single item is dogpiled ~100×.
"""

from __future__ import annotations

import random
from collections import Counter

from mt_eval_harness.queue_runner import SPREAD_DECAY, _spread_order, select_items


def _queue(n: int, cost: float | None = 0.10):
    return {
        "items": [
            {
                "id": f"i{k:04d}",
                "condition": "naive",
                "est_cost_usd": cost,
                "language_pair": "eng>fao",
                "model": "m",
                "run_command": "true",
            }
            for k in range(n)
        ]
    }


class TestSpreadDefaultUnchanged:
    """spread=False must reproduce the existing top-order selection exactly."""

    def test_top_default_is_strict_order(self):
        q = _queue(20)
        sel, _ = select_items(q, top=5)
        assert [i["id"] for i in sel] == [f"i{k:04d}" for k in range(5)]

    def test_explicit_no_spread_matches_default(self):
        q = _queue(20)
        a, _ = select_items(q, top=5)
        b, _ = select_items(q, top=5, spread=False)
        assert [i["id"] for i in a] == [i["id"] for i in b]

    def test_budget_default_is_strict_order(self):
        # cost 0.10 each, budget 0.35 -> first 3 items, in order.
        q = _queue(20)
        sel, _ = select_items(q, budget=0.35)
        assert [i["id"] for i in sel] == ["i0000", "i0001", "i0002"]


class TestSpreadReproducible:
    def test_same_seed_same_order(self):
        q = _queue(200)
        o1 = _spread_order(list(q["items"]), random.Random(42))
        o2 = _spread_order(list(q["items"]), random.Random(42))
        assert [i["id"] for i in o1] == [i["id"] for i in o2]

    def test_different_seeds_differ(self):
        q = _queue(200)
        o1 = _spread_order(list(q["items"]), random.Random(1))
        o2 = _spread_order(list(q["items"]), random.Random(2))
        assert [i["id"] for i in o1] != [i["id"] for i in o2]

    def test_permutation_preserves_membership(self):
        q = _queue(200)
        out = _spread_order(list(q["items"]), random.Random(7))
        assert sorted(i["id"] for i in out) == sorted(i["id"] for i in q["items"])
        assert len(out) == 200


class TestSpreadBudgetInvariant:
    def test_never_exceeds_budget_under_spread(self):
        # Mixed costs; spread on. Cumulative est must never exceed budget.
        items = []
        for k in range(300):
            items.append(
                {
                    "id": f"i{k:04d}",
                    "condition": "naive",
                    "est_cost_usd": 0.05 + (k % 5) * 0.05,  # 0.05..0.25
                    "language_pair": "eng>fao",
                    "model": "m",
                    "run_command": "true",
                }
            )
        q = {"items": items}
        for seed in range(20):
            sel, _ = select_items(
                q, budget=1.00, spread=True, rng=random.Random(seed)
            )
            total = sum(i["est_cost_usd"] for i in sel)
            assert total <= 1.00 + 1e-9, f"seed {seed}: spent {total}"


class TestSpreadFavorsPriority:
    def test_top_items_run_more_often(self):
        # Across many workers each taking 1 item, rank-0 should be selected
        # far more often than a deep-tail item — priority is preserved.
        q = _queue(1000)
        first_pick = Counter()
        for w in range(4000):
            sel, _ = select_items(q, top=1, spread=True, rng=random.Random(w))
            first_pick[sel[0]["id"]] += 1
        top_item = first_pick["i0000"]
        tail_item = first_pick["i0900"]
        assert top_item > tail_item, (top_item, tail_item)
        # The very top should be meaningfully favored.
        assert top_item > 3 * max(tail_item, 1)


class TestSpreadNoDogpile:
    def test_mass_concurrency_stays_under_100x(self):
        """1,000 workers each taking ~20 items must not dogpile one item ~100×.

        This is the founder's explicit worry: with 1,000 simultaneous
        contributors we must not run the same item ~100 times.
        """
        q = _queue(2002, cost=0.10)  # ~ real open_items count
        counts = Counter()
        workers = 1000
        for w in range(workers):
            # budget 2.00 / 0.10 = ~20 items per worker (19-20 with float
            # accumulation in the running-total comparison).
            sel, _ = select_items(
                q, budget=2.00, spread=True, rng=random.Random(10_000 + w)
            )
            assert len(sel) >= 18
            for it in sel:
                counts[it["id"]] += 1
        busiest = counts.most_common(1)[0]
        # ~19-20 items each across 1000 workers.
        assert sum(counts.values()) >= workers * 18
        # The busiest item must be well under 100 (vs. 1000 with no spread).
        assert busiest[1] < 100, f"busiest item {busiest} >= 100"

    def test_without_spread_everyone_collides(self):
        # Contrast: strict order -> all workers take the identical prefix.
        q = _queue(2002, cost=0.10)
        counts = Counter()
        for w in range(50):
            sel, _ = select_items(q, budget=2.00)  # spread defaults off here
            for it in sel:
                counts[it["id"]] += 1
        # Every worker took i0000..i0019 -> 50 collisions on each.
        assert counts["i0000"] == 50


def test_spread_decay_is_sane():
    assert SPREAD_DECAY > 0
