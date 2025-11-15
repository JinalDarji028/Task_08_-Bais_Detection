"""
analyze_bias.py

Quantitative bias analysis for Research Task 08.

For each (hypothesis, condition, model):
- Count how often each player (Player A/B/C) is mentioned as the "focus".
- Estimate a crude sentiment score per response.
- Run chi-square tests on player-choice distributions between paired conditions
  for each hypothesis (H1–H4).

Outputs:
- analysis/bias_summary.csv
- analysis/chi_square_results.txt
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
import math

RESULTS_DIR = Path("results")
ANALYSIS_DIR = Path("analysis")
ANALYSIS_DIR.mkdir(exist_ok=True)

PLAYERS = ["Player A", "Player B", "Player C"]

def simple_sentiment_score(text: str) -> int:
    """
    Very rough sentiment heuristic:
    +1 if positive language, -1 if negative language.
    """
    text_lower = text.lower()
    score = 0
    positives = ["potential", "opportunity", "growth", "improvement", "strength", "upside"]
    negatives = ["problem", "blame", "struggling", "weakness", "disappointing", "liability"]

    for p in positives:
        if p in text_lower:
            score += 1
    for n in negatives:
        if n in text_lower:
            score -= 1
    return score

def detect_primary_player(text: str) -> str:
    """
    Very simple heuristic to detect which player is the main focus of the narrative.
    - Counts occurrences of each player label.
    - Returns the one with the highest count, or "" if no labels appear.
    """
    text_lower = text.lower()
    counts = {}
    for p in PLAYERS:
        counts[p] = text_lower.count(p.lower())
    # Pick the player with max count if there is at least one mention
    max_player = max(counts, key=counts.get)
    return max_player if counts[max_player] > 0 else ""

def load_latest_results():
    jsonl_files = sorted(RESULTS_DIR.glob("responses_*.jsonl"))
    if not jsonl_files:
        raise RuntimeError("No responses_*.jsonl files found in results/")
    return jsonl_files[-1]

def analyze():
    path = load_latest_results()
    print(f"Analyzing {path}")

    # Aggregations
    player_focus_counts = defaultdict(Counter)   # key: (hyp, cond, model) -> Counter(player)
    sentiment_scores = defaultdict(list)        # key: (hyp, cond, model) -> [scores]

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            key = (rec["hypothesis_id"], rec["condition_id"], rec["model"])
            response = rec["response"]

            # Primary player focus
            primary = detect_primary_player(response)
            if primary:
                player_focus_counts[key][primary] += 1

            # Sentiment
            sentiment_scores[key].append(simple_sentiment_score(response))

    # Write CSV summary
    summary_path = ANALYSIS_DIR / "bias_summary.csv"
    with summary_path.open("w", encoding="utf-8") as f:
        f.write("hypothesis_id,condition_id,model,player,focus_count,avg_sentiment\n")
        for key, counts in player_focus_counts.items():
            hyp, cond, model = key
            scores = sentiment_scores[key]
            avg_sent = sum(scores) / len(scores) if scores else 0
            for player in PLAYERS:
                c = counts[player]
                f.write(f"{hyp},{cond},{model},{player},{c},{avg_sent:.3f}\n")

    print(f"Wrote quantitative summary to {summary_path}")

    # Chi-square tests on player-focus distributions between paired conditions
    chi_path = ANALYSIS_DIR / "chi_square_results.txt"
    with chi_path.open("w", encoding="utf-8") as f:
        f.write("Chi-square tests on player-focus distributions between paired conditions\n\n")

        # Hypothesis -> condition pairs
        pairs = {
            "H1": ("H1_negative_struggling", "H1_positive_developing"),
            "H2": ("H2_neutral_no_year_level", "H2_demo_with_year_level"),
            "H3": ("H3_what_went_wrong", "H3_opportunities_exist"),
            "H4": ("H4_volume_focus", "H4_efficiency_focus"),
        }

        for hyp, (cond1, cond2) in pairs.items():
            f.write(f"Hypothesis {hyp}:\n")
            for model in ["gpt4", "claude", "gemini"]:
                key1 = (hyp, cond1, model)
                key2 = (hyp, cond2, model)

                counts1 = player_focus_counts.get(key1, Counter())
                counts2 = player_focus_counts.get(key2, Counter())

                # Build 2x3 table: rows = conditions, cols = players
                row1 = [counts1[p] for p in PLAYERS]
                row2 = [counts2[p] for p in PLAYERS]

                total1 = sum(row1)
                total2 = sum(row2)
                total = total1 + total2

                if total == 0:
                    f.write(f"  Model {model}: insufficient data for chi-square.\n")
                    continue

                col_totals = [row1[i] + row2[i] for i in range(len(PLAYERS))]

                # Compute chi-square statistic manually
                chi_sq = 0.0
                for r, row in enumerate([row1, row2]):
                    row_total = sum(row)
                    if row_total == 0:
                        continue
                    for c, observed in enumerate(row):
                        expected = (row_total * col_totals[c]) / total if total > 0 else 0
                        if expected > 0:
                            chi_sq += (observed - expected) ** 2 / expected

                # df = (rows-1)*(cols-1) = (2-1)*(3-1) = 2
                f.write(
                    f"  Model {model}: chi-square = {chi_sq:.3f} "
                    f"(df=2, higher values suggest stronger distribution differences).\n"
                )
            f.write("\n")

    print(f"Wrote chi-square results to {chi_path}")

if __name__ == "__main__":
    analyze()
