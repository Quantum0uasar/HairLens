# products.py

PRODUCTS = {
    "normal": [
        "Gentle gel cleanser",
        "Lightweight daily moisturizer",
        "Broad-spectrum SPF 30 sunscreen",
    ],
    "dry": [
        "Cream-based hydrating cleanser",
        "Rich moisturizer with hyaluronic acid",
        "Facial oil for nighttime",
        "Broad-spectrum SPF 30 sunscreen",
    ],
    "oily": [
        "Foaming cleanser with salicylic acid",
        "Oil-free gel moisturizer",
        "Niacinamide serum",
        "Mattifying SPF 30 sunscreen",
    ],
    "combination": [
        "Balancing gel cleanser",
        "Lightweight moisturizer",
        "Niacinamide serum for T-zone",
        "Broad-spectrum SPF 30 sunscreen",
    ],
    "sensitive": [
        "Fragrance-free gentle cleanser",
        "Soothing moisturizer with ceramides",
        "Mineral SPF 30 sunscreen",
    ],
}

HAIR_PRODUCTS = {
    "dry": [
        "Hydrating sulfate-free shampoo",
        "Deep conditioning mask (weekly)",
        "Leave-in argan oil treatment",
    ],
    "oily": [
        "Clarifying shampoo",
        "Lightweight conditioner (ends only)",
        "Dry shampoo for between washes",
    ],
    "damaged": [
        "Bond-repair shampoo",
        "Protein treatment (bi-weekly)",
        "Heat protectant spray",
    ],
    "normal": [
        "Balancing daily shampoo",
        "Moisturizing conditioner",
        "Weekly nourishing mask",
    ],
}


def get_recommendations(skin_type: str, hair_condition: str) -> dict:
    skin_recs = PRODUCTS.get(skin_type, PRODUCTS["normal"])
    hair_recs = HAIR_PRODUCTS.get(hair_condition, HAIR_PRODUCTS["normal"])
    return {"skincare": skin_recs, "haircare": hair_recs}