"""
OW2 Scout - Comp Analyzer

Classifies enemy comp and returns accurate counter suggestions.
"""

HERO_DATA = {
    # Tanks
    "dva":          {"role": "tank", "mobility": "high",   "range": "short",  "tags": ["dive"]},
    "domina":       {"role": "tank", "mobility": "medium", "range": "medium", "tags": ["brawl"]},
    "doomfist":     {"role": "tank", "mobility": "high",   "range": "short",  "tags": ["dive", "brawl"]},
    "junkerqueen":  {"role": "tank", "mobility": "medium", "range": "short",  "tags": ["brawl", "rush"]},
    "mauga":        {"role": "tank", "mobility": "low",    "range": "medium", "tags": ["brawl"]},
    "orisa":        {"role": "tank", "mobility": "low",    "range": "medium", "tags": ["poke"]},
    "ramattra":     {"role": "tank", "mobility": "low",    "range": "medium", "tags": ["brawl", "poke"]},
    "reinhardt":    {"role": "tank", "mobility": "low",    "range": "short",  "tags": ["brawl", "rush"]},
    "roadhog":      {"role": "tank", "mobility": "low",    "range": "medium", "tags": ["brawl"]},
    "sigma":        {"role": "tank", "mobility": "low",    "range": "long",   "tags": ["poke"]},
    "winston":      {"role": "tank", "mobility": "high",   "range": "short",  "tags": ["dive"]},
    "wreckingball": {"role": "tank", "mobility": "high",   "range": "short",  "tags": ["dive", "disrupt"]},
    "zarya":        {"role": "tank", "mobility": "low",    "range": "medium", "tags": ["brawl"]},
    "hazard":       {"role": "tank", "mobility": "high",   "range": "short",  "tags": ["dive", "brawl"]},

    # DPS
    "ashe":         {"role": "dps", "mobility": "medium", "range": "long",   "tags": ["poke"]},
    "bastion":      {"role": "dps", "mobility": "low",    "range": "long",   "tags": ["poke"]},
    "cassidy":      {"role": "dps", "mobility": "low",    "range": "medium", "tags": ["poke", "brawl"]},
    "echo":         {"role": "dps", "mobility": "high",   "range": "medium", "tags": ["dive", "poke"]},
    "genji":        {"role": "dps", "mobility": "high",   "range": "short",  "tags": ["dive"]},
    "hanzo":        {"role": "dps", "mobility": "medium", "range": "long",   "tags": ["poke"]},
    "junkrat":      {"role": "dps", "mobility": "low",    "range": "medium", "tags": ["brawl", "poke"]},
    "mei":          {"role": "dps", "mobility": "low",    "range": "short",  "tags": ["brawl", "disrupt"]},
    "pharah":       {"role": "dps", "mobility": "high",   "range": "medium", "tags": ["poke"]},
    "reaper":       {"role": "dps", "mobility": "medium", "range": "short",  "tags": ["brawl"]},
    "sojourn":      {"role": "dps", "mobility": "high",   "range": "long",   "tags": ["poke"]},
    "soldier76":    {"role": "dps", "mobility": "medium", "range": "long",   "tags": ["poke", "brawl"]},
    "sombra":       {"role": "dps", "mobility": "high",   "range": "short",  "tags": ["dive", "disrupt"]},
    "symmetra":     {"role": "dps", "mobility": "low",    "range": "short",  "tags": ["brawl"]},
    "torbjorn":     {"role": "dps", "mobility": "low",    "range": "medium", "tags": ["poke"]},
    "tracer":       {"role": "dps", "mobility": "high",   "range": "short",  "tags": ["dive"]},
    "widowmaker":   {"role": "dps", "mobility": "medium", "range": "long",   "tags": ["poke"]},
    "venture":      {"role": "dps", "mobility": "high",   "range": "short",  "tags": ["dive", "brawl"]},
    "freja":        {"role": "dps", "mobility": "high",   "range": "medium", "tags": ["dive", "poke"]},
    "vendetta":     {"role": "dps", "mobility": "high",   "range": "short",  "tags": ["dive", "brawl"]},

    # Supports
    "ana":          {"role": "support", "mobility": "low",    "range": "long",   "tags": ["poke", "brawl"]},
    "baptiste":     {"role": "support", "mobility": "medium", "range": "long",   "tags": ["poke", "brawl"]},
    "brigitte":     {"role": "support", "mobility": "low",    "range": "short",  "tags": ["brawl"]},
    "illari":       {"role": "support", "mobility": "medium", "range": "long",   "tags": ["poke"]},
    "kiriko":       {"role": "support", "mobility": "high",   "range": "medium", "tags": ["brawl", "poke"]},  
    "lifeweaver":   {"role": "support", "mobility": "medium", "range": "medium", "tags": ["poke", "brawl"]},
    "lucio":        {"role": "support", "mobility": "high",   "range": "short",  "tags": ["rush", "brawl"]},
    "mercy":        {"role": "support", "mobility": "high",   "range": "medium", "tags": ["poke", "brawl"]},
    "moira":        {"role": "support", "mobility": "medium", "range": "short",  "tags": ["brawl"]},
    "zenyatta":     {"role": "support", "mobility": "low",    "range": "long",   "tags": ["poke"]},
    "juno":         {"role": "support", "mobility": "high",   "range": "medium", "tags": ["rush", "brawl"]},
    "wuyang":       {"role": "support", "mobility": "medium", "range": "medium", "tags": ["poke", "brawl"]},
    "emre":         {"role": "dps",     "mobility": "medium", "range": "medium", "tags": ["poke"]},
}

# Specific hero counters
# Used to add/remove heroes from generic suggestions based on who's actually on enemy team
SPECIFIC_COUNTERS = {
    "reinhardt": {
        "play_add":  ["bastion", "reaper", "junkrat", "pharah"],  # melt his shield
        "avoid_add": ["reinhardt", "symmetra"],                    # mirror rein is fine but symm can't poke
    },
    "orisa":     {"play_add": ["reaper", "bastion", "sombra"], "avoid_add": ["pharah"]},
    "winston":   {"play_add": ["cassidy", "symmetra", "torbjorn"], "avoid_add": ["genji", "tracer"]},
    "dva":       {"play_add": ["bastion", "sombra", "zarya"], "avoid_add": []},
    "roadhog":   {"play_add": ["sombra", "cassidy", "ana"], "avoid_add": []},
    "mauga":     {"play_add": ["sombra", "ana", "reaper"], "avoid_add": ["pharah", "echo"]},
    "zarya":     {"play_add": ["sombra", "reaper", "moira"], "avoid_add": ["pharah"]},
    "genji":     {"play_add": ["cassidy", "brigitte", "ana"], "avoid_add": []},
    "tracer":    {"play_add": ["cassidy", "brigitte", "symmetra"], "avoid_add": []},
    "pharah":    {"play_add": ["soldier76", "cassidy", "widowmaker"], "avoid_add": ["junkrat", "mercy"]},
    "bastion":   {"play_add": ["sombra", "genji", "pharah"], "avoid_add": []},
    "symmetra":  {"play_add": ["pharah", "echo", "soldier76"], "avoid_add": []},
    "widowmaker":{"play_add": ["winston", "sombra", "dva"], "avoid_add": ["widowmaker"]},
    "sombra":    {"play_add": ["lucio", "kiriko", "brigitte"], "avoid_add": []},
    "ana":       {"play_add": ["dva", "winston", "sombra"], "avoid_add": []},
    "zenyatta":  {"play_add": ["winston", "dva", "tracer"], "avoid_add": []},
}

COMP_COUNTERS = {
    "dive": {
        "description": "High-mobility flankers targeting your backline. Use CC and hitscan to shut them down.",
        "play":  ["cassidy", "soldier76", "ana", "brigitte", "torbjorn", "zenyatta", "sigma", "orisa"],
        "avoid": ["widowmaker", "hanzo", "zenyatta", "symmetra"],
    },
    "poke": {
        "description": "Long-range sustained damage. Get in their face or match their range.",
        "play":  ["winston", "dva", "genji", "tracer", "lucio", "pharah", "reaper", "wreckingball"],
        "avoid": ["reinhardt", "roadhog", "torbjorn"],
    },
    "brawl": {
        "description": "Short-range high-sustain brawl. Keep distance, poke them out, burst them down.",
        "play":  ["bastion", "soldier76", "ashe", "pharah", "junkrat", "zenyatta", "sigma", "orisa"],
        "avoid": ["reaper", "reinhardt", "moira", "symmetra"],
    },
    "rush": {
        "description": "Fast all-in aggression. Slow them with CC and area denial before they engage.",
        "play":  ["mei", "junkrat", "cassidy", "ana", "sigma", "orisa", "torbjorn"],
        "avoid": ["widowmaker", "zenyatta", "bastion"],
    },
    "disrupt": {
        "description": "Heavy CC and off-angles. Stay grouped, focus targets fast, use cleanse supports.",
        "play":  ["soldier76", "cassidy", "lucio", "kiriko", "reinhardt", "zarya"],
        "avoid": ["widowmaker", "hanzo", "lifeweaver"],
    },
    "mixed": {
        "description": "Flexible comp — no dominant archetype. Play to your strengths.",
        "play":  ["soldier76", "ana", "lucio", "dva", "sigma"],
        "avoid": [],
    },
}


def classify_comp(heroes: list) -> str:
    tag_scores = {"dive": 0, "poke": 0, "brawl": 0, "rush": 0, "disrupt": 0}

    for hero in heroes:
        key = hero.lower().replace(": ", "").replace(" ", "").replace(".", "")
        data = HERO_DATA.get(key)
        if not data:
            continue
        for tag in data["tags"]:
            if tag in tag_scores:
                tag_scores[tag] += 1

    # Tank is the biggest indicator — weight it double
    for hero in heroes:
        key = hero.lower().replace(": ", "").replace(" ", "").replace(".", "")
        data = HERO_DATA.get(key)
        if data and data["role"] == "tank":
            for tag in data["tags"]:
                if tag in tag_scores:
                    tag_scores[tag] += 1  # extra weight for tank

    best_comp  = max(tag_scores, key=tag_scores.get)
    best_score = tag_scores[best_comp]
    return best_comp if best_score >= 2 else "mixed"


def analyze_comp(detection_result: dict) -> dict:
    enemy_heroes = [h for h in detection_result.get("enemy_team", []) if h != "unknown"]

    comp_type = classify_comp(enemy_heroes)
    counters  = COMP_COUNTERS[comp_type]

    play  = list(counters["play"])
    avoid = list(counters["avoid"])

    # Apply specific hero adjustments
    for hero in enemy_heroes:
        key = hero.lower().replace(": ", "").replace(" ", "").replace(".", "")
        specific = SPECIFIC_COUNTERS.get(key, {})
        for h in specific.get("play_add", []):
            if h not in play:
                play.insert(0, h)   # prepend so specific counters show first
        for h in specific.get("avoid_add", []):
            if h not in avoid:
                avoid.append(h)

    # Remove duplicates while preserving order
    seen = set()
    play  = [h for h in play  if not (h in seen or seen.add(h))]
    seen  = set()
    avoid = [h for h in avoid if not (h in seen or seen.add(h))]

    # Don't suggest heroes that are on the enemy team
    play  = [h for h in play  if h not in enemy_heroes][:8]
    avoid = avoid[:6]
    # Remove any hero that appears in both lists — play takes priority
    avoid = [h for h in avoid if h not in play]

    result = {
        "enemy_comp":   comp_type,
        "enemy_heroes": enemy_heroes,
        "description":  counters["description"],
        "play":         play,
        "avoid":        avoid,
    }

    print(f"\n[Analyzer] Enemy comp:  {comp_type.upper()}")
    print(f"[Analyzer] {counters['description']}")
    print(f"[Analyzer] Play:  {play}")
    print(f"[Analyzer] Avoid: {avoid}")
    return result


if __name__ == "__main__":
    tests = [
        {"label": "Rein/Cassidy/Kiriko/Baptiste/Soldier76 (your case)",
         "enemy_team": ["reinhardt", "cassidy", "kiriko", "baptiste", "soldier76"]},
        {"label": "Dive comp",
         "enemy_team": ["winston", "genji", "tracer", "lucio", "kiriko"]},
        {"label": "Poke comp",
         "enemy_team": ["sigma", "hanzo", "widowmaker", "ana", "baptiste"]},
        {"label": "Brawl comp",
         "enemy_team": ["reinhardt", "reaper", "junkrat", "moira", "lucio"]},
    ]
    for t in tests:
        print(f"\n{'='*55}\nTEST: {t['label']}")
        analyze_comp({"your_team": [], "enemy_team": t["enemy_team"]})