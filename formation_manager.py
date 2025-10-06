#!/usr/bin/env python3
"""
Formation Manager Utility

This tool helps you add, edit, and manage formations for the FM Analysis tool.
It provides a simple interface to add new formations in the correct format.
"""

import os
import re

def load_formations():
    """Load existing formations from the formations.txt file."""
    formations_file = 'formations.txt'
    if os.path.exists(formations_file):
        with open(formations_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def save_formations(content):
    """Save formations to the formations.txt file."""
    with open('formations.txt', 'w', encoding='utf-8') as f:
        f.write(content)

def count_formations(content):
    """Count the number of formations in the content."""
    return len(re.findall(r'^\d+\.\s', content, re.MULTILINE))

def add_formation_interactive():
    """Interactive formation builder."""
    print("\n🏗️  Formation Builder")
    print("=" * 40)
    
    current_content = load_formations()
    current_count = count_formations(current_content)
    next_number = current_count + 1
    
    print(f"Current formations: {current_count}")
    print(f"Adding formation #{next_number}")
    
    # Get formation name
    name = input("\nFormation name (e.g., '4-4-2 Attacking'): ").strip()
    if not name:
        print("❌ Formation name is required")
        return
    
    print(f"\n📝 Building: {next_number}. {name}")
    print("Enter positions and roles in format: Position = RoleCode")
    print("Available role codes: GKD, FBS, CDD, WBS, BPDD, DMD, B2BS, APS, WS, AFA, etc.")
    print("Enter 'done' when finished, 'help' for role codes, or 'cancel' to abort")
    
    positions = []
    while True:
        position_input = input(f"Position {len(positions) + 1}: ").strip()
        
        if position_input.lower() == 'done':
            break
        elif position_input.lower() == 'cancel':
            print("❌ Formation creation cancelled")
            return
        elif position_input.lower() == 'help':
            show_role_codes()
            continue
        elif '=' not in position_input:
            print("❌ Invalid format. Use: Position = RoleCode")
            continue
        
        # Validate format
        if re.match(r'^[A-Z/()LC\s]+ = [A-Z0-9S]+$', position_input):
            positions.append(position_input)
            print(f"✅ Added: {position_input}")
        else:
            print("❌ Invalid format. Example: 'GK = GKD' or 'D (C) = CDD'")
    
    if not positions:
        print("❌ No positions added")
        return
    
    # Build formation text
    formation_text = f"\n{next_number}. {name}\n"
    formation_text += "\n".join(positions) + "\n"
    
    # Show preview
    print(f"\n📋 Formation Preview:")
    print("=" * 30)
    print(formation_text)
    
    confirm = input("Save this formation? (y/n): ").strip().lower()
    if confirm == 'y':
        # Append to existing formations
        new_content = current_content + formation_text
        save_formations(new_content)
        print(f"✅ Formation '{name}' added successfully!")
        print(f"📊 Total formations: {count_formations(new_content)}")
    else:
        print("❌ Formation not saved")

def show_role_codes():
    """Display common role codes for reference."""
    print("\n📖 Common Role Codes:")
    print("=" * 30)
    codes = {
        "Goalkeepers": ["GKD", "SKS", "SKA"],
        "Defenders": ["FBS", "FBD", "FBA", "WBS", "WBD", "WBA", "CDD", "CDC", "CDS", "BPDD", "BPDS", "WCBS"],
        "Midfielders": ["DMD", "DMS", "DLPS", "B2BS", "CMS", "CMD", "APS", "APA", "MEZS", "BWMD", "BWMS"],
        "Wide Players": ["WS", "WA", "WMS", "IFA", "IFS", "IWA", "IWS"],
        "Attacking Mids": ["AMS", "AMA", "TREA", "ENGS", "SSA"],
        "Forwards": ["AFA", "TFS", "TFA", "DLFS", "DLFA", "CFS", "CFA", "PFA", "PA", "F9S"]
    }
    
    for category, role_list in codes.items():
        print(f"\n{category}:")
        print("  " + ", ".join(role_list))

def list_formations():
    """List all current formations."""
    content = load_formations()
    if not content:
        print("❌ No formations found")
        return
    
    formations = re.findall(r'(\d+\.\s[^\n]+)', content)
    print(f"\n📋 Current Formations ({len(formations)}):")
    print("=" * 40)
    for formation in formations:
        print(f"  {formation}")

def main():
    """Main menu."""
    while True:
        print("\n🏟️  FM Formation Manager")
        print("=" * 30)
        print("1. List current formations")
        print("2. Add new formation")
        print("3. Show role codes")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            list_formations()
        elif choice == '2':
            add_formation_interactive()
        elif choice == '3':
            show_role_codes()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")

if __name__ == '__main__':
    main()