# Best Formations Runner
# This script uses the formation_calculator module to compute and display the best formations.

from formation_calculator import extract_player_data, extract_formation_data, parse_formations_file, analyze_formations
from collections import defaultdict
import json
import os

def get_latest_analysis_file():
    """Retrieve the latest analysis file based on modification time."""
    analysis_files = [f for f in os.listdir('.') if f.startswith('fm_analysis_') and f.endswith('.html')]
    if not analysis_files:
        raise FileNotFoundError("No analysis files found.")
    latest_file = max(analysis_files, key=os.path.getmtime)
    return latest_file

def run_best_formations():
    """Run the best formations computation and display results."""
    html_file = get_latest_analysis_file()
    print(f"Using the latest analysis file: {html_file}")
    formations_file = "formations.txt"

    # Extract data
    players = extract_player_data(html_file)
    formation_text = extract_formation_data(html_file)
    formations = parse_formations_file(formations_file)

    # Extract players and their positions from the HTML data
    player_positions = defaultdict(list)
    for player_data in players:
        player_name = player_data['Player']
        positions = player_data['Pos'].split(', ')  # Split positions into a list
        
        # Parse composite positions like D (RLC), D/WB (R), etc. into individual positions
        expanded_positions = []
        for pos in positions:
            # Handle positions with slashes like "D/WB (R)"
            if '/' in pos:
                parts = pos.split('/')
                if '(' in pos and ')' in pos:
                    # Extract the parenthetical part
                    paren_part = pos[pos.find('('):pos.find(')')+1]
                    for part in parts:
                        base = part.strip()
                        if '(' not in base:  # Only add the parenthetical to bases without it
                            expanded_positions.append(f"{base} {paren_part}")
                        else:
                            expanded_positions.append(part.strip())
                else:
                    # No parentheses, just split by slash
                    expanded_positions.extend([part.strip() for part in parts])
            elif '(' in pos and ')' in pos:
                # Extract base position and sub-positions like "D (RLC)"
                base = pos.split('(')[0].strip()
                sub_positions = pos.split('(')[1].split(')')[0]
                # Create individual positions for each sub-position
                for sub_pos in sub_positions:
                    expanded_positions.append(f"{base} ({sub_pos})")
            else:
                expanded_positions.append(pos)
        
        player_positions[player_name].extend(expanded_positions)

    # Create a dictionary keyed by player names for quick lookups
    player_data_dict = {player['Player']: player for player in players}

    # Function to find the best available player for a position
    def find_best_player_for_position(position, role, used_players):
        eligible_players = []
        for player, positions in player_positions.items():
            if player not in used_players:
                # Check if the player can play the required position (exact match)
                if position in positions:
                    role_score = float(player_data_dict.get(player, {}).get(role, 0))  # Get the role score, default to 0
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
    
    # Sort by total score (descending) and take top 5
    formation_scores.sort(key=lambda x: x['total_score'], reverse=True)
    top_5_formations = formation_scores[:5]
    
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

if __name__ == "__main__":
    run_best_formations()