# Best Formations Runner
# This script uses the formation_calculator module to compute and display the best formations.

from formation_calculator import parse_formations, analyze_formations
import json

def run_best_formations():
    """Run the best formations computation and display results."""
    # Example formation specification (replace with actual input)
    formation_spec = """
    1. 4-4-2
    GK - Goalkeeper (D)
    DL - Full Back (S)
    DR - Full Back (S)
    DC - Central Defender (D)
    DC - Central Defender (D)
    ML - Winger (S)
    MR - Winger (S)
    MC - Central Midfielder (S)
    MC - Central Midfielder (S)
    ST - Advanced Forward (A)
    ST - Advanced Forward (A)
    """

    # Example players data (replace with actual input)
    players = [
        {"name": "Player 1", "pos": "GK", "scores": {"GKD": 15}},
        {"name": "Player 2", "pos": "DL", "scores": {"FBS": 12}},
        {"name": "Player 3", "pos": "DR", "scores": {"FBS": 14}},
        {"name": "Player 4", "pos": "DC", "scores": {"CDD": 13}},
        {"name": "Player 5", "pos": "DC", "scores": {"CDD": 16}},
        {"name": "Player 6", "pos": "ML", "scores": {"WS": 11}},
        {"name": "Player 7", "pos": "MR", "scores": {"WS": 10}},
        {"name": "Player 8", "pos": "MC", "scores": {"CMS": 14}},
        {"name": "Player 9", "pos": "MC", "scores": {"CMS": 13}},
        {"name": "Player 10", "pos": "ST", "scores": {"AFA": 18}},
        {"name": "Player 11", "pos": "ST", "scores": {"AFA": 17}},
    ]

    # Parse formations
    formations = parse_formations(formation_spec)

    # Analyze formations
    results = analyze_formations(formations, players)

    # Display results
    print(json.dumps(results, indent=4))

if __name__ == "__main__":
    run_best_formations()