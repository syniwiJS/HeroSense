import cv2
import json
import numpy as np
import os
import sys
from pathlib import Path


ENEMY_TEAM_Y_START = 0
ENEMY_TEAM_Y_END   = 311
NUM_HEROES         = 5
TEMPLATE_SIZE      = (60, 60)
CONFIDENCE_THRESHOLD = 0.20


def resource_path(relative):
    # resolves paths correctly in dev and when packaged with PyInstaller
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)

TEMPLATES_DIR = Path(resource_path("templates"))


def load_templates() -> dict:
    templates = {}
    for f in sorted(TEMPLATES_DIR.glob("*.png")):
        img = cv2.imread(str(f))
        if img is not None:
            templates[f.stem] = cv2.resize(img, TEMPLATE_SIZE)
        else:
            print(f"[Detector] WARNING: could not load {f.name}")
    print(f"[Detector] {len(templates)} templates loaded")
    return templates


def extract_cards(img: np.ndarray) -> list:
    # slices the captured strip into 5 equal portrait cards
    card_h = (ENEMY_TEAM_Y_END - ENEMY_TEAM_Y_START) // NUM_HEROES
    return [img[i * card_h:(i + 1) * card_h, :] for i in range(NUM_HEROES)]


def score_match(card: np.ndarray, template: np.ndarray) -> float:
    # histogram catches color similarity, template match catches structure
    # both together are more reliable than either alone
    if card is None or card.size == 0 or template is None or template.size == 0:
        return 0.0
    c = cv2.resize(card, TEMPLATE_SIZE)
    hist_score = sum(
        cv2.compareHist(
            cv2.calcHist([c],        [ch], None, [64], [0, 256]),
            cv2.calcHist([template], [ch], None, [64], [0, 256]),
            cv2.HISTCMP_CORREL
        ) for ch in range(3)
    ) / 3.0
    _, tmatch, _, _ = cv2.minMaxLoc(
        cv2.matchTemplate(c, template, cv2.TM_CCOEFF_NORMED)
    )
    return (hist_score * 0.5) + (float(tmatch) * 0.5)


def best_match(card: np.ndarray, templates: dict) -> tuple:
    best_name, best_conf = "unknown", -1.0
    for name, tmpl in templates.items():
        s = score_match(card, tmpl)
        if s > best_conf:
            best_conf = s
            best_name = name
    if best_conf < CONFIDENCE_THRESHOLD:
        return "unknown", best_conf
    return best_name, best_conf


def detect_heroes(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot load: {image_path}")
    templates = load_templates()
    cards = extract_cards(img)
    print("[Detector] Scanning enemy team...")
    enemy_team = []
    for i, card in enumerate(cards):
        name, conf = best_match(card, templates)
        print(f"  slot {i + 1}: {name:20s}  conf={conf:.3f}")
        enemy_team.append(name)
    print(f"[Detector] Result: {enemy_team}")
    return {"enemy_team": enemy_team}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python Hero_Detector.py <screenshot.png>")
        sys.exit(1)
    result = detect_heroes(sys.argv[1])
    print(json.dumps(result, indent=2))