import json
import base64
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "tryon_dataset"
IMAGES_DIR = DATASET_DIR / "images"
HISTORY_FILE = DATASET_DIR / "history.json"
SAMPLES_FILE = DATASET_DIR / "samples.json"

def migrate():
    print("=" * 60)
    print("Virtual Try-on Data Migration & Optimization Script")
    print("=" * 60)

    # Ensure images directory exists
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Deduplicate samples.json
    if SAMPLES_FILE.exists():
        print(f"Reading {SAMPLES_FILE}...")
        try:
            with open(SAMPLES_FILE, "r", encoding="utf-8") as f:
                samples = json.load(f)
            
            seen_ids = set()
            deduped_samples = []
            for sample in samples:
                sid = sample.get("sample_id") or sample.get("id")
                if sid not in seen_ids:
                    seen_ids.add(sid)
                    deduped_samples.append(sample)
            
            print(f"Deduplicated samples: {len(samples)} -> {len(deduped_samples)}")
            with open(SAMPLES_FILE, "w", encoding="utf-8") as f:
                json.dump(deduped_samples, f, indent=2)
            print("Successfully saved deduplicated samples.json")
        except Exception as e:
            print(f"Error migrating samples.json: {e}")
    else:
        print("No samples.json found to migrate.")

    # 2. Migrate history.json
    if HISTORY_FILE.exists():
        original_size = HISTORY_FILE.stat().st_size
        print(f"Reading {HISTORY_FILE} (size: {original_size / (1024*1024):.2f} MB)...")
        
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
            
            migrated_count = 0
            for record in history:
                record_id = record.get("id")
                tryon_image = record.get("tryon_image")
                
                # Check if it has base64 image data
                if tryon_image and isinstance(tryon_image, str) and not tryon_image.startswith("tryon_dataset"):
                    try:
                        # Decode and save
                        tryon_filename = f"tryon_{record_id}.png"
                        target_path = IMAGES_DIR / tryon_filename
                        image_data = base64.b64decode(tryon_image)
                        with open(target_path, "wb") as img_file:
                            img_file.write(image_data)
                        
                        # Update record
                        record["tryon_image_path"] = f"tryon_dataset/images/{tryon_filename}"
                        # Omit/remove large base64 string
                        record.pop("tryon_image", None)
                        migrated_count += 1
                    except Exception as img_err:
                        print(f"Error migrating image for record {record_id}: {img_err}")
            
            print(f"Migrated {migrated_count} try-on images to files.")
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
            
            new_size = HISTORY_FILE.stat().st_size
            print(f"Optimization complete. New size: {new_size / 1024:.2f} KB")
            print(f"Space reclaimed: {(original_size - new_size) / (1024*1024):.2f} MB")
        except Exception as e:
            print(f"Error migrating history.json: {e}")
    else:
        print("No history.json found to migrate.")

if __name__ == "__main__":
    migrate()
