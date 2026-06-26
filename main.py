from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from analyzer import analyze_skin_hair
from recommender import get_recommendations

app = FastAPI(title="GlowScan API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DISCLAIMER = (
    "⚠️ This is an AI-generated suggestion only. Results may vary. "
    "Please consult a licensed dermatologist or aesthetician before changing "
    "your skincare routine. This app can make mistakes."
)

@app.get("/")
def root():
    return {"status": "GlowScan API is live 🌿"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    image_bytes = await file.read()
    analysis = analyze_skin_hair(image_bytes)
    recommendations = get_recommendations(
        analysis.get("skin_type", "normal"),
        analysis.get("hair_condition", "healthy")
    )
    return {
        "analysis": analysis,
        "recommendations": recommendations,
        "disclaimer": DISCLAIMER
    }