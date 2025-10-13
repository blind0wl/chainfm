# Formation Calculator Module
# This module contains logic for parsing, analyzing, and assigning players to formations.

import re
from bs4 import BeautifulSoup

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
    """Analyze formations and rank them based on player suitability."""
    results = []

    for formation in formations:
        total_score = 0
        valid_positions = 0
        assignments = []

        for pos in formation["positions"]:
            best_player = None
            best_score = -1

            for player in players:
                # Player's Pos field can contain multiple comma-separated entries (e.g. 'D (L), M (C)').
                # Normalize both the formation position and each player position entry for robust matching
                def normalize_position(s):
                    if not s:
                        return ""
                    # Remove spaces and parentheses, uppercase for case-insensitive compare
                    return s.replace(' ', '').replace('(', '').replace(')', '').upper()

                form_pos_norm = normalize_position(pos.get("position", ""))
                player_pos_field = player.get("Pos") or player.get("pos") or player.get("Position") or ""
                matched = False
                for ppart in [p.strip() for p in player_pos_field.split(',') if p.strip()]:
                    if form_pos_norm == normalize_position(ppart):
                        matched = True
                        break

                if matched:
                    # Role columns should exist in player dict; default to 0 if missing
                    try:
                        score = float(player.get(pos["role"], 0))
                    except Exception:
                        score = 0.0
                    if score > best_score:
                        best_score = score
                        best_player = player

            if best_player:
                total_score += best_score
                valid_positions += 1
                assignments.append({"position": pos["position"], "role": pos["role"], "player": best_player.get("Player") or best_player.get("name"), "score": best_score})
            else:
                assignments.append({"position": pos["position"], "role": pos["role"], "player": None, "score": 0})

        avg_score = total_score / len(formation["positions"]) if formation["positions"] else 0
        results.append({"formation": formation["name"], "avg_score": avg_score, "total_score": total_score, "valid_positions": valid_positions, "assignments": assignments})

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

def extract_player_data(html_file):
    """Extract player data from the HTML file."""
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    table = soup.find('table', {'id': 'playerTable'})
    players = []

    if table:
        headers = [th.text.strip() for th in table.find_all('th')]
        rows = table.find('tbody').find_all('tr')

        for row in rows:
            cells = row.find_all('td')
            player = {headers[i]: cells[i].text.strip() for i in range(len(cells))}
            players.append(player)

    return players

def extract_formation_data(html_file):
    """Extract formation data from the HTML file."""
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    textarea = soup.find('textarea', {'id': 'formationSpec'})
    if textarea:
        return textarea.text.strip()

    return ""

def parse_formations_file(file_path):
    """Parse the formations.txt file to retrieve formation details."""
    formations = []
    with open(file_path, 'r', encoding='utf-8') as file:
        current_formation = None

        for line in file:
            line = line.strip()
            if not line:
                continue

            if line[0].isdigit() and '.' in line:
                if current_formation:
                    formations.append(current_formation)
                current_formation = {"name": line, "positions": []}
            elif '=' in line and current_formation:
                position, role = map(str.strip, line.split('='))
                current_formation["positions"].append({"position": position, "role": role})

        if current_formation:
            formations.append(current_formation)

    return formations