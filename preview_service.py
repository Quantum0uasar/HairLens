"""
Haircut preview generator (virtual try-on on the user's own photo).

Uses input_fidelity="high" so the person's FACE is preserved across the edit
(default is "low", which lets the face drift). Requires API Organization
Verification for the image model.
"""
import os
from typing import Optional

from image_utils import to_png_buffer

IMAGE_MODEL = os.getenv("HAIRLENS_IMAGE_MODEL", "gpt-image-1")
IMAGE_QUALITY = os.getenv("HAIRLENS_IMAGE_QUALITY", "medium")  # low | medium | high


def generate_preview(client, image_bytes: bytes, cut_name: str) -> Optional[str]:
    photo = to_png_buffer(image_bytes)
    prompt = (
        f"Change ONLY this person's hairstyle to a '{cut_name}'. "
        "Keep everything else identical: the exact same face, facial features, "
        "bone structure, skin tone, eye colour, eyebrows, expression, apparent "
        "age, makeup, clothing, lighting, framing, and background. Do not "
        "beautify, slim, age, or otherwise alter the face. The person must "
        "stay clearly recognizable as the same individual. Photorealistic."
    )
    kwargs = dict(
        model=IMAGE_MODEL,
        image=photo,
        prompt=prompt,
        size="1024x1536",
        quality=IMAGE_QUALITY,
        n=1,
    )
    if not IMAGE_MODEL.startswith("gpt-image-2"):
        kwargs["input_fidelity"] = "high"

    result = client.images.edit(**kwargs)
    return f"data:image/png;base64,{result.data[0].b64_json}"
