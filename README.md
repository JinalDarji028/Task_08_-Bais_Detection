# Research Task 08 – Bias Detection in LLM Data Narratives

This repository contains the final implementation for **Research Task 08: Bias Detection in LLM Data Narratives**
(Nov 15 submission), building on the experimental design and data-collection progress reported on Nov 1.

## Objective

Test whether large language models (LLMs) produce systematically different narratives about the **same synthetic dataset**
when prompts change in terms of framing, demographic emphasis, prior assumptions, or which statistics are foregrounded.

## Design Summary

- Synthetic, anonymized player statistics (Player A–C) with fields:
  `player_id`, `goals`, `assists`, `turnovers`, `year_level`.
- Ground truth:
  - Player A has the most goals.
  - Player C has the fewest turnovers.
- Models under test:
  - GPT-4 family
  - Claude (Syracuse enterprise license)
  - Gemini
- Prompts organized into four hypotheses (H1–H4) with paired conditions:
  - H1: framing bias (struggling vs developing)
  - H2: demographic bias (with vs without year_level)
  - H3: confirmation / valence bias (what went wrong vs what opportunities exist)
  - H4: selection bias (volume vs efficiency prompts)
- Controls:
  - Same dataset block in all prompts.
  - Temperature fixed at 0.2 (or closest equivalent per model).
  - 3 samples per condition per model.

## Repository Structure

- `experiment_design.py`
  - Generates all H1–H4 prompt templates with embedded synthetic dataset and saves them to `prompts/H1_prompts.json`, etc.
- `run_experiment.py`
  - Executes all prompts for GPT-4, Claude, and Gemini.
  - Logs responses in JSONL format under `results/responses_*.jsonl`.
  - Contains placeholder API client functions for each model that you can connect to real APIs or adapt to a manual workflow.
- `analyze_bias.py`
  - Quantitative analysis of:
    - Primary player focus in each narrative.
    - Crude sentiment scores based on positive/negative word lists.
  - Writes a summary table to `analysis/bias_summary.csv`.
  - Runs chi-square tests on player-focus distributions between paired conditions for each hypothesis and model, writing to
    `analysis/chi_square_results.txt`.
- `validate_claims.py`
  - Contains a small set of transparent rules to detect strong contradictions with the ground truth (e.g., calling Player A
    the “worst scorer” despite having the most goals).
  - Writes a heuristic fabrication/contradiction rate to `analysis/fabrication_rate.txt`.
- `prompts/`
  - JSON files for each hypothesis created by `experiment_design.py`.
- `results/`
  - JSONL files with model responses (not pre-populated in this template).
- `analysis/`
  - Summary CSVs and text outputs created by `analyze_bias.py` and `validate_claims.py`.
- `REPORT.md`
  - Final written report describing the experiment, results, observed bias patterns, and mitigation strategies.
- `.gitignore`
  - Ensures raw datasets and intermediate data files (e.g., CSVs, JSONL from source data) are **not** committed.
- `requirements.txt`
  - Placeholder file to list any third-party Python libraries you decide to use.

## How to Use This Repository

1. (Optional) Create and activate a virtual environment.

2. Install any dependencies you add:

   ```bash
   pip install -r requirements.txt
   ```

3. Generate prompts:

   ```bash
   python experiment_design.py
   ```

4. Run the experiment:

   - Connect `call_gpt4`, `call_claude`, and `call_gemini` in `run_experiment.py` to your actual model clients,
     or modify the script to load responses you have collected manually.
   - Then run:

   ```bash
   python run_experiment.py
   ```

5. Analyze bias patterns:

   ```bash
   python analyze_bias.py
   python validate_claims.py
   ```

   - Check `analysis/bias_summary.csv` for focus and sentiment patterns.
   - Check `analysis/chi_square_results.txt` for chi-square results.
   - Check `analysis/fabrication_rate.txt` for contradiction / fabrication estimates.

6. Review and summarize:

   - Use `REPORT.md` as the main narrative artifact for your Nov 15 submission and link the GitHub repository
     in your Qualtrics report, as required for OPT documentation.

## Ethics and Privacy

- All players are anonymized as “Player A/B/C” with synthetic statistics.
- No personally identifying information (PII) is stored or processed.
- Raw source data files are **not** committed to this repository, in line with task instructions.
- The focus of this project is to study and mitigate bias in LLM-generated narratives, not to evaluate individuals.
