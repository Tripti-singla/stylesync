import sys
import huggingface_hub
# Mock cached_download in huggingface_hub to prevent import errors in older diffusers versions
if not hasattr(huggingface_hub, "cached_download"):
    try:
        import huggingface_hub.file_download
        huggingface_hub.cached_download = huggingface_hub.file_download.hf_hub_download
        sys.modules["huggingface_hub"].cached_download = huggingface_hub.file_download.hf_hub_download
    except Exception:
        pass

import base64
import io
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image, ImageOps

from services.supabase_service import add_tryon_sample, get_tryon_samples, supabase

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "tryon_dataset"
IMAGES_DIR = DATA_DIR / "images"
SAMPLES_FILE = DATA_DIR / "samples.json"
HISTORY_FILE = DATA_DIR / "history.json"
MODEL_PATH = DATA_DIR / "tryon_model.pth"

os.makedirs(IMAGES_DIR, exist_ok=True)


def _load_json_list(file_path: Path) -> list:
    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _append_json_record(file_path: Path, record: dict):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    records = _load_json_list(file_path)
    records.append(record)

    with open(file_path, "w", encoding="utf-8") as file_handle:
        json.dump(records, file_handle, indent=2)


def _load_image_from_url(url: str) -> Image.Image:
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert("RGBA")
    except Exception:
        return Image.new("RGBA", (768, 1024), (235, 235, 235, 255))


def _load_image_from_upload(file_data) -> Image.Image:
    try:
        if isinstance(file_data, (bytes, bytearray)):
            image_data = bytes(file_data)
        elif hasattr(file_data, "read"):
            image_data = file_data.read()
            if hasattr(file_data, "seek"):
                try:
                    file_data.seek(0)
                except Exception:
                    pass
        else:
            with open(file_data, "rb") as image_file:
                image_data = image_file.read()

        image = Image.open(io.BytesIO(image_data))
        image = ImageOps.exif_transpose(image).convert("RGBA")
        return image
    except Exception:
        return Image.new("RGBA", (768, 1024), (235, 235, 235, 255))


def _save_sample_record(record: dict):
    _append_json_record(SAMPLES_FILE, record)


def _load_sample_records() -> list:
    supabase_samples = get_tryon_samples(limit=500)
    if supabase_samples:
        return supabase_samples

    return _load_json_list(SAMPLES_FILE)


def _resolve_sample_image(entry: dict, path_key: str, url_key: str):
    image_path = entry.get(path_key)
    image_url = entry.get(url_key)

    if image_path:
        candidate_path = Path(image_path)
        if not candidate_path.is_absolute():
            candidate_path = BASE_DIR / candidate_path
        if candidate_path.exists():
            return Image.open(candidate_path).convert("RGBA")

    if image_url:
        return _load_image_from_url(image_url)

    raise ValueError(f"Sample is missing {path_key} and {url_key}")


def save_tryon_history_record(
    user_id: str,
    occasion: str,
    sample_id: str = None,
    body_image_path: str = None,
    clothing_image_path: str = None,
    tryon_image: str = None,
    model: str = None,
    clothing_analysis: dict = None,
    recommendations: dict = None,
) -> dict:
    record_id = uuid.uuid4().hex[:12]
    tryon_image_path = None
    
    # Save the base64 try-on image as a file if present
    if tryon_image and isinstance(tryon_image, str) and not tryon_image.startswith("tryon_dataset"):
        try:
            tryon_filename = f"tryon_{record_id}.png"
            target_path = IMAGES_DIR / tryon_filename
            clean_b64 = tryon_image
            if "," in clean_b64:
                clean_b64 = clean_b64.split(",")[1]
            image_data = base64.b64decode(clean_b64)
            with open(target_path, "wb") as f:
                f.write(image_data)
            tryon_image_path = f"tryon_dataset/images/{tryon_filename}"
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to save tryon history image file: {e}")

    # Build the record for history.json (without massive base64 tryon_image)
    json_record = {
        "id": record_id,
        "sample_id": sample_id,
        "user_id": user_id,
        "occasion": occasion,
        "body_image_path": body_image_path,
        "clothing_image_path": clothing_image_path,
        "tryon_image_path": tryon_image_path,
        "model": model,
        "clothing_analysis": clothing_analysis,
        "recommendations": recommendations,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _append_json_record(HISTORY_FILE, json_record)
    
    # Return record containing both the path and the base64 string for API compatibility
    return {
        **json_record,
        "tryon_image": tryon_image
    }


def _encode_image_to_base64(image: Image.Image) -> str:
    output = io.BytesIO()
    image.save(output, format="PNG")
    return base64.b64encode(output.getvalue()).decode("utf-8")


def _compose_try_on(body: Image.Image, clothing: Image.Image) -> Image.Image:
    clothing = ImageOps.contain(clothing, (int(body.width * 0.7), int(body.height * 0.45)))
    if clothing.mode != "RGBA":
        clothing = clothing.convert("RGBA")

    x = (body.width - clothing.width) // 2
    y = int(body.height * 0.18)

    output = body.copy()
    output.paste(clothing, (x, y), clothing)

    overlay = Image.new("RGBA", body.size, (255, 255, 255, 0))
    overlay.paste(clothing, (x, y), clothing)
    output = Image.alpha_composite(output, overlay)

    return output


def _load_sample_image(body_image_url, clothing_image_url, body_upload, clothing_upload):
    if body_upload is not None:
        body_image = _load_image_from_upload(body_upload)
    elif body_image_url:
        body_image = _load_image_from_url(body_image_url)
    else:
        raise ValueError("Body image is required")

    if clothing_upload is not None:
        clothing_image = _load_image_from_upload(clothing_upload)
    elif clothing_image_url:
        clothing_image = _load_image_from_url(clothing_image_url)
    else:
        raise ValueError("Clothing image is required")

    return body_image, clothing_image


def save_tryon_sample(user_id: str, category: str = None, body_image_url: str = None, clothing_image_url: str = None,
                      body_upload=None, clothing_upload=None) -> dict:
    body_image, clothing_image = _load_sample_image(body_image_url, clothing_image_url, body_upload, clothing_upload)

    sample_id = uuid.uuid4().hex[:12]
    body_filename = f"body_{sample_id}.png"
    clothing_filename = f"clothing_{sample_id}.png"
    body_path = IMAGES_DIR / body_filename
    clothing_path = IMAGES_DIR / clothing_filename

    body_image.save(body_path, format="PNG")
    clothing_image.save(clothing_path, format="PNG")

    record = {
        "id": sample_id,
        "sample_id": sample_id,
        "user_id": user_id,
        "category": category or "unknown",
        "source": "website",
        "body_image_url": body_image_url,
        "clothing_image_url": clothing_image_url,
        "body_image_path": str(body_path.relative_to(BASE_DIR)),
        "clothing_image_path": str(clothing_path.relative_to(BASE_DIR)),
    }

    if supabase is not None:
        _save_sample_record(record)
    saved_sample = add_tryon_sample(record)

    return {
        "status": "saved",
        "sample_id": sample_id,
        "body_image_path": record["body_image_path"],
        "clothing_image_path": record["clothing_image_path"],
        "supabase_sample": saved_sample,
    }


def generate_try_on(body_image_url: str = None, clothing_image_url: str = None,
                    body_upload=None, clothing_upload=None) -> dict:
    body_image, clothing_image = _load_sample_image(body_image_url, clothing_image_url, body_upload, clothing_upload)

    # Strategy: Try Advanced VTON first, then CatVTON, then trained model, then fallback composition

    # 1. Try Advanced VTON (Highest quality, IP-Adapter + Segformer)
    try:
        from services.advanced_vton import generate_tryon_with_advanced_pipeline
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("Attempting Advanced VTON inference...")
        result_image = generate_tryon_with_advanced_pipeline(body_image, clothing_image)
        if result_image is not None:
            logger.info("✓ Advanced VTON inference successful")
            return {"tryon_image": _encode_image_to_base64(result_image), "model": "advanced_vton"}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Advanced VTON inference failed: {e}, trying fallback...")

    # 2. Try CatVTON (Legacy high-quality)
    try:
        from services.catvton_service import generate_tryon_with_catvton
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("Attempting CatVTON inference...")
        result_image = generate_tryon_with_catvton(body_image, clothing_image)
        if result_image is not None:
            logger.info("✓ CatVTON inference successful")
            return {"tryon_image": _encode_image_to_base64(result_image), "model": "catvton"}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"CatVTON inference failed: {e}, trying fallback...")

    # 2. Try trained model
    try:
        from torch import no_grad
        from torchvision import transforms
        import torch
        
        if MODEL_PATH.exists():
            model = _load_tryon_model()
            result_image = _predict_with_model(model, body_image, clothing_image)
            return {"tryon_image": _encode_image_to_base64(result_image), "model": "trained"}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Trained model inference failed: {e}, using fallback...")

    # 3. Fallback to simple composition
    try_on_image = _compose_try_on(body_image, clothing_image)
    return {"tryon_image": _encode_image_to_base64(try_on_image), "model": "fallback"}


def _build_tryon_model():
    import torch
    from torch import nn

    class SimpleTryOnNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.encoder = nn.Sequential(
                nn.Conv2d(6, 32, 4, 2, 1),
                nn.ReLU(inplace=True),
                nn.Conv2d(32, 64, 4, 2, 1),
                nn.ReLU(inplace=True),
                nn.Conv2d(64, 128, 4, 2, 1),
                nn.ReLU(inplace=True),
            )
            self.decoder = nn.Sequential(
                nn.ConvTranspose2d(128, 64, 4, 2, 1),
                nn.ReLU(inplace=True),
                nn.ConvTranspose2d(64, 32, 4, 2, 1),
                nn.ReLU(inplace=True),
                nn.ConvTranspose2d(32, 3, 4, 2, 1),
                nn.Sigmoid(),
            )

        def forward(self, x):
            x = self.encoder(x)
            return self.decoder(x)

    return SimpleTryOnNet()


def _load_tryon_model():
    import torch
    model = _build_tryon_model()
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    return model


def _predict_with_model(model, body_image: Image.Image, clothing_image: Image.Image) -> Image.Image:
    from torchvision import transforms
    import torch

    size = (256, 256)
    transform = transforms.Compose([
        transforms.Resize(size),
        transforms.ToTensor(),
    ])

    body_tensor = transform(body_image.convert("RGB"))
    clothing_tensor = transform(clothing_image.convert("RGB"))
    input_tensor = torch.cat([body_tensor, clothing_tensor], dim=0).unsqueeze(0)

    with torch.no_grad():
        output_tensor = model(input_tensor).squeeze(0).clamp(0, 1)

    output_image = transforms.ToPILImage()(output_tensor.cpu())
    output_image = output_image.resize(body_image.size, Image.Resampling.LANCZOS)
    return output_image


def train_tryon_model(epochs: int = 3, batch_size: int = 2, learning_rate: float = 1e-3) -> dict:
    try:
        import torch
        from torch import nn, optim
        from torch.utils.data import DataLoader, Dataset
        from torchvision import transforms
    except ImportError:
        return {
            "status": "error",
            "message": "Install torch and torchvision to run training. Example: pip install torch torchvision",
        }

    samples = _load_sample_records()

    if not samples:
        return {"status": "error", "message": "No dataset samples found. Save try-on samples first."}

    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
    ])

    class TryOnDataset(Dataset):
        def __init__(self, records):
            self.records = records

        def __len__(self):
            return len(self.records)

        def __getitem__(self, idx):
            entry = self.records[idx]
            body = _resolve_sample_image(entry, "body_image_path", "body_image_url").convert("RGB")
            clothing = _resolve_sample_image(entry, "clothing_image_path", "clothing_image_url").convert("RGB")
            clothing = ImageOps.contain(clothing, (int(body.width * 0.7), int(body.height * 0.45)))
            composed = _compose_try_on(body.convert("RGBA"), clothing.convert("RGBA")).convert("RGB")

            body_tensor = transform(body)
            clothing_tensor = transform(clothing)
            target_tensor = transform(composed)
            return torch.cat([body_tensor, clothing_tensor], dim=0), target_tensor

    class SimpleTryOnNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.encoder = nn.Sequential(
                nn.Conv2d(6, 32, 4, 2, 1),
                nn.ReLU(inplace=True),
                nn.Conv2d(32, 64, 4, 2, 1),
                nn.ReLU(inplace=True),
                nn.Conv2d(64, 128, 4, 2, 1),
                nn.ReLU(inplace=True),
            )
            self.decoder = nn.Sequential(
                nn.ConvTranspose2d(128, 64, 4, 2, 1),
                nn.ReLU(inplace=True),
                nn.ConvTranspose2d(64, 32, 4, 2, 1),
                nn.ReLU(inplace=True),
                nn.ConvTranspose2d(32, 3, 4, 2, 1),
                nn.Sigmoid(),
            )

        def forward(self, x):
            x = self.encoder(x)
            return self.decoder(x)

    dataset = TryOnDataset(samples)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    model = SimpleTryOnNet()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.L1Loss()

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss = 0.0
        for inputs, targets in dataloader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        print(f"Epoch {epoch}/{epochs}  loss={epoch_loss / len(dataloader):.4f}")

    torch.save(model.state_dict(), MODEL_PATH)
    return {"status": "trained", "epochs": epochs, "samples": len(dataset), "model_path": str(MODEL_PATH)}
