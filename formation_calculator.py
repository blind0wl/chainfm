# Formation Calculator Module
# This module contains logic for parsing, analyzing, and assigning players to formations.

import re

ROLE_NAME_TO_CODE = {
    # Goalkeepers
    'Goalkeeper (D)': 'GKD',
    'Sweeper Keeper (S)': 'SKS',
    'Sweeper Keeper (A)': 'SKA',
    # ... (other roles omitted for brevity)
}

def parse_formations(spec_text):
    """Parses formation specifications."""
    formations = []
    current = None
    for line in spec_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^(\\d+)\\. (.+)$', line)
        if m:
            if current:
                formations.append(current)
            current = {"name": m[2], "positions": []}
        elif current:
            pm = re.match(r'^([A-Z\/\\s]+)\\s*[–\u2013\\-]\\s*(.+)$', line)
            if pm:
                pos = pm[1].strip()
                role = pm[2].strip()
                current["positions"].append({"pos": pos, "role": role})
    if current:
        formations.append(current)
    return formations

def analyze_formations(formations, players):
    """Analyzes formations and calculates scores."""
    results = []
    for formation in formations:
        assignment = assign_players_to_formation(formation, players)
        total_score = sum(assign.get("score", 0) for assign in assignment)
        avg_score = total_score / len(formation["positions"]) if formation["positions"] else 0
        results.append({
            "formation": formation["name"],
            "avg_score": avg_score,
            "total_score": total_score,
            "assignments": assignment
        })
    return sorted(results, key=lambda x: x["avg_score"], reverse=True)

def assign_players_to_formation(formation, players):
    """Assigns players to formation positions."""
    assignments = []
    used_players = set()
    for pos in formation["positions"]:
        best_player = None
        best_score = -1
        for player in players:
            if player["name"] not in used_players:
                score = player["scores"].get(pos["role"], 0)
                if score > best_score:
                    best_score = score
                    best_player = player
        if best_player:
            used_players.add(best_player["name"])
            assignments.append({"position": pos["pos"], "role": pos["role"], "player": best_player["name"], "score": best_score})
        else:
            assignments.append({"position": pos["pos"], "role": pos["role"], "player": None, "score": 0})
    return assignments

def is_player_eligible_for_position(player, position):
    """Checks if a player is eligible for a position."""
    return position.upper() in (pos.upper() for pos in player["pos"].split(","))