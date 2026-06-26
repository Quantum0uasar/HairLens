import base64
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")

def analyze_skin_hair(image_bytes: bytes) -> dict:
    base64_image = encode_image(image_bytes)
    prompt = """
    You are a skincare and haircare analysis assistant. Analyze this photo and return ONLY a valid JSON object with this exact structure, no markdown, no code blocks, just raw JSON:
    {
      "skin_type": "oily",
      "skin_concerns": ["dryness", "uneven tone"],
      "hydration_level": "medium",
      "skin_tone": "medium",
      "hair_visible": true,
      "hair_type": "wavy",
      "hair_condition": "dry",
      "confidence_note": "Hair clearly visible, skin not visible in this photo"
    }
    Replace the values based on what you see. Only include up to 3 skin concerns. Do not diagnose medical conditions. Return raw JSON only, absolutely no markdown or triple backticks.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low"
                        }
                    }
                ]
            }
        ],
        max_tokens=500
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())