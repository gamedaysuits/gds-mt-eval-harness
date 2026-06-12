# Database Schema — Single Source of Truth

> [!IMPORTANT]
> This document is the **canonical reference** for the Champollion Supabase schema.
> All migration files, publish.py code, and leaderboard queries must conform to this spec.
> When in doubt, this document wins.

## Schema Locations (History)

The schema has historically been defined across three directories. This caused
conflicting table definitions and column mismatches. Going forward:

| Location | Role | Status |
|----------|------|--------|
| `mt-eval-arena/supabase/migrations/` | **CANONICAL** — all new migrations go here | ✅ Active |
| `arena/migrations/` | Mirror of 001–011 only (kept for old references) | 🏛️ Historical reference |
| `crk-translate/eval/supabase/001_create_run_cards.sql` | Original base table (dashboard-applied) | 🏛️ Historical reference |
| `cli/supabase/migrations/` | Legacy CLI migrations (dashboard-applied) | 🏛️ Historical reference |

### Migration Application Order

The full schema is the result of applying these in order:

```
1. crk-translate/eval/supabase/001_create_run_cards.sql    (base table)
2. cli/supabase/migrations/20260528023253_*.sql             (added 6 columns)
3. cli/supabase/migrations/20260528024953_*.sql             (added 4 columns, created datasets)
4. mt-eval-arena/supabase/migrations/001–017_*.sql          (columns, entries, contests,
                                                             datasets, trading cards, licenses,
                                                             RLS hardening, audit trail)
```

> [!CAUTION]
> The `datasets` table was created by CLI migration `20260528024953` with one schema,
> then arena migration `009` attempted to CREATE the same table with a different schema.
> Since `CREATE TABLE IF NOT EXISTS` is used, **whichever ran first wins**.
> The canonical schema is defined below. A reconciliation migration is included.

---

## Table: `run_cards`

The primary leaderboard table. Each row is one benchmark submission.

### Columns

| Column | Type | Nullable | Default | Source | Notes |
|--------|------|----------|---------|--------|-------|
| `id` | TEXT | NOT NULL | — | `publish.py` | SHA-256 hash, PRIMARY KEY |
| `submitter` | TEXT | NOT NULL | — | `publish.py` | Email from OAuth session |
| `affirmation` | TEXT | NOT NULL | — | `publish.py` | Auto-generated attestation |
| `submitted_at` | TIMESTAMPTZ | NOT NULL | `now()` | DB default | Auto-set on insert |
| `trust` | TEXT | NOT NULL | `'unverified'` | `publish.py` | **CHECK**: `('unverified', 'verified', 'disqualified')` |
| `model_slug` | TEXT | NOT NULL | — | `publish.py` | e.g. `"anthropic/claude-3.5-sonnet"` |
| `condition` | TEXT | NOT NULL | — | `publish.py` | e.g. `"en>crk+coaching"` |
| `dataset_id` | TEXT | NOT NULL | — | `publish.py` | FK-like ref to `datasets.id` |
| `language_pair` | TEXT | NOT NULL | — | `publish.py` | e.g. `"en>crk"` |
| `harness_version` | TEXT | NOT NULL | — | `publish.py` | Semver string |
| `chrf_plus_plus` | REAL | YES | — | `publish.py` | 0–100 scale |
| `exact_match_rate` | REAL | YES | — | `publish.py` | 0–100 percentage |
| `fst_acceptance_rate` | REAL | YES | — | `publish.py` | 0–100 percentage |
| `equivalent_match_rate` | REAL | YES | — | `publish.py` | 0–100 percentage |
| `semantic_score` | REAL | YES | — | `publish.py` | 0.0–1.0 |
| `composite_score` | REAL | YES | — | `publish.py` | 0.0–1.0 weighted composite |
| `quality_tier` | TEXT | YES | — | `publish.py` | LYSS tier label |
| `total_cost_usd` | REAL | YES | — | `publish.py` | Total API cost |
| `cost_per_entry_usd` | REAL | YES | — | `publish.py` | Per-entry cost |
| `elapsed_seconds` | REAL | YES | — | `publish.py` | Total wall time |
| `avg_latency_seconds` | REAL | YES | — | `publish.py` | Mean per-entry latency |
| `median_latency_seconds` | REAL | YES | — | `publish.py` | Median per-entry latency |
| `p95_latency_seconds` | REAL | YES | — | `publish.py` | 95th percentile latency |
| `corpus_size` | INTEGER | YES | — | `publish.py` | Number of entries evaluated |
| `run_card` | JSONB | NOT NULL | — | `publish.py` | Complete run card (source of truth) |
| `fingerprint_hash` | TEXT | NOT NULL | — | `publish.py` | Method+config identity hash |
| `api_provider` | TEXT | YES | `'openrouter'` | `publish.py` | e.g. `"openrouter"` |
| `run_timestamp` | TIMESTAMPTZ | YES | — | `publish.py` | When the run was executed |
| `batch_size` | INTEGER | YES | `25` | `publish.py` | API batch size |
| `temperature` | REAL | YES | `0` | `publish.py` | Sampling temperature |
| `max_tokens` | INTEGER | YES | — | `publish.py` | Max completion tokens |
| `comet_score` | FLOAT8 | YES | — | `publish.py` | COMET metric (if computed) |
| `corpus_bleu` | FLOAT8 | YES | — | `publish.py` | Corpus-level BLEU |
| `chrf_ci_lower` | FLOAT8 | YES | — | `publish.py` | chrF++ 95% CI lower bound |
| `chrf_ci_upper` | FLOAT8 | YES | — | `publish.py` | chrF++ 95% CI upper bound |
| `exact_match_ci_lower` | FLOAT8 | YES | — | `publish.py` | Exact match CI lower |
| `exact_match_ci_upper` | FLOAT8 | YES | — | `publish.py` | Exact match CI upper |
| `fst_ci_lower` | REAL | YES | — | `publish.py` | FST acceptance CI lower |
| `fst_ci_upper` | REAL | YES | — | `publish.py` | FST acceptance CI upper |
| `composite_ci_lower` | REAL | YES | — | `publish.py` | Composite CI lower |
| `composite_ci_upper` | REAL | YES | — | `publish.py` | Composite CI upper |
| `ter` | REAL | YES | — | `publish.py` | Translation Edit Rate |
| `length_ratio` | REAL | YES | — | `publish.py` | Avg predicted/reference length |
| `tokens_per_second` | REAL | YES | — | `publish.py` | Throughput metric |
| `entries_per_minute` | REAL | YES | — | `publish.py` | Throughput metric |
| `cost_per_source_char` | REAL | YES | — | `publish.py` | Cost normalized by source length |
| `tokens_per_entry` | REAL | YES | — | `publish.py` | Avg tokens per corpus entry |
| `cost_per_1k_tokens` | REAL | YES | — | `publish.py` | Cost per 1000 tokens |
| `code_switching_rate` | REAL | YES | — | `publish.py` | 0.0–1.0, lower is better |
| `hallucination_rate` | REAL | YES | — | `publish.py` | 0.0–1.0, lower is better |
| `terminology_adherence` | REAL | YES | — | `publish.py` | 0.0–1.0, higher is better |
| `style_consistency_rate` | REAL | YES | — | `publish.py` | 0.0–1.0, informational only |
| `method_class` | TEXT | YES | — | *unused* | Reserved for future method categorization |
| `corpus_license` | TEXT | YES | — | `publish.py` | Corpus SPDX-ish license from `arena/datasets/registry.json` (migration 015); NULL for unregistered datasets |
| `corpus_attribution` | TEXT | YES | — | `publish.py` | Corpus attribution string (migration 015); NULL for unregistered datasets |

### Constraints

```sql
PRIMARY KEY (id)
CHECK (trust IN ('unverified', 'verified', 'disqualified'))
```

### RLS Policies

| Policy | Operation | Rule | Rationale |
|--------|-----------|------|-----------|
| Public read | SELECT | `USING (true)` | Leaderboard is public |
| Anonymous insert | INSERT | `WITH CHECK (trust = 'unverified' AND id IS NOT NULL AND length(id) > 10)` | CLI submissions must be unverified |
| No update/delete | — | — | Submissions are immutable; admins use service_role |

### Indexes

```sql
idx_run_cards_leaderboard  ON (dataset_id, chrf_plus_plus DESC NULLS LAST)
idx_run_cards_model        ON (model_slug, dataset_id)
idx_run_cards_fingerprint  ON (fingerprint_hash)
idx_run_cards_comet_score  ON (comet_score DESC NULLS LAST)
idx_run_cards_composite    ON (composite_score DESC NULLS LAST)
idx_run_cards_method_class ON (method_class) WHERE method_class IS NOT NULL
```

#### `run_card_entries` Indexes

| Name | Columns | Type |
|------|---------|------|
| `idx_rce_run_card` | `run_card_id` | B-tree |
| `idx_rce_entry_id` | `entry_id` | B-tree |
| `idx_rce_fst_valid` | `fst_valid` | Partial (WHERE fst_valid IS NOT NULL) |
| `idx_rce_semantic` | `semantic_verdict` | Partial (WHERE semantic_verdict IS NOT NULL) |
| `idx_rce_code_switching` | `code_switching_detected` | Partial (WHERE = TRUE) |
| `idx_rce_hallucination` | `hallucination_detected` | Partial (WHERE = TRUE) |

#### `datasets` Indexes

| Name | Columns | Type |
|------|---------|------|
| `idx_datasets_language_pair` | `language_pair` | B-tree |

#### `contests` Indexes

| Name | Columns | Type |
|------|---------|------|
| `idx_contests_status` | `status` | B-tree |
| `idx_contests_language_pair` | `language_pair` | B-tree |

#### `contest_submissions` Indexes

| Name | Columns | Type |
|------|---------|------|
| `idx_cs_contest` | `contest_id` | B-tree |
| `idx_cs_run_card` | `run_card_id` | B-tree |

---

## Table: `run_card_entries`

Per-entry results for each run. Denormalized LYSS verdicts enable SQL filtering.

### Columns

| Column | Type | Nullable | Default | Source |
|--------|------|----------|---------|--------|
| `id` | BIGINT | NOT NULL | auto-increment | DB |
| `run_card_id` | TEXT | NOT NULL | — | FK to `run_cards.id` |
| `entry_id` | TEXT | NOT NULL | — | Corpus entry ID |
| `source` | TEXT | NOT NULL | — | Source text |
| `expected` | TEXT | NOT NULL | — | Reference translation |
| `raw_predicted` | TEXT | YES | — | Raw model output (pre-processing) |
| `predicted` | TEXT | YES | — | Final predicted translation |
| `segment` | TEXT | YES | — | Corpus segment |
| `difficulty` | SMALLINT | YES | — | Difficulty tier (1–5) |
| `domain` | TEXT | YES | — | Content domain |
| `exact_match` | BOOLEAN | NOT NULL | — | Exact string match |
| `chrf_score` | REAL | YES | — | Per-entry chrF++ |
| `bleu_score` | REAL | YES | — | Per-entry BLEU |
| `latency_s` | REAL | YES | — | Per-entry response time |
| `cost_usd` | REAL | YES | — | Per-entry API cost |
| `tool_call_count` | SMALLINT | YES | `0` | Tool calls used |
| `error` | TEXT | YES | — | Error message if failed |
| `plugin_metrics` | JSONB | YES | `'{}'` | Full plugin results blob |
| `fst_valid` | BOOLEAN | YES | — | FST accepted? |
| `equivalent_match` | BOOLEAN | YES | — | Structural equivalence? |
| `semantic_verdict` | TEXT | YES | — | VALID/MISMATCH/UNKNOWN/ERROR |
| `code_switching_detected` | BOOLEAN | YES | — | Source leakage? |
| `hallucination_detected` | BOOLEAN | YES | — | Fabricated content? |

### Constraints

```sql
UNIQUE (run_card_id, entry_id)
```

### RLS Policies

| Policy | Operation | Rule |
|--------|-----------|------|
| Public read | SELECT | `USING (true)` |
| Authenticated insert | INSERT | `WITH CHECK (auth.uid() IS NOT NULL)` |
| Authenticated update | UPDATE | `USING (auth.uid() IS NOT NULL)` |

---

## Table: `datasets`

Corpus metadata registry. Populated organically by `publish.py` on every publish.

### Canonical Schema

> [!WARNING]
> Two conflicting schemas existed:
> - **CLI migration** `20260528024953`: scalar `domain TEXT`, `segment TEXT` with CHECK, `source TEXT`, `notes TEXT`
> - **Arena migration** `009`: array `domains TEXT[]`, `segments TEXT[]`, with `difficulty_min/max`
>
> **Resolution**: The CLI migration was applied first to the live DB. Arena migration 009
> uses `CREATE TABLE IF NOT EXISTS` and would be a no-op. A reconciliation migration
> (`011_reconcile_datasets.sql`) adds the arena columns to the existing CLI table.

### Columns (after reconciliation)

| Column | Type | Nullable | Default | Source | Origin |
|--------|------|----------|---------|--------|--------|
| `id` | TEXT | NOT NULL | — | PK | CLI |
| `name` | TEXT | NOT NULL | — | `publish.py` | CLI |
| `version` | TEXT | YES | — | `publish.py` | CLI (relaxed by 011) |
| `source_language` | TEXT | NOT NULL | — | `publish.py` | CLI |
| `target_language` | TEXT | NOT NULL | — | `publish.py` | CLI |
| `language_pair` | TEXT | NOT NULL | — | `publish.py` | CLI |
| `entry_count` | INTEGER | YES | — | `publish.py` | CLI |
| `sha256` | TEXT | YES | — | `publish.py` | CLI |
| `domain` | TEXT | YES | — | — | CLI (scalar, original) |
| `segment` | TEXT | NOT NULL | `'development'` | — | CLI (with CHECK) |
| `license` | TEXT | YES | — | — | CLI |
| `source` | TEXT | YES | — | — | CLI (attribution) |
| `notes` | TEXT | YES | — | — | CLI |
| `created_at` | TIMESTAMPTZ | YES | `now()` | DB | CLI |
| `difficulty_min` | INTEGER | YES | — | `publish.py` | Arena (via 011) |
| `difficulty_max` | INTEGER | YES | — | `publish.py` | Arena (via 011) |
| `domains` | TEXT[] | YES | `'{}'` | `publish.py` | Arena (via 011) |
| `segments` | TEXT[] | YES | `'{}'` | `publish.py` | Arena (via 011) |
| `updated_at` | TIMESTAMPTZ | YES | `now()` | DB trigger | Arena (via 011) |
| `metadata` | JSONB | YES | `'{}'` | — | Arena (via 011) |

### RLS Policies

| Policy | Operation | Rule |
|--------|-----------|------|
| Anon read (public segments) | SELECT | `TO anon USING (segment IS NULL OR segment NOT IN ('held_out', 'gold_standard'))` |
| Authenticated read | SELECT | `TO authenticated USING (true)` |
| Authenticated write | ALL (INSERT/UPDATE/DELETE) | `WITH CHECK (auth.role() = 'authenticated')` |

> [!NOTE]
> Migration `016_datasets_rls.sql` replaced the original blanket public-read
> policy (`datasets_public_read`, `USING (true)`). Anonymous visitors can no
> longer enumerate metadata (entry counts, sha256 hashes) of held-out or
> gold-standard corpora. `service_role` bypasses RLS and is unaffected.

---

## Table: `run_cards_audit`

Audit trail for run card mutations (migration `017_run_cards_audit.sql`).
Run cards are immutable via the public API; any UPDATE/DELETE (admin
moderation via service_role, or a future policy mistake) preserves the
prior row here so tampering is detectable and reversible.

### Columns

| Column | Type | Nullable | Default | Source |
|--------|------|----------|---------|--------|
| `id` | BIGINT | NOT NULL | identity | DB |
| `run_card_id` | TEXT | NOT NULL | — | Trigger (`OLD.id`) |
| `action` | TEXT | NOT NULL | — | Trigger (`TG_OP`) — **CHECK**: `('UPDATE', 'DELETE')` |
| `changed_at` | TIMESTAMPTZ | NOT NULL | `now()` | DB |
| `old_row` | JSONB | NOT NULL | — | Trigger (`to_jsonb(OLD)`) — complete prior row |

### Trigger

```sql
run_cards_audit_trigger: AFTER UPDATE OR DELETE ON run_cards
    FOR EACH ROW EXECUTE FUNCTION run_cards_audit_fn()  -- SECURITY DEFINER
```

### Indexes

```sql
idx_run_cards_audit_run_card ON (run_card_id)
```

### RLS Policies

| Policy | Operation | Rule |
|--------|-----------|------|
| Service-role read | SELECT | `TO service_role USING (true)` |
| *(no anon/authenticated policies)* | — | RLS enabled + no policy = deny; the audit log is invisible to the public API |

---

## Table: `contests`

Contest infrastructure for competitive evaluation.

### Columns

| Column | Type | Nullable | Default | Source |
|--------|------|----------|---------|--------|
| `id` | TEXT | NOT NULL | — | PK (slug) |
| `name` | TEXT | NOT NULL | — | `contest.py` |
| `description` | TEXT | YES | `''` | `contest.py` |
| `corpus_id` | TEXT | NOT NULL | — | `contest.py` |
| `language_pair` | TEXT | NOT NULL | — | `contest.py` |
| `visibility` | TEXT | NOT NULL | `'public'` | `contest.py` |
| `teams` | TEXT[] | YES | `'{}'` | `contest.py` |
| `created_by` | TEXT | NOT NULL | — | `contest.py` (from auth) |
| `status` | TEXT | NOT NULL | `'open'` | `contest.py` |
| `metadata` | JSONB | YES | `'{}'` | *unused* |
| `created_at` | TIMESTAMPTZ | YES | `now()` | DB |

### Constraints

```sql
CHECK (visibility IN ('public', 'private', 'team'))
CHECK (status IN ('open', 'closed', 'archived'))
```

### RLS Policies

| Policy | Operation | Rule |
|--------|-----------|------|
| Read public/private/team | SELECT | `USING (visibility IN ('public','private') OR auth.uid() IS NOT NULL)` |
| Authenticated create | INSERT | `WITH CHECK (auth.uid() IS NOT NULL)` |
| Owner update | UPDATE | `USING (created_by = jwt.email)` |

---

## Table: `contest_submissions`

Links run cards to contests.

### Columns

| Column | Type | Nullable | Default | Source |
|--------|------|----------|---------|--------|
| `id` | BIGINT | NOT NULL | auto-increment | DB |
| `contest_id` | TEXT | NOT NULL | — | FK to `contests.id` |
| `run_card_id` | TEXT | NOT NULL | — | FK to `run_cards.id` |
| `submitted_by` | TEXT | NOT NULL | — | `contest.py` (from auth) |
| `team` | TEXT | YES | — | `contest.py` |
| `notes` | TEXT | YES | `''` | `contest.py` |
| `submitted_at` | TIMESTAMPTZ | YES | `now()` | DB |

### Constraints

```sql
UNIQUE (contest_id, run_card_id)
```

### RLS Policies

| Policy | Operation | Rule |
|--------|-----------|------|
| Read own or public submissions | SELECT | `USING (public contest OR own submission OR contest creator)` |
| Authenticated submit | INSERT | `WITH CHECK (auth.uid() IS NOT NULL)` |

---

## Design Principles

1. **Denormalize for query speed**: Core metrics are top-level REAL columns (not buried in JSONB) so the leaderboard can `ORDER BY composite_score DESC` without function calls.

2. **JSONB as source of truth**: The `run_card` JSONB blob contains everything. Top-level columns are denormalized copies for SQL ergonomics. If they disagree, JSONB wins.

3. **Immutable submissions**: Run cards cannot be updated or deleted via the API. Only admins (service_role key) can moderate. This prevents score tampering.

4. **Trust escalation is admin-only**: CLI always inserts `trust = 'unverified'`. Promotion to `'verified'` or demotion to `'disqualified'` happens via the Supabase dashboard.

5. **Organic metadata**: The `datasets` table is populated by `publish.py` as a side effect of publishing runs. No separate seeding workflow needed.

6. **RLS requires authentication for writes**: All INSERT/UPDATE policies require `auth.uid() IS NOT NULL`. The anon key is only sufficient for SELECT.
