# -----------------------------------------------------------------------------
# WHAT THIS FILE IS FOR
# -----------------------------------------------------------------------------
# Fine-tuning tools (unsloth, trl, datasets, torch) expect training examples
# as JSON Lines (one JSON object per line), not CSV. This script converts the
# human-editable training_data.csv in this folder into that JSONL format, so
# the CSV stays easy to open and edit in Excel or a text editor while the
# actual training step still gets the format it needs.
#
# WHAT'S DEFINED HERE
#   - main(): reads training_data.csv, builds one instruction/input/output
#     example per row, and writes training_data.jsonl.
#
# WHO CALLS THIS FILE
#   - Run it directly before finetune.py: it produces the file finetune.py
#     reads from.
#
# OUTPUT SHAPE (per line)
#   {
#     "instruction": "Format this bug report",
#     "input": "<brain_dump column>",
#     "output": "{\"title\": ..., \"steps_to_reproduce\": [...], ...}"
#   }
# The "output" JSON matches app/schemas/bug_report.py exactly, so a model
# fine-tuned on this data learns to produce answers the rest of the app can
# already validate and use.
# -----------------------------------------------------------------------------

import csv
import json
from pathlib import Path

THIS_DIR = Path(__file__).parent
INPUT_CSV = THIS_DIR / "training_data.csv"
OUTPUT_JSONL = THIS_DIR / "training_data.jsonl"

INSTRUCTION = "Format this bug report"


def row_to_example(row: dict[str, str]) -> dict[str, str]:
    """Convert one CSV row into an instruction/input/output training example."""
    # steps_to_reproduce is stored in the CSV as a single "|"-separated
    # string (e.g. "Open app|Click export") since CSV cells can't hold a
    # list directly. Split it back into the list shape the app's schema
    # expects, dropping any empty/whitespace-only steps.
    steps = [step.strip() for step in row["steps_to_reproduce"].split("|") if step.strip()]

    output = {
        "title": row["title"],
        "steps_to_reproduce": steps,
        "expected_result": row["expected_result"],
        "actual_result": row["actual_result"],
        "environment_context": row["environment_context"],
    }

    return {
        "instruction": INSTRUCTION,
        "input": row["brain_dump"],
        "output": json.dumps(output),
    }


def main() -> None:
    with INPUT_CSV.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        examples = [row_to_example(row) for row in reader]

    with OUTPUT_JSONL.open("w", encoding="utf-8") as jsonl_file:
        for example in examples:
            jsonl_file.write(json.dumps(example) + "\n")

    print(f"Wrote {len(examples)} examples to {OUTPUT_JSONL}")


if __name__ == "__main__":
    main()
