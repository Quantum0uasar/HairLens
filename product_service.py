"""
Curated, rule-based product matcher.

Why not let the AI invent product links? Because it hallucinates dead URLs.
Here we keep a small catalog of REAL, widely sold products and pick the best
match for the analyzed hair profile. Links are honest brand/Amazon search
links, so they never 404. Swap in a live product API later if you want.
"""
from typing import Any, Dict, List
from urllib.parse import quote_plus

AMZ = "https://www.amazon.com/s?k="

# slot -> list of products tagged with which profiles they suit
CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "shampoo": [
        {"name": "Olaplex No.4 Bond Maintenance Shampoo", "price": "$30",
         "tags": ["damaged", "high", "coarse", "dry"],
         "why": "Repairs broken bonds in damaged or color-treated hair while it cleanses."},
        {"name": "Briogeo Don't Despair, Repair! Shampoo", "price": "$32",
         "tags": ["dry", "damaged", "brittle", "high"],
         "why": "Rich, sulfate-free clean for dry, stressed strands."},
        {"name": "Verb Hydrating Shampoo", "price": "$20",
         "tags": ["balanced", "wavy", "medium", "healthy"],
         "why": "Light daily hydration that won't weigh down healthy hair."},
        {"name": "Neutrogena Anti-Residue Clarifying Shampoo", "price": "$9",
         "tags": ["oily", "fine", "low"],
         "why": "Cuts oil and product buildup without stripping."},
        {"name": "SheaMoisture Coconut & Hibiscus Shampoo", "price": "$12",
         "tags": ["curly", "coily", "coarse", "dry"],
         "why": "Curl-friendly moisture for thick, textured hair."},
    ],
    "conditioner": [
        {"name": "Moroccanoil Moisture Repair Conditioner", "price": "$26",
         "tags": ["dry", "damaged", "high", "coarse"],
         "why": "Argan-oil conditioner that softens rough, thirsty ends."},
        {"name": "Verb Ghost Conditioner", "price": "$20",
         "tags": ["fine", "oily", "balanced", "low"],
         "why": "Weightless slip for fine hair that flattens easily."},
        {"name": "SheaMoisture Manuka Honey & Mafura Oil Conditioner", "price": "$13",
         "tags": ["curly", "coily", "dry", "high", "coarse"],
         "why": "Deep slip and moisture for coils that drink up product."},
        {"name": "Aussie 3 Minute Miracle", "price": "$6",
         "tags": ["wavy", "medium", "balanced", "healthy"],
         "why": "Cheap, reliable everyday softness."},
    ],
    "treatment": [
        {"name": "Olaplex No.3 Hair Perfector", "price": "$30",
         "tags": ["damaged", "brittle", "high", "frizzy"],
         "why": "At-home bond repair for breakage and over-processing."},
        {"name": "K18 Leave-In Molecular Repair Mask", "price": "$29",
         "tags": ["damaged", "high", "coarse"],
         "why": "Reverses damage from heat and color in minutes."},
        {"name": "Briogeo Don't Despair, Repair! Deep Mask", "price": "$38",
         "tags": ["dry", "brittle", "curly", "coily"],
         "why": "Weekly intensive moisture for very dry hair."},
        {"name": "Living Proof No Frizz Vanishing Oil", "price": "$28",
         "tags": ["frizzy", "wavy", "medium", "healthy"],
         "why": "Tames flyaways and adds shine without grease."},
    ],
    "scalp": [
        {"name": "The Ordinary Multi-Peptide Serum for Hair Density", "price": "$20",
         "tags": ["fine", "low", "balanced"],
         "why": "Lightweight serum aimed at thicker-looking, fuller hair."},
        {"name": "The Inkey List Caffeine Stimulating Scalp Treatment", "price": "$15",
         "tags": ["oily", "fine", "balanced", "healthy"],
         "why": "Caffeine scalp serum to support a healthy growth environment."},
        {"name": "Rosemary Mint Scalp & Hair Strengthening Oil (Mielle)", "price": "$10",
         "tags": ["dry", "curly", "coily", "coarse"],
         "why": "Popular scalp oil to nourish dry scalp and ends."},
    ],
}


def _profile_tags(analysis: Dict[str, Any]) -> List[str]:
    return [str(analysis.get(k, "")).lower() for k in
            ("hair_type", "texture", "hydration_level", "hair_condition", "porosity")]


WHEN = {
    "shampoo": "2–3 times a week. Massage into wet scalp, rinse well.",
    "conditioner": "Every wash. Smooth onto mid-lengths and ends, leave 1–2 min, rinse.",
    "treatment": "Once a week on towel-dried hair. Leave 5–10 min, then rinse.",
    "scalp": "2–3 times a week on a clean, dry scalp. Massage in, don't rinse out.",
}

HELPS = {
    "shampoo": "Cleans without stripping, so hair stays balanced.",
    "conditioner": "Adds slip and softness so hair detangles and feels smooth.",
    "treatment": "A weekly deep-repair step for stronger, less frizzy hair.",
    "scalp": "Supports a healthy scalp — the base for healthier growth.",
}


def _best(slot: str, tags: List[str]) -> Dict[str, Any]:
    items = CATALOG[slot]
    ranked = sorted(items, key=lambda p: len(set(p["tags"]) & set(tags)), reverse=True)
    pick = ranked[0]
    return {
        "name": pick["name"],
        "price": pick["price"],
        "why": pick["why"],
        "helps": HELPS[slot],
        "when": WHEN[slot],
        "link": AMZ + quote_plus(pick["name"]),
    }


def recommend_products(analysis: Dict[str, Any]) -> Dict[str, Any]:
    if not analysis.get("hair_visible", False):
        return {"haircare": {}}
    tags = _profile_tags(analysis)
    return {
        "haircare": {
            "shampoo": _best("shampoo", tags),
            "conditioner": _best("conditioner", tags),
            "treatment": _best("treatment", tags),
            "scalp": _best("scalp", tags),
        }
    }
