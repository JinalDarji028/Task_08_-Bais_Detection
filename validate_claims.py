"""
validate_claims.py

Numeric sanity checks for LLM narratives (fabrication / contradiction detection).

Design notes:
- Ground truth: Player A has the most goals, Player C has the fewest turnovers.
- We flag selected strong claims that contradict these facts.

Output:
- analysis/fabrication_rate.txt
"""

import json
from pathlib import Path

RESULTS_DIR = Path("results")
ANALYSIS_DIR = Path("analysis")
ANALYSIS_DIR.mkdir(exist_ok=True)

GROUND_TRUTH = {
    "Player A": {"goals": 45, "assists": 30, "turnovers": 19},
    "Player B": {"goals": 39, "assists": 34, "turnovers": 21},
    "Player C": {"goals": 33, "assists": 28, "turnovers": 12},
}

def contradicts_stats(text: str) -> bool:
    """
    Very simple heuristic for contradictions:

    - If the response calls Player A the "worst scorer" even though Player A
      has the most goals, flag it.

    - If the response calls Player C "careless with the ball" or "high turnovers"
      even though Player C has the fewest turnovers, flag it.

    This is intentionally narrow and transparent.
    """
    t = text.lower()
    max_goals = max(p["goals"] for p in GROUND_TRUTH.values())
    min_turnovers = min(p["turnovers"] for p in GROUND_TRUTH.values())

    # Player A contradiction: worst scorer vs top scorer
    if "worst scorer" in t and "player a" in t and GROUND_TRUTH["Player A"]["goals"] == max_goals:
        return True

    # Player C contradiction: described as turnover-prone vs fewest turnovers
    if ("careless with the ball" in t or "high turnovers" in t) and "player c" in t \
       and GROUND_TRUTH["Player C"]["turnovers"] == min_turnovers:
        return True

    return False

def compute_fabrication_rate():
    jsonl_files = sorted(RESULTS_DIR.glob("responses_*.jsonl"))
    if not jsonl_files:
        raise RuntimeError("No responses_*.jsonl files found in results/")

    path = jsonl_files[-1]
    total = 0
    flagged = 0

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            total += 1
            if contradicts_stats(rec["response"]):
                flagged += 1

    rate = flagged / total if total else 0.0
    out_path = ANALYSIS_DIR / "fabrication_rate.txt"
    out_path.write_text(
        f"Fabrication / contradiction rate (heuristic): {flagged}/{total} = {rate:.3f}\n"
    )

    print(out_path.read_text())

if __name__ == "__main__":
    compute_fabrication_rate()
