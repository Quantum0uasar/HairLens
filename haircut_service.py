"""
Haircut recommender — gendered style sets with a large option pool.

The vision model estimates a styling category (feminine / masculine / unclear)
ONLY to choose which menu to show by default. It is not an identity claim, and
the UI lets the user switch freely between Women's and Men's cuts. This is
cosmetic styling guidance, like a salon's lookbook.
"""
from typing import Any, Dict, List, Tuple

SHAPE_INFO: Dict[str, Dict[str, str]] = {
    "oval":    {"summary": "Versatile — almost anything works. Pick what you like.",
                "avoid": "Heavy straight-across fringe that hides your balance."},
    "round":   {"summary": "Add height and length to lengthen the face.",
                "avoid": "Blunt chin-length cuts and centre parts that widen the face."},
    "square":  {"summary": "Soften the strong, angular jawline.",
                "avoid": "Boxy one-length cuts and heavy straight fringes."},
    "heart":   {"summary": "Balance a wider forehead with a narrower chin.",
                "avoid": "Tight slicked-back styles that expose forehead width."},
    "oblong":  {"summary": "Add width and avoid extra length.",
                "avoid": "Long, flat, one-length styles that add length."},
    "diamond": {"summary": "Soften the cheekbones; balance forehead and chin.",
                "avoid": "Slicked, tight styles that emphasise wide cheekbones."},
}

WOMEN: Dict[str, List[Tuple[str, str]]] = {
    "oval": [
        ("Long layers", "Movement and softness that suit balanced proportions."),
        ("Blunt lob (long bob)", "Clean, modern, and flattering on an even face."),
        ("Curtain bangs", "Frames the face while keeping length."),
        ("Beachy waves", "Effortless texture that adds body."),
        ("Sleek straight bob", "Sharp and polished for a put-together look."),
        ("Layered pixie", "Bold, low-maintenance, and shows off features."),
    ],
    "round": [
        ("Long layers", "Vertical movement slims and elongates."),
        ("Side-swept bangs", "Diagonal lines break up width."),
        ("Long bob below the chin", "Length past the chin lengthens the face."),
        ("Face-framing layers", "Slimming pieces around the cheeks."),
        ("Voluminous blowout", "Height on top draws the eye upward."),
        ("Deep side part", "Off-centre lines add length and asymmetry."),
    ],
    "square": [
        ("Soft beachy waves", "Rounded movement balances a defined jaw."),
        ("Side-swept layers", "Diagonal lines soften sharp corners."),
        ("Wispy curtain bangs", "Softens the forehead and angles."),
        ("Textured lob", "Piecey ends ease a strong jawline."),
        ("Long layered cut", "Length and layers round out the shape."),
        ("Side part with soft fringe", "Breaks up symmetry for a softer look."),
    ],
    "heart": [
        ("Chin-length lob", "Adds width at the jaw to balance the chin."),
        ("Side-swept bangs", "Softens and narrows a broader forehead."),
        ("Soft waves at the jaw", "Volume lower down evens proportions."),
        ("Layered mid-length", "Fullness toward the ends balances the top."),
        ("Deep side part", "Reduces forehead width visually."),
        ("Textured ends bob", "Movement at the jaw widens the lower face."),
    ],
    "oblong": [
        ("Blunt bob", "Horizontal weight shortens a long face."),
        ("Soft waves", "Width at the sides balances length."),
        ("Curtain bangs", "Cuts visual length at the forehead."),
        ("Blunt fringe", "A strong fringe shortens the face."),
        ("Voluminous layers", "Body at the cheeks adds width."),
        ("Shoulder-length cut", "Avoids the dragging effect of very long hair."),
    ],
    "diamond": [
        ("Chin-length bob", "Adds fullness where the face narrows."),
        ("Side part with fringe", "Widens the forehead area visually."),
        ("Soft layers at the jaw", "Softens sharp cheekbones."),
        ("Curtain bangs", "Balances a narrow forehead."),
        ("Wavy lob", "Texture at the jaw rounds the shape."),
        ("Textured mid-length", "Movement softens angular cheekbones."),
    ],
}

MEN: Dict[str, List[Tuple[str, str]]] = {
    "oval": [
        ("Classic taper", "Clean, timeless, works with most features."),
        ("Textured crop", "Modern, low effort, adds a bit of edge."),
        ("Side part", "Sharp and professional."),
        ("Quiff", "Height and volume up front."),
        ("Medium swept-back", "Relaxed length that suits a balanced face."),
        ("Buzz cut", "Minimal, confident, easy to maintain."),
    ],
    "round": [
        ("Pompadour", "Height up top lengthens a rounder face."),
        ("High fade with volume", "Tight sides slim, volume adds length."),
        ("Faux hawk", "Centre height draws the eye upward."),
        ("Spiky textured top", "Vertical texture elongates."),
        ("Undercut with quiff", "Sharp contrast plus height."),
        ("Side part with height", "Asymmetry and lift break up width."),
    ],
    "square": [
        ("Textured crop", "Soft, piecey top eases strong angles."),
        ("Crew cut", "Clean and balanced on a defined jaw."),
        ("Short quiff", "A little height without harsh lines."),
        ("Classic taper", "Neat and versatile."),
        ("Buzz cut", "Leans into a strong, masculine jaw."),
        ("Side part", "Adds a softer diagonal line."),
    ],
    "heart": [
        ("Medium length with fringe", "Width lower down balances the chin."),
        ("Textured fringe", "Softens a broader forehead."),
        ("Side-swept", "Reduces forehead width visually."),
        ("Layered medium cut", "Fullness toward the jaw evens proportions."),
        ("Mid fade with texture", "Keeps weight where it flatters."),
        ("Loose quiff", "Soft height without exposing the forehead."),
    ],
    "oblong": [
        ("Forward-styled crop", "Fringe shortens a long face."),
        ("Textured crop with fringe", "Cuts visual length at the forehead."),
        ("Caesar cut", "Short fringe is ideal for longer faces."),
        ("Low fade with fringe", "Keeps height down, width up."),
        ("Side part, low height", "Avoids adding length on top."),
        ("Medium textured sides", "Width at the cheeks balances the shape."),
    ],
    "diamond": [
        ("Textured fringe", "Adds width at the forehead."),
        ("Side part with fringe", "Balances narrow forehead and chin."),
        ("Volume on the sides", "Softens prominent cheekbones."),
        ("Layered crop", "Movement eases sharp angles."),
        ("Brushed-forward style", "Fills the narrower forehead."),
        ("Low fade with texture", "Keeps balance around the cheekbones."),
    ],
}


def _opts(table: Dict[str, List[Tuple[str, str]]], shape: str) -> List[Dict[str, str]]:
    rows = table.get(shape) or table["oval"]
    return [{"name": n, "why": w} for n, w in rows]


def recommend_haircuts(analysis: Dict[str, Any]) -> Dict[str, Any]:
    if not analysis.get("face_visible", False):
        return {}
    shape = str(analysis.get("face_shape", "")).lower()
    if shape not in SHAPE_INFO:
        shape = "oval"
    presentation = str(analysis.get("presentation", "unclear")).lower()
    default_tab = "men" if presentation == "masculine" else "women"
    info = SHAPE_INFO[shape]
    return {
        "face_shape": shape,
        "detected": presentation,
        "default_tab": default_tab,
        "summary": info["summary"],
        "avoid": info["avoid"],
        "options": {
            "women": _opts(WOMEN, shape),
            "men": _opts(MEN, shape),
        },
    }
