#!/usr/bin/env python3
"""
Test script to verify formation analysis functionality
"""

import os
import re
from bs4 import BeautifulSoup

def test_formation_html():
    """Check if the latest HTML contains proper formation analysis code"""
    
    # Find the latest HTML file
    html_files = [f for f in os.listdir('.') if f.startswith('fm_analysis_') and f.endswith('.html')]
    if not html_files:
        print("❌ No HTML files found")
        return False
    
    latest_html = max(html_files, key=lambda x: os.path.getctime(x))
    print(f"📄 Testing: {latest_html}")
    
    # Should be the new file: fm_analysis_886955ab821543d5ba6e3b49bed21a86.html
    
    # Read and parse HTML
    with open(latest_html, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key components
    checks = {
        'ROLE_NAME_TO_CODE mapping': 'ROLE_NAME_TO_CODE = {',
        'getPlayerRoleScore function': 'function getPlayerRoleScore(player, formationRole)',
        'calculatePositionRelevantScore function': 'function calculatePositionRelevantScore(player, formationRole)',
        'Formation analysis button': 'onclick="computeTopFormations()"',
        'Formation specifications': 'const formations = ['
    }
    
    results = {}
    for check_name, search_pattern in checks.items():
        found = search_pattern in content
        results[check_name] = found
        status = "✅" if found else "❌"
        print(f"{status} {check_name}: {'Found' if found else 'Missing'}")
    
    # Check formation count
    if 'Formation specifications' in results and results['Formation specifications']:
        # Try to count formations in the textarea content
        spec_pattern = r'<textarea[^>]*id="formationSpec"[^>]*>([^<]+)</textarea>'
        spec_match = re.search(spec_pattern, content, re.DOTALL)
        if spec_match:
            formation_content = spec_match.group(1)
            # Decode HTML entities
            formation_content = formation_content.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&#x27;', "'").replace('&quot;', '"')
            formation_count = len(re.findall(r'^\d+\.\s', formation_content, re.MULTILINE))
            print(f"📊 Formations found: {formation_count}")
            if formation_count >= 40:
                print(f"🎉 All 40+ formations loaded successfully!")
            elif formation_count >= 6:
                print(f"✅ Basic formations loaded ({formation_count})")
            else:
                print(f"⚠️  Only {formation_count} formations found")
        else:
            print("❌ Could not find formation textarea content")
    
    # Check role mapping completeness
    if results['ROLE_NAME_TO_CODE mapping']:
        role_mapping_match = re.search(r'const ROLE_NAME_TO_CODE = \{([^}]+)\}', content, re.DOTALL)
        if role_mapping_match:
            mapping_content = role_mapping_match.group(1)
            role_count = len(re.findall(r"'[^']+'\s*:\s*'[^']+'", mapping_content))
            print(f"📊 Role mappings found: {role_count}")
            
            # Check for key role mappings
            key_roles = [
                "'Box-to-Box Mid (S)': 'B2BS'",
                "'Advanced Forward (A)': 'AFA'",
                "'Ball-Playing Def (D)': 'BPDD'"
            ]
            for role in key_roles:
                if role in content:
                    print(f"✅ Key role mapping: {role}")
                else:
                    print(f"❌ Missing key role: {role}")
    
    all_passed = all(results.values())
    print(f"\n{'🎉 All checks passed!' if all_passed else '⚠️  Some checks failed'}")
    return all_passed

if __name__ == '__main__':
    print("🧪 Testing Formation Analysis Implementation")
    print("=" * 50)
    test_formation_html()