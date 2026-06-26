"""
Haircut recommender.

Maps a detected face shape to flattering cut suggestions. This is cosmetic
styling guidance only (the same kind a stylist gives), not identity detection.
Kept rule-based so results are stable and explainable.
"""
from typing import Any, Dict

CUTS: Dict[str, Dict[str, Any]] = {
    "oval": {
        "summary": "The most versatile shape — almost any cut works. Lean into what you like.",
        "styles": [
            ("Soft layers", "Adds movement without fighting your balanced proportions."),
            ("Blunt lob (long bob)", "Clean, modern, and flattering on an even jaw-to-forehead ratio."),
            ("Curtain bangs", "Frames the face while keeping length and versatility."),
        ],
        "avoid": "Heavy, straight-across fringe that hides your natural balance.",
    },
    "round": {
        "summary": "Goal: add height and length to lengthen the face.",
        "styles": [
            ("Long layers", "Vertical movement slims and elongates a rounder face."),
            ("Side part with volume on top", "Off-center lines break up width."),
            ("Textured quiff / pompadour", "Height up top draws the eye upward."),
        ],
        "avoid": "Blunt chin-length bobs and centre parts that widen the face.",
    },
    "square": {
        "summary": "Goal: soften a strong, angular jawline.",
        "styles": [
            ("Side-swept layers", "Diagonal lines soften sharp corners."),
            ("Textured waves", "Rounded movement balances a defined jaw."),
            ("Scissor-cut textured crop", "Soft, piecey ends ease the angles."),
        ],
        "avoid": "Heavy straight fringes and boxy, one-length cuts.",
    },
    "heart": {
        "summary": "Goal: balance a wider forehead with a narrower chin.",
        "styles": [
            ("Chin-length lob", "Adds width at the jaw to even out proportions."),
            ("Side-swept bangs", "Softens and narrows a broader forehead."),
            ("Layered medium cut", "Volume lower down balances the top."),
        ],
        "avoid": "Tight slicked-back styles that expose forehead width.",
    },
    "oblong": {
        "summary": "Goal: add width and avoid extra length.",
        "styles": [
            ("Blunt bob or waves", "Horizontal volume shortens a long face."),
            ("Curtain bangs / blunt fringe", "Cuts visual length at the forehead."),
            ("Layered, voluminous sides", "Width at the cheeks balances the shape."),
        ],
        "avoid": "Long, flat, one-length styles that drag the face longer.",
    },
    "diamond": {
        "summary": "Goal: soften the cheekbones and balance a narrow forehead/chin.",
        "styles": [
            ("Chin-length cut with texture", "Adds fullness where the face narrows."),
            ("Side part with soft fringe", "Widens the forehead area visually."),
            ("Textured ends", "Movement at the jaw softens sharp cheekbones."),
        ],
        "avoid": "Slicked, tight styles that emphasise wide cheekbones.",
    },
}


def recommend_haircuts(analysis: Dict[str, Any]) -> Dict[str, Any]:
    if not analysis.get("face_visible", False):
        return {}
    shape = str(analysis.get("face_shape", "")).lower()
    data = CUTS.get(shape)
    if not data:
        return {}
    return {
        "face_shape": shape,
        "summary": data["summary"],
        "styles": [{"name": n, "why": w} for n, w in data["styles"]],
        "avoid": data["avoid"],
    }
