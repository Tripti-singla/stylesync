import json
from pathlib import Path

from services.virtual_tryon import train_tryon_model, _load_sample_records

BASE_DIR = Path(__file__).resolve().parent
SAMPLES_FILE = BASE_DIR / "tryon_dataset" / "samples.json"


def _load_samples() -> list:
    samples = _load_sample_records()
    if samples:
        return samples

    if not SAMPLES_FILE.exists():
        return []

    try:
        return json.loads(SAMPLES_FILE.read_text(encoding="utf-8") or "[]")
    except Exception:
        return []

if __name__ == "__main__":
    if not _load_samples():
        print("No try-on samples found yet. Open the Try On page and generate a try-on once, or run backend/seed_tryon_samples.py to seed Supabase.")
        exit(0)

    print("Starting virtual try-on training...")
    result = train_tryon_model(epochs=5, batch_size=2, learning_rate=1e-3)

    if result.get("status") == "trained":
        print(f"Training completed: {result}")
    else:
        print(f"Training failed: {result}")
