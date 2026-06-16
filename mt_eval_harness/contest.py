"""
Contest Management — Create, submit to, and list evaluation contests.

Contests are structured evaluation challenges scoped to a corpus and
language pair. They support three visibility modes:

  - public:  Anyone can see the contest and all submissions.
  - private: Anyone can see the contest exists, but submissions are
             visible only to the contest creator and the submitter.
  - team:    Only listed teams can see and submit.

This module handles CRUD operations against the Supabase `contests`
and `contest_submissions` tables. Authentication uses the same OAuth
PKCE flow as publish.py (via auth.py).

Usage (via CLI):
    mt-eval contest create --name "EN→CRK Open" --corpus edtekla-v1.json
    mt-eval contest submit --contest en-crk-open --run report.json
    mt-eval contest list
"""

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from mt_eval_harness.auth import get_session, SUPABASE_URL, SUPABASE_ANON_KEY


# ---------------------------------------------------------------------------
# Configuration — imported from auth.py (same constants as publish.py)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Slug generation
# ---------------------------------------------------------------------------

def _slugify(name: str) -> str:
    """Convert a contest name to a URL-safe slug.

    "EN→CRK Open 2026" → "en-crk-open-2026"
    """
    # Replace arrows and special chars with hyphens
    slug = name.lower()
    slug = slug.replace("→", "-").replace("->", "-")
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _api_request(
    method: str,
    path: str,
    data: Optional[dict] = None,
    params: Optional[dict] = None,
    session: Optional[dict] = None,
) -> dict | list | None:
    """Make a request to the Supabase REST API.

    If session is provided, the request is authenticated with the user's
    access token. If session is None, only the anon key is used (suitable
    for reading public data without forcing a login).

    Returns parsed JSON response, or None for empty responses.
    Raises RuntimeError on HTTP errors with descriptive messages.
    """
    url = f"{SUPABASE_URL}/rest/v1/{path}"

    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query}"

    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    # Add user auth if a session was provided
    if session:
        access_token = session.get("access_token", "")
        headers["Authorization"] = f"Bearer {access_token}"

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            if not raw:
                return None
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        raise RuntimeError(
            f"Supabase API error ({e.code}): {body_text}"
        ) from e
    except (urllib.error.URLError, OSError) as e:
        raise RuntimeError(
            f"Network error contacting Supabase: {e}"
        ) from e


# ---------------------------------------------------------------------------
# Contest CRUD
# ---------------------------------------------------------------------------

def create_contest(
    name: str,
    corpus_id: str,
    language_pair: str,
    visibility: str = "public",
    teams: Optional[list[str]] = None,
    description: str = "",
) -> dict:
    """Create a new evaluation contest.

    Args:
        name:          Human-readable contest name (e.g. "EN→CRK Open 2026")
        corpus_id:     Dataset ID or corpus filename to evaluate against
        language_pair: Language pair string (e.g. "en>crk")
        visibility:    Access mode: "public", "private", or "team"
        teams:         Team slugs for team-scoped contests
        description:   Human-readable description

    Returns:
        The created contest record as a dict.

    Raises:
        ValueError: If visibility is invalid or team mode has no teams.
        RuntimeError: On Supabase API errors.
    """
    if visibility not in ("public", "private", "team"):
        raise ValueError(
            f"Invalid visibility '{visibility}'. "
            f"Must be one of: public, private, team."
        )
    if visibility == "team" and not teams:
        raise ValueError(
            "Team-scoped contests require at least one team. "
            "Use --teams 'team1,team2'."
        )

    slug = _slugify(name)

    # Get the submitter's identity from the auth session
    session = get_session()
    from mt_eval_harness.auth import get_submitter_name
    submitter = get_submitter_name(session)

    contest_data = {
        "id": slug,
        "name": name,
        "description": description,
        "corpus_id": corpus_id,
        "language_pair": language_pair,
        "visibility": visibility,
        "teams": teams or [],
        "created_by": submitter,
        "status": "open",
    }

    print(f"\n  Creating contest: {name}")
    print(f"  Slug:            {slug}")
    print(f"  Corpus:          {corpus_id}")
    print(f"  Language pair:   {language_pair}")
    print(f"  Visibility:      {visibility}")
    if teams:
        print(f"  Teams:           {', '.join(teams)}")

    result = _api_request("POST", "contests", data=contest_data, session=session)

    if result:
        record = result[0] if isinstance(result, list) else result
        print(f"\n  ✅ Contest created: {record['id']}")
        return record
    else:
        raise RuntimeError("Contest creation returned empty response.")


def submit_to_contest(
    contest_id: str,
    run_card_id: str,
    team: Optional[str] = None,
    notes: str = "",
) -> dict:
    """Submit a run card to a contest.

    The run card must already be published to Supabase (via mt-eval publish).
    This creates a link between the run and the contest.

    Args:
        contest_id:  Contest slug (e.g. "en-crk-open-2026")
        run_card_id: Run card ID (from the published run card)
        team:        Optional team attribution
        notes:       Optional submission notes

    Returns:
        The created submission record.

    Raises:
        RuntimeError: On Supabase API errors (e.g. contest doesn't exist,
                      run card doesn't exist, duplicate submission).
    """
    # Authenticate first — needed for both the check and the insert
    session = get_session()
    from mt_eval_harness.auth import get_submitter_name
    submitter = get_submitter_name(session)

    # Verify the contest exists and is still accepting submissions.
    # NOTE: The session must be passed here — team-visibility contests
    # are only visible via RLS when authenticated.
    contest_result = _api_request(
        "GET", "contests",
        params={"id": f"eq.{contest_id}", "select": "id,status"},
        session=session,
    )
    if not contest_result:
        raise RuntimeError(f"Contest '{contest_id}' not found.")
    contest = contest_result[0] if isinstance(contest_result, list) else contest_result

    if contest.get("status") != "open":
        raise RuntimeError(
            f"Contest '{contest_id}' is {contest.get('status', 'unknown')} "
            f"— submissions are not accepted."
        )

    submission_data = {
        "contest_id": contest_id,
        "run_card_id": run_card_id,
        "submitted_by": submitter,
        "team": team,
        "notes": notes,
    }

    print(f"\n  Submitting to contest: {contest_id}")
    print(f"  Run card:              {run_card_id}")
    if team:
        print(f"  Team:                  {team}")

    result = _api_request("POST", "contest_submissions", data=submission_data, session=session)

    if result:
        record = result[0] if isinstance(result, list) else result
        print(f"\n  ✅ Submission accepted (id: {record.get('id', '?')})")
        return record
    else:
        raise RuntimeError("Submission returned empty response.")


def list_contests(
    status: str = "open",
    language_pair: Optional[str] = None,
) -> list[dict]:
    """List contests, optionally filtered by status and language pair.

    Args:
        status:        Filter by status: "open", "closed", "all"
        language_pair: Filter by language pair (e.g. "en>crk")

    Returns:
        List of contest records.
    """
    params = {"order": "created_at.desc"}

    if status != "all":
        params["status"] = f"eq.{status}"

    if language_pair:
        params["language_pair"] = f"eq.{language_pair}"

    result = _api_request("GET", "contests", params=params)
    contests = result if isinstance(result, list) else []

    if not contests:
        print("\n  No contests found.")
        return []

    print(f"\n  {'ID':<30s} {'Name':<35s} {'Lang':<8s} {'Vis':<8s} {'Status':<8s}")
    print(f"  {'-'*30} {'-'*35} {'-'*8} {'-'*8} {'-'*8}")

    for c in contests:
        print(
            f"  {c['id']:<30s} "
            f"{c['name'][:35]:<35s} "
            f"{c.get('language_pair', '?'):<8s} "
            f"{c['visibility']:<8s} "
            f"{c['status']:<8s}"
        )

    print(f"\n  {len(contests)} contest(s) found.")
    return contests


def list_submissions(
    contest_id: str,
) -> list[dict]:
    """List submissions for a specific contest.

    Returns submissions joined with basic run_card info. For private
    contests, Supabase RLS ensures only the creator and individual
    submitters see their own submissions.

    Args:
        contest_id: Contest slug

    Returns:
        List of submission records.
    """
    params = {
        "contest_id": f"eq.{contest_id}",
        "order": "submitted_at.desc",
        # Select submission fields + key run_card fields via foreign key
        "select": "id,contest_id,run_card_id,submitted_by,submitted_at,team,notes",
    }

    result = _api_request("GET", "contest_submissions", params=params)
    submissions = result if isinstance(result, list) else []

    if not submissions:
        print(f"\n  No submissions for contest '{contest_id}'.")
        return []

    print(f"\n  Submissions for '{contest_id}':")
    print(f"  {'Run Card':<40s} {'By':<25s} {'Team':<15s} {'Date':<20s}")
    print(f"  {'-'*40} {'-'*25} {'-'*15} {'-'*20}")

    for s in submissions:
        print(
            f"  {s['run_card_id']:<40s} "
            f"{s['submitted_by'][:25]:<25s} "
            f"{(s.get('team') or '-'):<15s} "
            f"{s['submitted_at'][:19]:<20s}"
        )

    print(f"\n  {len(submissions)} submission(s).")
    return submissions


def resolve_run_card_id(run_path: str) -> str:
    """Resolve a run card ID from either a direct ID or a report JSON path.

    If the input looks like a file path (contains / or .json), load the
    file and extract the run_id. Otherwise, treat it as a direct ID.

    Args:
        run_path: Either a run_card_id string or a path to a report JSON.

    Returns:
        The resolved run_card_id string.

    Raises:
        FileNotFoundError: If the path doesn't exist.
        KeyError: If the JSON doesn't contain a run_id.
    """
    if "/" in run_path or run_path.endswith(".json"):
        path = Path(run_path)
        if not path.exists():
            raise FileNotFoundError(f"Report file not found: {run_path}")

        data = json.loads(path.read_text(encoding="utf-8"))

        # Try run_id at top level, then in run_card, then in the report
        run_id = (
            data.get("run_id")
            or data.get("run_card", {}).get("run_id")
            or data.get("metadata", {}).get("run_id")
        )
        if not run_id:
            raise KeyError(
                f"Could not find run_id in {run_path}. "
                f"Publish the run first with 'mt-eval publish'."
            )
        return run_id

    # Treat as direct ID
    return run_path
