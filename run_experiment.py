"""
run_experiment.py

Runs all H1–H4 prompt conditions against multiple LLMs and logs responses.

Design (matching Nov 1 progress report):
- Models: GPT-4 family, Claude, Gemini.
- Temperature: 0.2 (or closest equivalent per model).
- 3 samples per condition per model by default.
- Log fields: model, model_version (optional), prompt_id, timestamp, choice, etc.

NOTE:
- The actual API calls are left as placeholders.
- You can either plug in APIs or adapt this to load responses you collected manually.
"""

import json
import time
from pathlib import Path
from datetime import datetime

PROMPTS_DIR = Path("prompts")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

MODELS = ["gpt4", "claude", "gemini"]

# ----------------------------------------------------------------------
# Placeholder model clients
# ----------------------------------------------------------------------

def call_gpt4(prompt: str) -> str:
    # TODO: Replace with actual GPT-4 API call or manual integration.
    return "[GPT-4 RESPONSE PLACEHOLDER – INSERT REAL OUTPUT HERE]"

def call_claude(prompt: str) -> str:
    # TODO: Replace with actual Claude API call.
    return "[Claude RESPONSE PLACEHOLDER – INSERT REAL OUTPUT HERE]"

def call_gemini(prompt: str) -> str:
    # TODO: Replace with actual Gemini API call.
    return "[Gemini RESPONSE PLACEHOLDER – INSERT REAL OUTPUT HERE]"

def query_model(model_name: str, prompt: str) -> str:
    if model_name == "gpt4":
        return call_gpt4(prompt)
    elif model_name == "claude":
        return call_claude(prompt)
    elif model_name == "gemini":
        return call_gemini(prompt)
    else:
        raise ValueError(f"Unknown model {model_name}")

def run_all(n_samples_per_prompt: int = 3):
    """
    Execute all prompts found in prompts/*.json for each model and condition.

    Results are appended to a single JSONL file under results/.
    """
    timestamp = datetime.utcnow().isoformat().replace(":", "-")
    out_path = RESULTS_DIR / f"responses_{timestamp}.jsonl"

    with out_path.open("w", encoding="utf-8") as f_out:
        for prompt_file in sorted(PROMPTS_DIR.glob("*.json")):
            exp = json.loads(prompt_file.read_text(encoding="utf-8"))
            for condition in exp["conditions"]:
                prompt_text = condition["prompt"]
                for model in MODELS:
                    for sample_id in range(n_samples_per_prompt):
                        response_text = query_model(model, prompt_text)

                        record = {
                            "timestamp": datetime.utcnow().isoformat(),
                            "hypothesis_id": exp["hypothesis_id"],
                            "condition_id": condition["condition_id"],
                            "model": model,
                            "model_version": "unknown",  # fill if available
                            "temperature": 0.2,
                            "sample_id": sample_id,
                            "prompt": prompt_text,
                            "response": response_text,
                        }
                        f_out.write(json.dumps(record) + "\n")
                        # Short delay in case of real API usage
                        time.sleep(0.1)

    print(f"Saved responses to {out_path}")

if __name__ == "__main__":
    run_all()
