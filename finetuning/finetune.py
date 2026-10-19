# -----------------------------------------------------------------------------
# WHAT THIS FILE IS FOR
# -----------------------------------------------------------------------------
# This runs the actual fine-tuning step described in the "Fine-tuning path"
# section of learning.md. It trains a small LoRA adapter on top of the frozen
# Qwen2.5-7B-Instruct base model using the examples in training_data.jsonl, so
# the model reliably produces the exact bug-report JSON shape this project
# needs, instead of relying on prompting alone.
#
# This is a QLoRA fine-tune: the base model is loaded 4-bit quantized and kept
# frozen, and only a small adapter (a few percent of the base model's size)
# gets trained. That's what makes this feasible on a single consumer GPU with
# 8 to 12GB VRAM, instead of needing to retrain all 7B parameters.
#
# WHAT'S DEFINED HERE
#   - main(): loads training_data.jsonl, loads the base model, trains the
#     adapter, and saves the result to ./jira-architect-adapter.
#
# BEFORE RUNNING THIS FILE
#   1. Run prepare_dataset.py first, so training_data.jsonl exists.
#   2. Install the fine-tuning tools (not part of the main app's
#      requirements.txt, since fine-tuning is a separate, optional,
#      run-on-your-own-hardware step):
#        .venv\Scripts\python.exe -m pip install -r finetuning\requirements.txt
#   3. Make sure you have a CUDA-capable GPU available. This step runs
#      locally on hardware you control, never a hosted fine-tuning API, since
#      that would mean sending defect data to a third party (see
#      .github/copilot-instructions.md).
#
# AFTER RUNNING THIS FILE
#   Merge the adapter into the base model and convert to GGUF so Ollama can
#   run it, then evaluate it against the base model before switching the app
#   over. See the "Merge and convert for Ollama" section of learning.md for
#   those remaining steps.
# -----------------------------------------------------------------------------

from pathlib import Path

from datasets import load_dataset
from trl import SFTTrainer
from unsloth import FastLanguageModel

THIS_DIR = Path(__file__).parent
TRAINING_DATA = THIS_DIR / "training_data.jsonl"
ADAPTER_OUTPUT_DIR = THIS_DIR / "jira-architect-adapter"

BASE_MODEL = "unsloth/Qwen2.5-7B-Instruct"


def format_example(example: dict) -> dict:
    """Combine instruction/input/output into the single text field SFTTrainer trains on."""
    prompt = f"{example['instruction']}\n\n{example['input']}"
    return {"text": f"{prompt}\n\n{example['output']}"}


def main() -> None:
    if not TRAINING_DATA.exists():
        raise FileNotFoundError(f"{TRAINING_DATA} not found. Run prepare_dataset.py first.")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE_MODEL,
        load_in_4bit=True,  # QLoRA: trains a small adapter, not the full model
    )
    model = FastLanguageModel.get_peft_model(model, r=16, lora_alpha=16)

    dataset = load_dataset("json", data_files=str(TRAINING_DATA), split="train")
    dataset = dataset.map(format_example)

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        tokenizer=tokenizer,
        dataset_text_field="text",
    )
    trainer.train()

    model.save_pretrained(str(ADAPTER_OUTPUT_DIR))
    tokenizer.save_pretrained(str(ADAPTER_OUTPUT_DIR))
    print(f"Adapter saved to {ADAPTER_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
