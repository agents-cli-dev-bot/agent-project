"""Self-evaluation feedback loop.

Reads the latest grade results, identifies weak responses (score below threshold),
and drafts new eval cases to expand coverage. Run after `agents-cli eval run`.

Usage:
    uv run python tests/eval/feedback_loop.py
    uv run python tests/eval/feedback_loop.py --threshold 4 --output tests/eval/datasets/weak-cases.json
"""

from __future__ import annotations

import argparse
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types

_ARTIFACTS_DIR = Path(__file__).parent.parent.parent / "artifacts" / "grade_results"
_DATASETS_DIR = Path(__file__).parent / "datasets"

_local = threading.local()


def _client() -> genai.Client:
    c = getattr(_local, "client", None)
    if c is None:
        c = _local.client = genai.Client()
    return c


def _latest_results_file() -> Path | None:
    if not _ARTIFACTS_DIR.exists():
        return None
    files = sorted(_ARTIFACTS_DIR.glob("results_*.json"))
    return files[-1] if files else None


def _load_results(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _mean_score(scores: dict[str, float]) -> float:
    values = [v for v in scores.values() if v is not None]
    return sum(values) / len(values) if values else 0.0


def _draft_new_eval_case(weak_case: dict, model: str = "gemini-2.5-flash") -> dict | None:
    """Use an LLM to draft a new eval case inspired by a weak response."""
    prompt_text = weak_case.get("prompt_text", "")
    agent_response = ""

    if not prompt_text:
        return None

    draft_prompt = f"""You are a QA engineer for a customer support AI agent.

A real interaction had a weak response (low score). Draft a NEW, distinct eval case
that tests a similar scenario but with a clearer expected outcome.

Weak interaction:
- User prompt: {prompt_text}
- Agent response: {agent_response}

Draft a new eval case as JSON with these fields:
- eval_case_id: a unique snake_case ID
- prompt: {{"role": "user", "parts": [{{"text": "<user message>"}}]}}
- reference: {{"response": {{"role": "model", "parts": [{{"text": "<expected response summary>"}}]}}}}

Focus on what the agent SHOULD have done better. Return only the JSON object.
"""

    try:
        response = _client().models.generate_content(
            model=model,
            contents=draft_prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json",
            ),
        )
        raw = response.text or ""
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as exc:
        print(f"  Warning: could not draft new case: {exc}")
        return None


def run_feedback_loop(
    results_file: Path | None,
    threshold: float,
    output: Path,
    dry_run: bool,
) -> None:
    if results_file is None:
        results_file = _latest_results_file()
    if results_file is None:
        print("No grade results found. Run `agents-cli eval run` first.")
        return

    print(f"Reading results from: {results_file}")
    data = _load_results(results_file)
    eval_cases = data.get("eval_cases", [])

    # The grade results file uses eval_case_results with nested response_candidate_results.
    # The dataset metadata is in data["metadata"]["dataset"].
    eval_case_results = data.get("eval_case_results", [])
    dataset_entries = data.get("metadata", {}).get("dataset", [])

    print(f"Found {len(eval_case_results)} graded eval cases.")
    print(f"Identifying weak responses (mean score < {threshold})...")

    weak_cases = []
    for idx, case_result in enumerate(eval_case_results):
        candidates = case_result.get("response_candidate_results", [])
        if not candidates:
            continue
        metric_results = candidates[0].get("metric_results", {})
        scores = {
            metric: v.get("score")
            for metric, v in metric_results.items()
            if isinstance(v, dict) and v.get("score") is not None
        }
        mean = _mean_score(scores)
        # Get case metadata from the dataset entries
        dataset_meta = dataset_entries[idx] if idx < len(dataset_entries) else {}
        prompt_text = dataset_meta.get("prompt_display_text", "")
        case_id = dataset_meta.get("eval_case_id", f"case_{idx}")
        if mean < threshold:
            print(f"  Weak case: {case_id} (mean score: {mean:.2f})")
            weak_cases.append({
                "eval_case_id": case_id,
                "prompt_text": prompt_text,
                "scores": scores,
                "mean_score": mean,
            })

    if not weak_cases:
        print(f"All cases scored >= {threshold}. No new eval cases needed.")
        return

    print(f"\nDrafting {len(weak_cases)} new eval case(s)...")
    new_cases = []
    for case in weak_cases:
        case_id = case.get("eval_case_id", "unknown")
        print(f"  Drafting for: {case_id} (mean score: {case.get('mean_score', 0):.2f})...")
        if dry_run:
            new_cases.append({
                "eval_case_id": f"draft_for_{case_id}",
                "prompt": {"role": "user", "parts": [{"text": "<placeholder — run without --dry-run>"}]},
                "_source": {"weak_case_id": case_id, "mean_score": case.get("mean_score", 0)},
            })
        else:
            new_case = _draft_new_eval_case(case)
            if new_case:
                new_case["eval_case_id"] = new_case.get("eval_case_id", f"draft_for_{case_id}")
                new_cases.append(new_case)
                print(f"    → Drafted: {new_case['eval_case_id']}")

    if not new_cases:
        print("No new cases could be drafted.")
        return

    dataset = {
        "_comment": (
            f"Auto-generated by feedback_loop.py on {datetime.now(timezone.utc).isoformat()} "
            f"from {results_file.name}. Review before adding to main dataset."
        ),
        "eval_cases": new_cases,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(dataset, indent=2), encoding="utf-8")
    print(f"\nWrote {len(new_cases)} new eval case(s) to: {output}")
    print("Review them, adjust the expected answers, then add to your main dataset.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Self-eval feedback loop")
    parser.add_argument("--results", type=Path, default=None,
                        help="Path to a results_*.json file (defaults to latest)")
    parser.add_argument("--threshold", type=float, default=4.0,
                        help="Mean score below which a case is 'weak' (default: 4.0)")
    parser.add_argument("--output", type=Path,
                        default=_DATASETS_DIR / "weak-cases.json",
                        help="Where to write new eval cases")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show which cases would be drafted without calling the LLM")
    args = parser.parse_args()
    run_feedback_loop(
        results_file=args.results,
        threshold=args.threshold,
        output=args.output,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
