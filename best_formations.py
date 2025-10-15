# Best Formations Runner
# This script uses the formation_calculator module to compute and display the best formations.

from formation_calculator import extract_player_data, extract_formation_data, parse_formations_file, analyze_formations
from collections import defaultdict
import json
import os
import argparse

def get_latest_analysis_file():
    """Retrieve the latest analysis file based on modification time."""
    analysis_files = [f for f in os.listdir('.') if f.startswith('fm_analysis_') and f.endswith('.html')]
    if not analysis_files:
        raise FileNotFoundError("No analysis files found.")
    latest_file = max(analysis_files, key=os.path.getmtime)
    return latest_file

def run_best_formations(target_formation_substring: str = None):
    """Run the best formations computation and display results."""
    html_file = get_latest_analysis_file()
    print(f"Using the latest analysis file: {html_file}")
    formations_file = "formations.txt"

    # Extract data
    players = extract_player_data(html_file)
    formation_text = extract_formation_data(html_file)
    formations = parse_formations_file(formations_file)

    # Extract players and their positions from the HTML data
    # Helper to normalize positions for matching (removes spaces/parentheses, uppercase)
    def normalize_position(s: str) -> str:
        if not s:
            return ""
        return s.replace(' ', '').replace('(', '').replace(')', '').upper()

    player_positions = defaultdict(list)
    for player_data in players:
        player_name = player_data.get('Player') or player_data.get('name') or player_data.get('Name')
        pos_field = player_data.get('Pos') or player_data.get('pos') or player_data.get('Position') or ''
        tokens = [p.strip() for p in pos_field.split(',') if p.strip()]
        norm_positions = set()
        for token in tokens:
            # Handle slashes like D/WB (R)
            if '/' in token:
                parts = [p.strip() for p in token.split('/')]
                if '(' in token and ')' in token:
                    paren_part = token[token.find('(')+1:token.find(')')].strip()
                    for part in parts:
                        if '(' in part and ')' in part:
                            norm_positions.add(normalize_position(part))
                        else:
                            norm_positions.add(normalize_position(f"{part} ({paren_part})"))
                else:
                    for part in parts:
                        norm_positions.add(normalize_position(part))
            elif '(' in token and ')' in token:
                base = token.split('(')[0].strip()
                sub_positions = token.split('(')[1].split(')')[0]
                for sub_pos in sub_positions:
                    norm_positions.add(normalize_position(f"{base} ({sub_pos})"))
            else:
                norm_positions.add(normalize_position(token))

        player_positions[player_name] = list(norm_positions)

    # Create a dictionary keyed by player names for quick lookups
    player_data_dict = {player['Player']: player for player in players}

    # Function to find the best available player for a position
    def find_best_player_for_position(position, role, used_players):
        eligible_players = []
        # Normalize requested formation position and compare against normalized player positions
        form_pos_norm = normalize_position(position)
        # Helper: parse a normalized token into (base, side) where side is one of 'L','R','C' or ''
        def parse_token(tok: str):
            if not tok:
                return '', ''
            side = ''
            if tok.endswith('L') or tok.endswith('R') or tok.endswith('C'):
                side = tok[-1]
                base = tok[:-1]
            else:
                base = tok
            return base, side

        # Compatibility rules: map formation base -> acceptable player bases
        COMPATIBILITY = {
            'D': {'D', 'WB', 'LWB', 'RWB', 'CB', 'LB', 'RB'},
            # allow M positions to cover AM/CM etc.
            'M': {'M', 'AM', 'CM', 'DM', 'MC'},
            'ST': {'ST', 'CF', 'F', 'STR'},
            # fallback: treat equal bases as compatible
        }

        def is_compatible(form_tok, player_tok):
            fbase, fside = parse_token(form_tok)
            pbase, pside = parse_token(player_tok)

            # If either base empty, require direct match
            if not fbase or not pbase:
                return form_tok == player_tok

            # If sides are specified and conflict, not compatible
            if fside and pside and fside != pside:
                return False

            # Direct base equality
            if fbase == pbase:
                return True

            # Check compatibility mapping
            allowed = COMPATIBILITY.get(fbase)
            if allowed:
                return pbase in allowed

            # Last resort: accept only tight suffix matches where one base is the other's base
            # with a single side char appended (e.g., ST <-> STC, D <-> DL)
            if (pbase.startswith(fbase) and len(pbase) == len(fbase) + 1 and pbase[-1] in ('L','R','C')):
                return True
            if (fbase.startswith(pbase) and len(fbase) == len(pbase) + 1 and fbase[-1] in ('L','R','C')):
                return True

            return False

        for player, positions in player_positions.items():
            if player not in used_players:
                # check if any of the player's normalized tokens are compatible
                matched = False
                for ptok in positions:
                    if is_compatible(form_pos_norm, ptok):
                        matched = True
                        break
                if matched:
                    try:
                        role_score = float(player_data_dict.get(player, {}).get(role, 0))  # Get the role score, default to 0
                    except Exception:
                        role_score = 0.0
                    eligible_players.append((player, role_score))

        if eligible_players:
            # Sort players by their role score in descending order
            eligible_players.sort(key=lambda x: x[1], reverse=True)
            
            # Return the best player (highest score)
            best_player = eligible_players[0][0]
            return best_player

        return None

    # Analyze formations
    results = analyze_formations(formations, players)
    
    # Calculate total scores for each formation
    formation_scores = []
    
    for result in results:
        # Assign players to positions in the formation using fresh player tracking
        assignment_used_players = set()
        corrected_assignments = []
        total_score = 0
        
        for assignment in result['assignments']:
            position = assignment['position']
            role = assignment['role']
            best_player = find_best_player_for_position(position, role, assignment_used_players)
            if best_player:
                assignment_used_players.add(best_player)
                role_score = float(player_data_dict.get(best_player, {}).get(role, 0))
                corrected_assignments.append({
                    'position': position,
                    'role': role,
                    'player': best_player,
                    'score': role_score
                })
                total_score += role_score
            else:
                pass  # No available player
                corrected_assignments.append({
                    'position': position,
                    'role': role,
                    'player': None,
                    'score': 0
                })
        
        formation_scores.append({
            'formation': result['formation'],
            'total_score': total_score,
            'assignments': corrected_assignments
        })
    
    # Sort by total score (descending)
    formation_scores.sort(key=lambda x: x['total_score'], reverse=True)

    # If a target formation substring is provided, filter to matching formation(s)
    if target_formation_substring:
        substr = target_formation_substring.lower()
        filtered = [f for f in formation_scores if substr in f['formation'].lower()]
        if not filtered:
            print(f"No formations matched '{target_formation_substring}' — showing top results instead.")
            top_5_formations = formation_scores[:5]
        else:
            top_5_formations = filtered
    else:
        # Take top 5 overall
        top_5_formations = formation_scores[:5]
    # Print results for the selected/top formations
    print("🏆 TOP 5 FORMATIONS BY TOTAL SCORE")
    print("=" * 50)

    for i, formation_data in enumerate(top_5_formations, 1):
        total_score = formation_data['total_score']
        corrected_assignments = formation_data['assignments']

        # Clean summary
        print(f"\n#{i}. {formation_data['formation']}")
        print(f"📊 Total Score: {total_score:.2f}")
        print("👥 Selected XI:")
        print("-" * 40)
        # Table header for clarity
        print(f"{ 'Position (Role)':20} | { 'Player':20} | Score")
        print("-" * 40)
        for assignment in corrected_assignments:
            if assignment['player'] and assignment['score'] > 0:
                position = assignment['position']
                role = assignment['role']
                player = assignment['player']
                score = assignment['score']
                position_role = f"{position} ({role})"
                print(f"{position_role:20} | {player:20} | {score:.1f}")
        print("-" * 40)
        assigned_count = len([a for a in corrected_assignments if a['player'] is not None])
        if assigned_count > 0:
            print(f"Average Score: {total_score/assigned_count:.2f}")

        if i < len(top_5_formations):  # Don't print separator after last formation
            print("=" * 50)

    # Final summary table
    print("\n\n🎯 QUICK SUMMARY - TOP 5 FORMATIONS")
    print("=" * 70)
    print(f"{'Rank':<4} | {'Formation':<35} | {'Total Score':<10} | {'Avg Score':<9}")
    print("-" * 70)

    for i, formation_data in enumerate(top_5_formations, 1):
        formation_name = formation_data['formation']
        total_score = formation_data['total_score']
        assigned_count = len([a for a in formation_data['assignments'] if a['player'] is not None])
        avg_score = total_score/assigned_count if assigned_count > 0 else 0

        print(f"#{i:<3} | {formation_name:<35} | {total_score:<10.2f}  | {avg_score:<9.2f}")

    print("=" * 70)

    # Debugging: Check why no players are available for certain positions (only if needed)
    unassigned_positions = [assignment for assignment in corrected_assignments if assignment['player'] is None]
    if unassigned_positions:
        print("\nDebugging player eligibility for unassigned positions:")
        for assignment in unassigned_positions:
            position = assignment['position']
            role = assignment['role']
            print(f"No player assigned for {position} ({role}). Checking eligible players...")
            for player, positions in player_positions.items():
                if player not in assignment_used_players and position in positions:
                    score = float(player_data_dict.get(player, {}).get(role, 0))
                    print(f"  {player} can play {position} - {role} score: {score}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate best formations from the latest FM analysis HTML.')
    parser.add_argument('-f', '--formation', help='Filter to formation name or substring (case-insensitive)', default=None)
    args = parser.parse_args()
    run_best_formations(target_formation_substring=args.formation)