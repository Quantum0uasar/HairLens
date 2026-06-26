import os
import json
import base64
from typing import Any, Dict

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from openai import OpenAI
from dotenv import load_dotenv

from product_service import recommend_products
from haircut_service import recommend_haircuts
from preview_service import generate_preview

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("HAIRLENS_MODEL", "gpt-4o")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

app = FastAPI(title="HairLens")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


SYSTEM_PROMPT = """
You are HairLens, a cosmetic (non-medical) hair-analysis assistant.

You receive ONE close-up photo of someone's hair. Work in this order:

STEP 1 - OBSERVE. Silently note what you actually see: curl/wave shape,
strand thickness, surface shine vs. matte, flyaways/frizz, split or rough
ends, scalp visibility, and any product/styling.

STEP 2 - CLASSIFY using the rubric below. Commit to the single best label
for each field. Do NOT default to "dry" or "damaged" unless the photo shows
real evidence (matte texture, roughness, breakage, frizz). Healthy, shiny,
well-moisturized hair is common - say so when you see it.

STEP 3 - SCORE four traits from 0-100 so results are specific, not generic:
- hydration_score: 0 = parched/brittle, 100 = glossy/well-moisturized
- damage_score: 0 = pristine, 100 = heavily damaged (split ends, breakage)
- frizz_score: 0 = smooth, 100 = very frizzy/flyaway
- shine_score: 0 = matte, 100 = mirror shine

RUBRIC:
- hair_type: straight | wavy | curly | coily
- texture: fine | medium | coarse
- hydration_level: dry | balanced | oily
- hair_condition: healthy | smooth | frizzy | damaged | brittle
- porosity: low | medium | high   (estimate from shine + how the ends look)

STEP 4 - FACE SHAPE (for haircut advice). If a face is clearly visible,
classify face_shape as one of: oval | round | square | heart | oblong |
diamond. If the face is hidden, cropped, or it's only a hair close-up, set
face_visible=false and face_shape="unknown". Never guess a face you can't see.

Return ONE JSON object only, no markdown, in EXACTLY this shape:

{
  "hair_visible": true,
  "observations": "1-2 sentences describing what you literally see in the photo",
  "hair_type": "wavy",
  "texture": "medium",
  "hydration_level": "balanced",
  "hair_condition": "healthy",
  "porosity": "medium",
  "scores": { "hydration_score": 72, "damage_score": 18, "frizz_score": 30, "shine_score": 65 },
  "face_visible": true,
  "face_shape": "oval",
  "confidence": "high | medium | low",
  "confidence_note": "short reason for the confidence level"
}

If hair is not clearly visible: set hair_visible=false, confidence="low",
and explain why in confidence_note. Never invent detail you cannot see.
"""


def _safe_json(raw: str) -> Dict[str, Any]:
    raw = (raw or "").strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _normalize(data: Dict[str, Any]) -> Dict[str, Any]:
    data.setdefault("hair_visible", False)
    data.setdefault("observations", "")
    data.setdefault("hair_type", "unknown")
    data.setdefault("texture", "unknown")
    data.setdefault("hydration_level", "unknown")
    data.setdefault("hair_condition", "unknown")
    data.setdefault("porosity", "unknown")
    data.setdefault("face_visible", False)
    data.setdefault("face_shape", "unknown")
    data.setdefault("confidence", "low")
    data.setdefault("confidence_note", "")
    scores = data.get("scores") or {}
    for k in ("hydration_score", "damage_score", "frizz_score", "shine_score"):
        try:
            scores[k] = max(0, min(100, int(scores.get(k, 50))))
        except (TypeError, ValueError):
            scores[k] = 50
    data["scores"] = scores
    return data


async def analyze_hair(image_bytes: bytes) -> Dict[str, Any]:
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    completion = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        temperature=0.5,
        max_tokens=600,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this hair photo. Return only the JSON object."},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/jpeg;base64,{image_b64}", "detail": "high"}},
                ],
            },
        ],
    )
    raw = completion.choices[0].message.content
    return _normalize(_safe_json(raw))


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if not OPENAI_API_KEY:
        return JSONResponse(status_code=500,
                            content={"error": "OPENAI_API_KEY not set in .env"})
    try:
        image_bytes = await file.read()
        analysis = await analyze_hair(image_bytes)
        products = recommend_products(analysis)
        haircuts = recommend_haircuts(analysis)
        return JSONResponse(content={"analysis": analysis,
                                     "recommendations": products,
                                     "haircuts": haircuts})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/preview")
async def preview(file: UploadFile = File(...), cut: str = Form(...)):
    if not OPENAI_API_KEY:
        return JSONResponse(status_code=500,
                            content={"error": "OPENAI_API_KEY not set in .env"})
    try:
        image_bytes = await file.read()
        data_url = generate_preview(client, image_bytes, cut)
        return JSONResponse(content={"image": data_url, "cut": cut})
    except Exception as e:
        msg = str(e)
        if "must be verified" in msg or "organization" in msg.lower():
            msg = ("Image model needs org verification. Verify once at "
                   "platform.openai.com/settings/organization/general, then retry.")
        elif "safety" in msg.lower() or "moderation" in msg.lower():
            msg = "The image model declined this edit. Try a clearer, front-facing photo."
        return JSONResponse(status_code=500, content={"error": msg})


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL}
