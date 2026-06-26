"""
Haircut preview generator.

Takes the user's own uploaded photo and edits it to show a requested haircut,
using OpenAI's image model (gpt-image-1 by default). This is a 'virtual try-on'
on the user's own image. Output is clearly labeled an AI visualization.

Setup note: the image model requires API Organization Verification at
platform.openai.com/settings/organization/general (one-time).
"""
import io
import os
from typing import Optional

from PIL import Image

IMAGE_MODEL = os.getenv("HAIRLENS_IMAGE_MODEL", "gpt-image-1")
IMAGE_QUALITY = os.getenv("HAIRLENS_IMAGE_QUALITY", "medium")  # low | medium | high


def _to_png(image_bytes: bytes) -> io.BytesIO:
    """Normalize any uploaded format to PNG so the edit endpoint is happy."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    buf.name = "photo.png"
    return buf


def generate_preview(client, image_bytes: bytes, cut_name: str) -> Optional[str]:
    """Return a data: URL of the preview image, or raise with a clear message."""
    photo = _to_png(image_bytes)
    prompt = (
        f"Photorealistic edit of this exact person now wearing a '{cut_name}' "
        "hairstyle. Keep their face, identity, skin tone, and facial features "
        "completely unchanged - only change the hair. Clean head-and-shoulders "
        "portrait, natural lighting, neutral background."
    )
    result = client.images.edit(
        model=IMAGE_MODEL,
        image=photo,
        prompt=prompt,
        size="1024x1536",
        quality=IMAGE_QUALITY,
        n=1,
    )
    b64 = result.data[0].b64_json
    return f"data:image/png;base64,{b64}"
