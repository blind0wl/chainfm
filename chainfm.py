import sys
import os
import glob
import uuid
import argparse
import pandas as pd
import numpy as np
import re

# Prevent Python from writing .pyc files into __pycache__ in the target folder.
# This avoids error when the script is run in folders where the user
# does not have permission to create files (OneDrive sync folders can be problematic).
sys.dont_write_bytecode = True
import argparse
import pandas as pd
from typing import Optional


def find_latest_file(folder: str) -> Optional[str]:
    """Return the most recently created/modified file in folder or None."""
    # Prefer HTML exports; only consider regular files (ignore directories like __pycache__)
    patterns = ('*.html', '*.htm')
    candidates = []
    for pat in patterns:
        candidates.extend(glob.glob(os.path.join(folder, pat)))

    # If no HTML files found, fall back to any regular file
    if not candidates:
        candidates = [p for p in glob.glob(os.path.join(folder, '*')) if os.path.isfile(p)]
    else:
        candidates = [p for p in candidates if os.path.isfile(p)]

    # Filter out files that look like our own output (UUID filenames) to avoid
    # re-reading previously generated HTMLs. Prefer files that, when parsed by
    # pandas.read_html, contain expected numeric FM columns (Pac/Acc).
    def looks_like_fm_export(path: str) -> bool:
        try:
            tables = pd.read_html(path, header=0, keep_default_na=False)
            if not tables:
                return False
            cols = tables[0].columns
            return ('Pac' in cols) or ('Acc' in cols)
        except Exception:
            return False

    real_exports = [p for p in candidates if looks_like_fm_export(p) and not os.path.basename(p).split('.')[0].isalnum() == False]
    # If we found real exports, prefer the newest of them
    if real_exports:
        return max(real_exports, key=os.path.getctime)

    # fallback: pick newest regular file
    if not candidates:
        return None
    return max(candidates, key=os.path.getctime)


def generate_html(dataframe: pd.DataFrame) -> str:
    """Wrap a DataFrame in a small HTML page that uses DataTables with improved readability."""
    
    # Check for missing expected columns
    print(f"DEBUG: generate_html received dataframe with {len(dataframe.columns)} columns")
    print(f"DEBUG: Has 'Highest Role Score': {'Highest Role Score' in dataframe.columns}")
    print(f"DEBUG: Has 'Resulting Role': {'Resulting Role' in dataframe.columns}")
    print(f"DEBUG: Last 5 columns: {list(dataframe.columns)[-5:]}")
    
    # Create better column titles mapping - using shorter but descriptive names
    column_titles = {
        'Inf': 'Info',
        'Name': 'Player',
        'Age': 'Age',
        'Club': 'Club',
        'Transfer Value': 'Value',
        'Wage': 'Wage',
        'Nat': 'Nat',
        'Position': 'Pos',
        'Personality': 'Pers',
        'Media Handling': 'Media',
        'Left Foot': 'L.Foot',
        'Right Foot': 'R.Foot',
        'Spd': 'Speed',
        'Jmp': 'Jump',
        'Str': 'Str',
        'Work': 'Work',
        'Height': 'Height',
        'str': 'Str',
        
    # Goalkeeper roles
    'gkd': 'GKD',
    'skd': 'SKD', 'sks': 'SKS', 'ska': 'SKA',
        
    # Defender roles
    'bpdd': 'BPDD', 'bpds': 'BPDS', 'bpdc': 'BPDC',
    'cdd': 'CDD', 'cds': 'CDS', 'cdc': 'CDC',
    'cwbs': 'CWBS', 'cwba': 'CWBA',
    'fbd': 'FBD', 'fbs': 'FBS', 'fba': 'FBA',
    'ifbd': 'IFBD',
    'iwbd': 'IWBD', 'iwbs': 'IWBS', 'iwba': 'IWBA',
    'ld': 'LD', 'ls': 'LS',
    'ncbd': 'NCBD', 'ncbs': 'NCBS', 'ncbc': 'NCBC',
    'nfbd': 'NFBD',
    'wcbd': 'WCBD', 'wcbs': 'WCBS', 'wcba': 'WCBA',
    'wbd': 'WBD', 'wbs': 'WBS', 'wba': 'WBA',
        
    # Midfielder roles
    'aps': 'APS', 'apa': 'APA',
    'ad': 'AD',
    'ams': 'AMS', 'ama': 'AMA',
    'bwmd': 'BWMD', 'bwms': 'BWMS',
    'b2bs': 'B2BS',
    'cars': 'CARS',
    'cmd': 'CMD', 'cms': 'CMS', 'cma': 'CMA',
    'dlpd': 'DLPD', 'dlps': 'DLPS',
    'dmd': 'DMD', 'dms': 'DMS',
    'dwd': 'DWD', 'dws': 'DWS',
    'engs': 'ENGS',
    'hbd': 'HBD',
    'ifs': 'IFS', 'ifa': 'IFA',
    'iws': 'IWS', 'iwa': 'IWA',
    'mezs': 'MEZS', 'meza': 'MEZA',
    'raua': 'RAUA',
    'regs': 'REGS',
    'rps': 'RPS',
    'svs': 'SVS', 'sva': 'SVA',
    'ssa': 'SSA',
    'wmd': 'WMD', 'wms': 'WMS', 'wma': 'WMA',
    'wps': 'WPS', 'wpa': 'WPA',
    'wtfs': 'WTFS', 'wtfa': 'WTFA',
    'ws': 'WS', 'wa': 'WA',
        
    # Forward roles
    'afa': 'AFA',
    'cfs': 'CFS', 'cfa': 'CFA',
    'dlfs': 'DLFS', 'dlfa': 'DLFA',
    'f9s': 'F9S',
    'pa': 'PA',
    'pfd': 'PFD', 'pfs': 'PFS', 'pfa': 'PFA',
    'tfs': 'TFS', 'tfa': 'TFA',
    'trea': 'TREA',
        
        # Composite scores
        'fb': 'FB',
        'cb': 'CB',
        
        # Summary columns
        'Best_Score': 'Best Score',
        'Best_Role': 'Best Role'
    }
    
    # Use the same wanted column order as the main script, but exclude UID columns
    wanted = [
        'Name','Age','Club','Position',
        'Best_Score','Best_Role',
        'Spd','str','Work','Jmp',
        'gkd','skd','sks','ska',
        'bpdd','bpds','bpdc','cdd','cds','cdc','cwbs','cwba','fbd','fbs','fba','ifbd','iwbd','iwbs','iwba',
        'ld','ls','ncbd','ncbs','ncbc','nfbd','wcbd','wcbs','wcba','wbd','wbs','wba',
        'aps','apa','ad','ams','ama','bwmd','bwms','b2bs','cars','cmd','cms','cma','dlpd','dlps','dmd','dms','dwd','dws',
        'engs','hbd','ifs','ifa','iws','iwa','mezs','meza','raua','regs','rps','svs','sva','ssa','wmd','wms','wma','wps','wpa',
        'wtfs','wtfa','ws','wa','afa','cfs','cfa','dlfs','dlfa','f9s','pa','pfd','pfs','pfa','tfs','tfa','trea',
        'fb','cb'
    ]
    ordered_cols = [col for col in wanted if col in dataframe.columns]
    dataframe = dataframe[ordered_cols]
    
    # Rename columns for better display
    display_df = dataframe.copy()
    display_df.columns = [column_titles.get(col, col) for col in display_df.columns]
    
    # Generate the table HTML with improved styling
    table_html = display_df.to_html(table_id="playerTable", index=False, escape=False, 
                                   classes="display compact nowrap")

    # Build a compact role-only legend using the user's full role descriptions.
    full_role_map = {
        'AFA': 'Advanced Forward Attack',
        'APA': 'Advanced Playmaker Attack',
        'APS': 'Advanced Playmaker Support',
        'AD': 'Anchor Defend',
        'AMA': 'Attacking Midfielder Attack',
        'AMS': 'Attacking Midfielder Support',
        'BPDC': 'Ball Playing Defender Cover',
        'BPDD': 'Ball Playing Defender Defend',
        'BPDS': 'Ball Playing Defender Stopper',
        'BWMD': 'Ball Winning Midfielder Defend',
        'BWMS': 'Ball Winning Midfielder Support',
        'B2BS': 'Box to Box Midfielder Support',
        'CARS': 'Carrilero Support',
        'CDC': 'Central Defender Cover',
        'CDD': 'Central Defender Defend',
        'CDS': 'Central Defender Stopper',
        'CMA': 'Central Midfielder Attack',
        'CMD': 'Central Midfielder Defend',
        'CMS': 'Central Midfielder Support',
        'CFA': 'Complete Forward Attack',
        'CFS': 'Complete Forward Support',
        'CWBA': 'Complete Wing Back Attack',
        'CWBS': 'Complete Wing Back Support',
        'DLFA': 'Deep Lying Forward Attack',
        'DLFS': 'Deep Lying Forward Support',
        'DLPD': 'Deep Lying Playmaker Defend',
        'DLPS': 'Deep Lying Playmaker Support',
        'DMD': 'Defensive Midfielder Defend',
        'DMS': 'Defensive Midfielder Support',
        'DWD': 'Defensive Winger Defend',
        'DWS': 'Defensive Winger Support',
        'ENGS': 'Enganche Support',
        'F9S': 'False Nine Support',
        'FBA': 'Full Back Attack',
        'FBD': 'Full Back Defend',
        'FBS': 'Full Back Support',
        'GKD': 'Goalkeeper Defend',
        'HBD': 'Half Back Defend',
        'IFA': 'Inside Forward Attack',
        'IFS': 'Inside Forward Support',
        'IFBD': 'Inverted Full Back Defend',
        'IFBS': 'Inverted Full Back Support',
        'IWA': 'Inverted Winger Attack',
        'IWS': 'Inverted Winger Support',
        # Additional common roles / fallbacks
        'SKD': 'Sweeper Keeper Defend',
        'SKS': 'Sweeper Keeper Support',
        'SKA': 'Sweeper Keeper Attack',
        'IWBD': 'Inverted Wing Back Defend',
        'IWBS': 'Inverted Wing Back Support',
        'IWBA': 'Inverted Wing Back Attack',
        'LD': 'Libero Defend',
        'LS': 'Libero Support',
        'NCBD': 'No-nonsense Centre Back Defend',
        'NCBS': 'No-nonsense Centre Back Support',
        'NCBC': 'No-nonsense Centre Back Cover',
        'NFBD': 'No-nonsense Full Back Defend',
        'WCBD': 'Wide Centre Back Defend',
        'WCBS': 'Wide Centre Back Support',
        'WCBA': 'Wide Centre Back Attack',
        'WBD': 'Wing Back Defend',
        'WBS': 'Wing Back Support',
        'WBA': 'Wing Back Attack',
        'MEZS': 'Mezzala Support',
        'MEZA': 'Mezzala Attack',
        'RAUA': 'Raumdeuter Attack',
        'REGS': 'Regista Support',
        'RPS': 'Roaming Playmaker Support',
        'SVS': 'Supportive Role Support',
        'SVA': 'Supportive Role Attack',
        'SSA': 'Secondary Striker Attack',
        'WMD': 'Wide Midfielder Defend',
        'WMS': 'Wide Midfielder Support',
        'WMA': 'Wide Midfielder Attack',
        'WPS': 'Wide Playmaker Support',
        'WPA': 'Wide Playmaker Attack',
        'WTFS': 'Wide Target Forward Support',
        'WTFA': 'Wide Target Forward Attack',
        'WS': 'Wide Support',
        'WA': 'Wide Attack',
        'PA': 'Poacher Attack',
        'PFD': 'Pressing Forward Defend',
        'PFS': 'Pressing Forward Support',
        'PFA': 'Pressing Forward Attack',
        'TFS': 'Trequartista Support',
        'TFA': 'Trequartista Attack',
        'TREA': 'Trequartista (Role)',
        'FB': 'Full Back Composite',
        'CB': 'Centre Back Composite',
    }

    # Build list of role display keys present in the table (uppercase codes)
    role_pairs = []
    present_codes = []
    for orig_key, short in column_titles.items():
        if orig_key.islower() and orig_key != 'str':  # exclude composite metric from legend
            code = short.upper()
            # include role if the column (display name) exists in the table
            if code in display_df.columns or orig_key in dataframe.columns or short in display_df.columns:
                present_codes.append(code)

    # Deduplicate while preserving order
    present_codes = list(dict.fromkeys(present_codes))

    # Determine which codes are missing full descriptions
    missing_full = [c for c in present_codes if c not in full_role_map]
    if missing_full:
        print("DEBUG: role codes missing full description:", missing_full)

    # Build role_pairs using full descriptions when available, otherwise fallback heuristics
    suffix_map = {'A': 'Attack', 'D': 'Defend', 'S': 'Support'}
    for code in present_codes:
        if code in full_role_map:
            role_pairs.append((code, full_role_map[code]))
        else:
            # fallback: split last letter as duty if it's A/D/S, else just use code
            if len(code) > 1 and code[-1] in suffix_map:
                base = code[:-1]
                role_pairs.append((code, f"{base} {suffix_map[code[-1]]}"))
            else:
                role_pairs.append((code, code))

    if role_pairs:
        half = (len(role_pairs) + 1) // 2
        left = role_pairs[:half]
        right = role_pairs[half:]
        left_html = ''.join([f"<div class=\"legend-row clickable\" data-code=\"{orig}\" data-active=\"1\" onclick=\"legendToggleRole(this)\"><code>{orig}</code> &nbsp;&rarr;&nbsp; <strong>{disp}</strong></div>" for orig, disp in left])
        right_html = ''.join([f"<div class=\"legend-row clickable\" data-code=\"{orig}\" data-active=\"1\" onclick=\"legendToggleRole(this)\"><code>{orig}</code> &nbsp;&rarr;&nbsp; <strong>{disp}</strong></div>" for orig, disp in right])

        legend_html = f"""
            <div class="legend" style="margin-bottom:6px; display:none;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <strong>Role legend</strong>
                    <div class="legend-controls" style="margin-left:12px; display:flex; gap:8px;">
                        <button class="legend-toggle" onclick="disableAllRoles()">Disable all</button>
                        <button class="legend-toggle" onclick="enableAllRoles()">Enable all</button>
                    </div>
                </div>
                <div style="display:flex; gap:12px; margin-top:6px;">
                    <div style="flex:1">{left_html}</div>
                    <div style="flex:1">{right_html}</div>
                </div>
            </div>
        """
    else:
        legend_html = '<div class="legend" style="margin-bottom:6px; font-size:11px; color:#666;">Legend not available</div>'

    # Simple HTML without DataTables for perfect alignment
    html_template = r"""
<!DOCTYPE html>
<html>
<head>
    <title>FM Player Analysis</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%%, #764ba2 100%%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .controls {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .table-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: auto;
            max-height: 80vh;
        }
        
        #playerTable {
            width: 100%%;
            font-size: 12px;
            table-layout: auto;
            border-collapse: collapse;
        }
        
        #playerTable th {
            background-color: #2c3e50;
            color: white;
            font-weight: bold;
            text-align: center;
            padding: 8px 6px;
            border: 1px solid #34495e;
            white-space: nowrap;
            font-size: 10px;
            line-height: 1.1;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        #playerTable td {
            padding: 6px 6px;
            text-align: center;
            border: 1px solid #ecf0f1;
            white-space: nowrap;
            font-size: 10px;
        }
        
        /* Player info columns styling */
        #playerTable th:nth-child(1),
        #playerTable th:nth-child(2),
        #playerTable th:nth-child(3),
        #playerTable th:nth-child(4) {
            background-color: #34495e;
            font-weight: bold;
            text-align: left;
            padding-left: 10px;
        }
        
        #playerTable td:nth-child(1),
        #playerTable td:nth-child(2),
        #playerTable td:nth-child(3),
        #playerTable td:nth-child(4) {
            background-color: #ecf0f1;
            font-weight: bold;
            text-align: left;
            padding-left: 10px;
        }
        
        /* Color coding for scores */
        .score-excellent { background-color: #2ecc71; color: white; font-weight: bold; }
        .score-good { background-color: #f39c12; color: white; }
        .score-average { background-color: #f1c40f; }
        .score-poor { background-color: #e74c3c; color: white; }
        
        .position-filter {
            margin: 5px;
            padding: 8px 16px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .position-filter:hover,
        .position-filter.active {
            background: #2980b9;
        }
        /* Legend styling (compact) */
        .legend { font-size: 11px; color: #333; }
        .legend-row { margin-bottom: 4px; }
        .legend-row.clickable { cursor: pointer; user-select: none; }
        .legend-row.inactive { opacity: 0.6; }
        .legend-row.inactive code { text-decoration: line-through; color:#888; background:#f0f0f0; }
        .legend small { color: #666; margin-left: 6px; }
        .legend code { font-family: Consolas, "Courier New", monospace; font-size: 10px; color: #444; background:#f7f7f7; padding:2px 4px; border-radius:3px; }
    .legend-toggle { margin-left: 8px; padding:4px 8px; font-size:11px; cursor:pointer; background:#ddd; border-radius:4px; border:1px solid #ccc; }

    /* Best formations panel */
    #bestFormationsPanel { display:none; margin-top:10px; }
    #bestFormationsPanel .row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
    #bestFormationsResults { margin-top:8px; font-size:12px; }
    #bestFormationsResults table { width:100%%; border-collapse: collapse; margin-bottom:14px; }
    #bestFormationsResults th, #bestFormationsResults td { border:1px solid #ddd; padding:6px; text-align:left; font-size:12px; }
    .muted { color:#666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Football Manager Player Analysis</h1>
        <p>Comprehensive role suitability analysis for your squad</p>
    </div>
    
    <div class="controls">
        <div>
            <strong>Quick Filters:</strong>
            <button class="position-filter" onclick="filterByPosition(this, 'GK')">Goalkeepers</button>
            <button class="position-filter" onclick="filterByPosition(this, 'D')">Defenders</button>
            <button class="position-filter" onclick="filterByPosition(this, 'M')">Midfielders</button>
            <button class="position-filter" onclick="filterByPosition(this, 'F')">Forwards</button>
            <button class="position-filter" onclick="clearFilters(this)">Show All</button>
            <button id="externalLegendToggle" class="legend-toggle" style="margin-left:12px;" onclick="toggleLegendExternal(this)">Show legend</button>
            <button class="legend-toggle" style="margin-left:8px;" onclick="toggleBestFormations()">Best formations</button>
        </div>
        <div id="bestFormationsPanel">
            <div class="row">
                <span class="muted">Top 3 matches based on Pos eligibility and Best Score (0–20):</span>
                <button onclick="computeTopFormations()">Compute top 3</button>
            </div>
            <div id="bestFormationsResults"></div>
            <textarea id="formationSpec" style="display:none;">
1. 4-4-2
GK – Goalkeeper (D)
D R – Full Back (S)
DC – Central Defender (D)
DC – Central Defender (D)
D L – Full Back (S)
M R – Winger (S)
MC – Box-to-Box Mid (S)
MC – Ball-Winning Mid (D)
M L – Winger (A)
ST C – Advanced Forward (A)
ST C – Deep-Lying Forward (S)

2. 4-2-3-1 Wide
GK – Sweeper Keeper (S)
D/WB R – Wing Back (S)
DC – Ball-Playing Def (D)
DC – Central Def (D)
D/WB L – Wing Back (S)
DM – Deep-Lying Playmaker (S)
DM – Def Mid (D)
AM R – Inside Forward (A)
AMC – Att Mid (S)
AM L – Winger (A)
ST C – Pressing Forward (A)

3. 4-3-3 DM Wide
GK – Sweeper Keeper (S)
D/WB R – Wing Back (S)
DC – Central Def (D)
DC – Central Def (D)
D/WB L – Wing Back (S)
DM – Anchor Man (D)
MC – Box-to-Box Mid (S)
MC – Advanced Playmaker (S)
AM R – Inside Forward (A)
AM L – Winger (A)
ST C – Advanced Forward (A)

4. 4-1-2-1-2 Narrow (Diamond)
GK – Goalkeeper (D)
D R – Full Back (S)
DC – Central Def (D)
DC – Central Def (D)
D L – Full Back (S)
DM – Def Mid (D)
MC – Box-to-Box Mid (S)
MC – Mezzala (S)
AMC – Advanced Playmaker (A)
ST C – Poacher (A)
ST C – Deep-Lying Forward (S)

5. 3-5-2
GK – Sweeper Keeper (S)
DC – Wide Centre-Back (S)
DC – Central Def (D)
DC – Wide Centre-Back (S)
D/WB R – Wing Back (S)
D/WB L – Wing Back (S)
MC – Ball-Winning Mid (D)
MC – Deep-Lying Playmaker (S)
MC – Mezzala (S)
ST C – Pressing Forward (A)
ST C – Target Forward (S)

6. 5-3-2 WB
GK – Sweeper Keeper (S)
D/WB R – Wing Back (S)
DC – Central Def (D)
DC – Ball-Playing Def (D)
DC – Central Def (D)
D/WB L – Wing Back (S)
MC – Box-to-Box Mid (S)
MC – Deep-Lying Playmaker (S)
MC – Ball-Winning Mid (D)
ST C – Target Forward (S)
ST C – Poacher (A)
            </textarea>
        </div>
    </div>
    
    <!-- Legend inserted here -->
    %s

    <div class="table-container">
        %s
    </div>
    
    <script>
        // Simple filtering without DataTables
        function filterByPosition(btn, position) {
            // reset active state
            document.querySelectorAll('.position-filter').forEach(b => b.classList.remove('active'));
            if (btn && btn.classList) btn.classList.add('active');

                const rows = document.querySelectorAll('#playerTable tbody tr');
                // common tokens for matching
                const defTokens = ['CB','LB','RB','LWB','RWB','WB','FB','BPD','WCB','NFB','DC','DL','DR','CD','NCB','FULLBACK','BACK','DEF'];
                const midTokens = ['CM','DM','AM','MF','MID','LM','RM','WM','ENG','MEZ','AP','BWM','DLP','REG','CM-A','CM-S','MIDFIEL'];
                const fwdTokens = ['ST','FW','CF','SS','WF','F9','FWD','ATT','STR','AF','DLF','TF','PF','PA','CF-A','CF-S','FORW'];

                rows.forEach(row => {
                    const positionCell = row.cells[3]; // Position is 4th column (index 3)
                    if (!positionCell) return;
                    let posText = (positionCell.textContent || positionCell.innerText || '').toUpperCase().trim();
                    // normalize non-letters/digits to spaces so tokens like 'ST (C)' become ['ST','C']
                    posText = posText.replace(/[^A-Z0-9]/g, ' ').trim();
                    const tokens = posText.split(/\s+/);
                    let match = false;
                    if (position === 'GK') {
                        // Exact GK token
                        match = tokens.includes('GK');
                    } else if (position === 'D') {
                        // Any token that starts with 'D' (e.g., 'DC', 'DL', 'DR', 'DM' excluded)
                        match = tokens.some(t => t.startsWith('D') && t !== 'DM');
                    } else if (position === 'M') {
                        // DM OR tokens that start with 'M' OR start with 'AM' (attacking midfield)
                        match = tokens.includes('DM') || tokens.some(t => t.startsWith('M')) || tokens.some(t => t.startsWith('AM'));
                    } else if (position === 'F') {
                        // Forwards: tokens that include 'ST' (covers 'ST', 'STC', etc.)
                        match = tokens.some(t => t.includes('ST'));
                    }
                    row.style.display = match ? '' : 'none';
                });
        }

        function clearFilters(btn) {
            document.querySelectorAll('.position-filter').forEach(b => b.classList.remove('active'));
            // don't set active for 'Show All'
            const rows = document.querySelectorAll('#playerTable tbody tr');
            rows.forEach(row => row.style.display = '');
        }
        
        // Color code score cells after page loads (use DOMContentLoaded for reliability)
        document.addEventListener('DOMContentLoaded', function() {
            try {
                const cells = document.querySelectorAll('#playerTable td');
                cells.forEach(cell => {
                    const data = parseFloat(cell.textContent);
                    if (!isNaN(data) && data >= 0 && data <= 20) {
                        if (data >= 15) {
                            cell.classList.add('score-excellent');
                        } else if (data >= 12) {
                            cell.classList.add('score-good');
                        } else if (data >= 8) {
                            cell.classList.add('score-average');
                        } else if (data >= 5) {
                            cell.classList.add('score-poor');
                        }
                    }
                });
            } catch (e) {
                // no-op; avoid breaking other features if coloring fails
                console && console.error && console.error('Coloring error:', e);
            }
        });

        // (internal legend toggle removed) Use the external 'Show legend' button instead

        // External toggle (button outside hidden legend). Keeps label in sync.
        function toggleLegendExternal(extBtn) {
            const legend = document.querySelector('.legend');
            if (!legend) return;
            const isHidden = window.getComputedStyle(legend).display === 'none';
            legend.style.display = isHidden ? 'block' : 'none';
            if (extBtn) extBtn.textContent = isHidden ? 'Hide legend' : 'Show legend';
        }

        // ===== Best formations (Top 3) =====
        function toggleBestFormations(){
            const p = document.getElementById('bestFormationsPanel');
            if (!p) return;
            const isHidden = window.getComputedStyle(p).display === 'none';
            p.style.display = isHidden ? 'block' : 'none';
        }

        function headerIndex(){
            const map = {};
            document.querySelectorAll('#playerTable thead th').forEach((th,i)=>{
                const k = (th.textContent||'').trim().toUpperCase();
                if (!map[k]) map[k] = [];
                map[k].push(i);
            });
            return map;
        }

        function posTokens(posText){
            const txt = (posText || '').toUpperCase().replace(/[^A-Z0-9]/g,' ');
            const raw = txt.split(/\s+/).filter(Boolean);
            const set = new Set(raw);
            // Expand combined side tokens RC/LC/RL/RLC into individual R/L/C for later combos
            if (set.has('RLC')) { set.add('R'); set.add('L'); set.add('C'); }
            if (set.has('RC')) { set.add('R'); set.add('C'); }
            if (set.has('LC')) { set.add('L'); set.add('C'); }
            if (set.has('RL')) { set.add('R'); set.add('L'); }
            // Build derived position+side tokens
            if (set.has('D') && set.has('R')) set.add('DR');
            if (set.has('D') && set.has('L')) set.add('DL');
            if (set.has('D') && set.has('C')) set.add('DC');
            if (set.has('WB') && set.has('R')) set.add('WBR');
            if (set.has('WB') && set.has('L')) set.add('WBL');
            if (set.has('M') && set.has('R')) set.add('MR');
            if (set.has('M') && set.has('L')) set.add('ML');
            if (set.has('M') && set.has('C')) set.add('MC');
            if (set.has('AM') && set.has('R')) set.add('AMR');
            if (set.has('AM') && set.has('L')) set.add('AML');
            if (set.has('AM') && set.has('C')) set.add('AMC');
            return set;
        }

        // Map a slot requirement to relevant role columns (table headers) to score by
        function roleCandidatesFor(req){
            const s = (req||'').toUpperCase().trim();
            const any = [];
            const GK = ['GKD','SKD','SKS','SKA'];
            const DC = ['CDD','CDS','CDC','BPDD','BPDS','BPDC','NCBD','NCBS','NCBC','WCBD','WCBS','WCBA'];
            const FB = ['FBD','FBS','FBA','WBD','WBS','WBA','CWBS','CWBA','IWBD','IWBS','IWBA','IFBD','NFBD'];
            const WB = ['WBD','WBS','WBA','CWBS','CWBA','IWBD','IWBS','IWBA'];
            const DM = ['DMD','DMS','HBD','AD','DLPD','DLPS','REGS','RPS'];
            const MC = ['CMD','CMS','CMA','B2BS','CARS','MEZS','MEZA','DLPD','DLPS','RPS','REGS'];
            const WM = ['WMD','WMS','WMA','WPS','WPA','DWD','DWS'];
            const AMC = ['AMS','AMA','APS','APA','ENGS','SVS','SVA','SSA','TREA'];
            const AMW = ['IFS','IFA','IWS','IWA','WPS','WPA','WMS','WMA','WMD','DWD','DWS','RAUA','SVS','SVA','TREA'];
            const ST = ['AFA','CFS','CFA','DLFS','DLFA','F9S','PA','PFD','PFS','PFA','TFS','TFA','WTFS','WTFA','SSA'];
            if (s.startsWith('GK')) return GK;
            if (s.startsWith('DC')) return DC;
            if (s.startsWith('D R')) return FB;
            if (s.startsWith('D L')) return FB;
            if (s.startsWith('D/WB R')) return FB.concat(WB);
            if (s.startsWith('D/WB L')) return FB.concat(WB);
            if (s.startsWith('WB R')) return WB;
            if (s.startsWith('WB L')) return WB;
            if (s.startsWith('DM')) return DM;
            if (s.startsWith('MC R') || s.startsWith('MC L') || s.startsWith('MC')) return MC;
            if (s.startsWith('M R') || s.startsWith('M L')) return WM;
            if (s.startsWith('AM R')) return AMW;
            if (s.startsWith('AM L')) return AMW;
            if (s.startsWith('AMC')) return AMC;
            if (s.startsWith('ST')) return ST;
            // generic fallbacks
            if (s.includes('AM')) return AMW;
            if (s.includes('WB')) return WB;
            if (s.includes(' D')) return FB.concat(DC);
            if (s.includes(' M')) return MC;
            return any;
        }

        function readPlayers(){
            const idx = headerIndex();
            const rows = Array.from(document.querySelectorAll('#playerTable tbody tr'));
            return rows.map(r=>{
                const get = key=>{
                    const i = idx[key.toUpperCase()];
                    if (i==null) return null;
                    const t = r.cells[i] ? r.cells[i].textContent.trim() : '';
                    const n = parseFloat(t);
                    return isNaN(n) ? t : n;
                };
                const values = {};
                Object.keys(idx).forEach(k=>{
                    const i = idx[k];
                    const t = r.cells[i] ? r.cells[i].textContent.trim() : '';
                    const n = parseFloat(t);
                    values[k] = isNaN(n) ? t : n;
                });
                const pos = (get('Pos') || '').toString();
                return { name: (get('Player')||'').toString(), pos, tokens: posTokens(pos), values };
            });
        }

        function parseFormations(){
            const el = document.getElementById('formationSpec');
            let txt = el ? (el.value || '') : '';
            if (!txt || !txt.trim()) { txt = el ? (el.textContent || '') : ''; }
            // Split on CRLF or LF newlines
            const lines = txt.split(/\r?\n/);
            const map = {};
            let current = null;
            const headerRe = /^\d+\.\s+(.*)$/;
            const sepRe = /\s[–—-]\s/; // space dash space: en-dash/em-dash/hyphen
            lines.forEach(line=>{
                const s = line.trim();
                if (!s) return;
                // Header lines: "1. Formation Name" or a line with digits/dashes and no role separator
                const m = s.match(headerRe);
                if (m){ current = m[1].trim(); map[current] = []; return; }
                if (!sepRe.test(s)){
                    // If no separator and looks like a formation title, treat as header
                    if (/\d.*-.*\d/.test(s)) { current = s; map[current] = []; }
                    return;
                }
                if (!current){
                    // Start a default formation if slots appear before a header
                    current = 'Formation';
                    map[current] = [];
                }
                const parts = s.split(sepRe);
                const left = (parts[0]||'').trim();
                const right = (parts[1]||'').trim();
                if (!left) return;
                map[current].push({ req: left, role: right });
            });
            return map;
        }

        function allowedTokensForReq(req){
            const s = (req||'').toUpperCase().replace(/\s+/g,' ').trim();
            const has = (frag)=> s.indexOf(frag) >= 0;
            if (s.startsWith('GK')) return ['GK'];
            if (s.startsWith('DC')) return ['DC'];
            if (s.startsWith('D R')) return ['DR'];
            if (s.startsWith('D L')) return ['DL'];
            if (s.startsWith('D/WB R')) return ['DR','WBR'];
            if (s.startsWith('D/WB L')) return ['DL','WBL'];
            if (s.startsWith('WB R')) return ['WBR'];
            if (s.startsWith('WB L')) return ['WBL'];
            if (s.startsWith('DM')) return ['DM'];
            if (s.startsWith('MC R')) return ['MC','MR'];
            if (s.startsWith('MC L')) return ['MC','ML'];
            if (s.startsWith('MC')) return ['MC'];
            if (s.startsWith('M R')) return ['MR'];
            if (s.startsWith('M L')) return ['ML'];
            if (s.startsWith('AM R') || s.startsWith('AMC R')) return ['AMR'];
            if (s.startsWith('AM L') || s.startsWith('AMC L')) return ['AML'];
            if (s.startsWith('AMC')) return ['AMC'];
            if (s.startsWith('ST C') || s.startsWith('ST')) return ['ST'];
            if (has('AM')) return ['AMR','AMC','AML'];
            if (has('WB')) return ['WBR','WBL'];
            if (has('D ')) return ['DR','DC','DL'];
            if (has('M ')) return ['MR','MC','ML'];
            return [];
        }

        function computeXIForFormation(name, spec, players, scoreKey){
            const used = new Set();
            const xi = [];
            let total = 0;
            for (const slot of spec){
                const allow = allowedTokensForReq(slot.req);
                const roleCols = roleCandidatesFor(slot.req);
                let best = { p:null, score: -Infinity };
                for (const p of players){
                    if (used.has(p.name)) continue;
                    const ok = allow.length === 0 ? true : allow.some(t => p.tokens.has(t));
                    if (!ok) continue;
                    // Prefer role-specific score for the slot; fall back to Best Score
                    let score = -Infinity;
                    for (const col of roleCols){
                        const vRole = p.values[col];
                        if (typeof vRole === 'number') {
                            if (vRole > score) score = vRole;
                        }
                    }
                    if (!isFinite(score)){
                        const v = p.values[scoreKey];
                        score = (typeof v === 'number') ? v : -Infinity;
                    }
                    if (score > best.score) best = { p, score };
                }
                if (best.p){
                    used.add(best.p.name);
                    xi.push({ req: slot.req, role: slot.role, name: best.p.name, pos: best.p.pos, score: best.score });
                    total += best.score;
                } else {
                    xi.push({ req: slot.req, role: slot.role, name: '(no suitable player)', pos: '', score: 0 });
                }
            }
            const maxPerSlot = 20;
            const percent = spec.length ? (total / (maxPerSlot * spec.length)) * 100 : 0;
            return { name, xi, total, percent };
        }

        function computeTopFormations(){
            const formations = parseFormations();
            const players = readPlayers();
            const idx = headerIndex();
            let scoreKey = 'BEST SCORE';
            if (idx[scoreKey]==null){
                scoreKey = Object.keys(idx).find(k => k.replace(/\s+/g,'')==='BESTSCORE') || 'BEST SCORE';
            }

            const results = [];
            Object.keys(formations).forEach(fname=>{
                const res = computeXIForFormation(fname, formations[fname], players, scoreKey);
                results.push(res);
            });
            results.sort((a,b)=> b.percent - a.percent);

            const top = results.slice(0,3);
            const out = [];
            top.forEach((r, idxTop)=>{
                out.push(`<h3 style="margin:8px 0 6px 0;">${idxTop+1}. ${r.name} — ${r.percent.toFixed(1)}%% (Total ${r.total.toFixed(1)})</h3>`);
                let t = '<table><thead><tr><th>#</th><th>Requirement</th><th>Suggested role</th><th>Player</th><th>Pos</th><th>Score</th></tr></thead><tbody>';
                r.xi.forEach((row,i)=>{
                    t += `<tr>
                        <td>${i+1}</td>
                        <td>${row.req}</td>
                        <td>${row.role||''}</td>
                        <td>${row.name}</td>
                        <td>${row.pos}</td>
                        <td>${row.score.toFixed ? row.score.toFixed(1) : row.score}</td>
                    </tr>`;
                });
                t += '</tbody></table>';
                out.push(t);
            });
            if (!top.length){ out.push('<div class="muted">No formations parsed.</div>'); }
            document.getElementById('bestFormationsResults').innerHTML = out.join('');
        }

        // ===== Column visibility via legend =====
        function setColumnVisibilityByIndex(colIndex, visible){
            if (colIndex == null || colIndex < 0) return;
            const table = document.getElementById('playerTable');
            if (!table) return;
            // header
            const th = table.querySelectorAll('thead th')[colIndex];
            if (th) th.style.display = visible ? '' : 'none';
            // body cells
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(r=>{
                const cell = r.cells[colIndex];
                if (cell) cell.style.display = visible ? '' : 'none';
            });
        }

        function setColumnVisibilityByCode(code, visible){
            if (!code) return;
            const idx = headerIndex();
            const key = code.toUpperCase();
            const val = idx[key];
            if (val==null) return;
            if (Array.isArray(val)) {
                val.forEach(i=> setColumnVisibilityByIndex(i, visible));
            } else {
                setColumnVisibilityByIndex(val, visible);
            }
        }

        function updateLegendRowState(rowEl, active){
            if (!rowEl) return;
            rowEl.dataset.active = active ? '1' : '0';
            rowEl.classList.toggle('inactive', !active);
        }

        function legendToggleRole(rowEl){
            const code = rowEl && rowEl.dataset ? rowEl.dataset.code : null;
            if (!code) return;
            const active = rowEl.dataset.active !== '0';
            const next = !active;
            setColumnVisibilityByCode(code, next);
            updateLegendRowState(rowEl, next);
        }

        function disableAllRoles(){
            document.querySelectorAll('.legend-row.clickable').forEach(row=>{
                const code = row.dataset.code;
                setColumnVisibilityByCode(code, false);
                updateLegendRowState(row, false);
            });
        }

        function enableAllRoles(){
            document.querySelectorAll('.legend-row.clickable').forEach(row=>{
                const code = row.dataset.code;
                setColumnVisibilityByCode(code, true);
                updateLegendRowState(row, true);
            });
        }
    </script>
</body>
</html>
    """ % (legend_html, table_html)
    
    # DEBUG: Print Michael Aileman's row before HTML generation
    if 'Michael Aileman' in dataframe['Name'].values:
        row = dataframe[dataframe['Name'] == 'Michael Aileman']
        print('DEBUG: Michael Aileman row:')
        print(row.iloc[0].to_dict())
    
    # Drop UID columns if present
    for col in dataframe.columns:
        if col.lower() == 'uid' or 'uid' in col.lower():
            dataframe = dataframe.drop(col, axis=1)
    # Save Best Score and Best Role, then re-add as last columns
    best_score = dataframe['Highest Role Score'] if 'Highest Role Score' in dataframe.columns else None
    best_role = dataframe['Resulting Role'] if 'Resulting Role' in dataframe.columns else None
    # Drop if present
    for col in ['Highest Role Score', 'Resulting Role']:
        if col in dataframe.columns:
            dataframe = dataframe.drop(col, axis=1)
    # Re-add as last columns
    if best_score is not None:
        dataframe['Highest Role Score'] = best_score
    if best_role is not None:
        dataframe['Resulting Role'] = best_role

    return html_template
def _parse_attribute_value(val):
    """Best-effort parse FM attribute values from scouting reports.

    Handles forms like:
    - 14
    - "13-16" or with unicode dashes
    - "14 (13-16)" -> 14
    - "N/A", "-", "—" -> 0
    Returns float.
    """
    # Fast-path for numeric
    if isinstance(val, (int, float, np.integer, np.floating)):
        try:
            # cast to float safely
            return float(val)
        except Exception:
            return 0.0

    if val is None:
        return 0.0

    s = str(val).strip()
    if not s:
        return 0.0

    # Common non-values
    if s.upper() in {"N/A", "NA", "NONE"}:
        return 0.0

    # Normalize unicode dashes to '-'
    s_norm = s.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")

    # If there's a number at the start, prefer it (e.g., "14 (13-16)")
    m_head = re.match(r"\s*(\d{1,3})(?:\D|$)", s_norm)
    if m_head:
        try:
            return float(m_head.group(1))
        except Exception:
            pass

    # Otherwise, if it's a range like "13-16", take midpoint
    # Extract all integers present
    nums = re.findall(r"\d{1,3}", s_norm)
    if len(nums) >= 2 and "-" in s_norm:
        try:
            a, b = int(nums[0]), int(nums[1])
            return (a + b) / 2.0
        except Exception:
            pass

    # If at least one integer, take the first
    if nums:
        try:
            return float(nums[0])
        except Exception:
            return 0.0

    # Fallback: try pandas conversion
    try:
        v = pd.to_numeric(s_norm, errors='coerce')
        return float(v) if pd.notna(v) else 0.0
    except Exception:
        return 0.0


def _coerce_attribute_series(series: pd.Series, col_name: str) -> pd.Series:
    """Convert an attribute column to numeric values robustly.

    - Keeps numeric dtype as-is (fillna(0))
    - Parses strings/ranges to numbers
    - Emits a small debug message once per column if non-numeric values were found
    """
    if series.dtype.kind in {"i", "u", "f"}:
        return series.fillna(0)

    # Identify values that are non-numeric before parsing (sample for debug)
    non_num_mask = pd.to_numeric(series, errors='coerce').isna()
    parsed = series.map(_parse_attribute_value)

    # Debug a few examples to help diagnose future issues
    try:
        if non_num_mask.any():
            examples = list(pd.unique(series[non_num_mask].dropna().astype(str)))[:5]
            if examples:
                print(f"DEBUG: Parsed non-numeric values in '{col_name}' -> numeric. Examples: {examples}")
    except Exception:
        pass

    return pd.Series(parsed, index=series.index).fillna(0.0)


def safe_get(df: pd.DataFrame, col: str):
    """Return a numeric Series for column `col` or zeros if missing.

    Applies robust parsing for scouting report strings (ranges, annotations).
    """
    if col in df.columns:
        return _coerce_attribute_series(df[col], col)
    # return a Series of zeros with same length as df
    return pd.Series([0.0] * len(df), index=df.index)


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Compute derived attributes and role scores. Non-destructive: operates on a copy.

    The function uses safe_get so missing columns are handled gracefully.
    """
    df = df.copy()
    get = lambda c: safe_get(df, c)

    # Build all new columns in a dictionary to avoid DataFrame fragmentation
    new_cols = {}

    # derived columns
    new_cols['Spd'] = (get('Pac') + get('Acc')) / 2
    new_cols['Work'] = (get('Wor') + get('Sta')) / 2

    # example role computations (rounded to 1 decimal)
    new_cols['gkd'] = (((get('Agi') + get('Ref')) * 5 + (get('Cmd') + get('Kic') + get('Pos')) * 3) / 32).round(1)
    new_cols['fb'] = (((get('Wor') + get('Acc') + get('Pac') + get('Sta')) * 5 + (get('Cro') + get('Dri')) * 3) / 20).round(1)
    new_cols['cb'] = (((get('Tck') + get('Mar') + get('Pos')) * 4 + (get('Pas') + get('Hea')) * 2) / 18).round(1)
    new_cols['str'] = (((get('Fin') + get('Pac') + get('Cmp')) * 4) / 12).round(1)

    # Full set of role/position composite scores
    # For efficiency, compute role components and then combine them

    # Helper function to compute role score from key/green/blue components
    def role_score(key_attrs, green_attrs, blue_attrs, total_weight):
        key_sum = sum(get(attr) for attr in key_attrs)
        green_sum = sum(get(attr) for attr in green_attrs)
        blue_sum = sum(get(attr) for attr in blue_attrs)
        return (((key_sum * 5) + (green_sum * 3) + (blue_sum * 1)) / total_weight).round(1)

    # All role computations using the helper function
    new_cols['gkd'] = role_score(['Agi', 'Ref'], ['Aer', 'Cmd', 'Han', 'Kic', 'Cnt', 'Pos'], ['1v1', 'Thr', 'Ant', 'Dec'], 32)
    new_cols['skd'] = role_score(['Agi', 'Ref'], ['Cmd', 'Kic', '1v1', 'Ant', 'Cnt', 'Pos'], ['Aer', 'Fir', 'Han', 'Pas', 'TRO', 'Dec', 'Vis', 'Acc'], 36)
    new_cols['sks'] = role_score(['Agi', 'Ref'], ['Cmd', 'Kic', '1v1', 'Ant', 'Cnt', 'Pos'], ['Aer', 'Fir', 'Han', 'Pas', 'TRO', 'Dec', 'Vis', 'Acc'], 36)
    new_cols['ska'] = role_score(['Agi', 'Ref'], ['Cmd', 'Kic', '1v1', 'Ant', 'Cnt', 'Pos'], ['Aer', 'Fir', 'Han', 'Pas', 'TRO', 'Dec', 'Vis', 'Acc'], 36)
    
    new_cols['bpdd'] = role_score(['Acc', 'Pac', 'Jum', 'Cmp'], ['Hea', 'Mar', 'Pas', 'Tck', 'Pos', 'Str'], ['Fir', 'Tec', 'Agg', 'Ant', 'Bra', 'Cnt', 'Dec', 'Vis'], 46)
    new_cols['bpds'] = role_score(['Acc', 'Pac', 'Jum', 'Cmp'], ['Hea', 'Pas', 'Tck', 'Pos', 'Str', 'Agg', 'Bra', 'Dec'], ['Fir', 'Tec', 'Ant', 'Cnt', 'Vis', 'Mar'], 50)
    new_cols['bpdc'] = role_score(['Acc', 'Pac', 'Jum', 'Cmp'], ['Mar', 'Pas', 'Tck', 'Pos', 'Ant', 'Cnt', 'Dec'], ['Fir', 'Tec', 'Bra', 'Vis', 'Str', 'Hea'], 47)
    
    new_cols['cdd'] = role_score(['Acc', 'Pac', 'Jum', 'Cmp'], ['Hea', 'Mar', 'Tck', 'Pos', 'Str'], ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'], 40)
    new_cols['cds'] = role_score(['Acc', 'Pac', 'Jum', 'Cmp'], ['Hea', 'Tck', 'Agg', 'Bra', 'Dec', 'Pos', 'Str'], ['Mar', 'Ant', 'Cnt'], 44)
    new_cols['cdc'] = role_score(['Acc', 'Pac', 'Jum', 'Cmp'], ['Mar', 'Tck', 'Ant', 'Cnt', 'Dec', 'Pos'], ['Hea', 'Bra', 'Str'], 41)
    
    # Fullback and wingback roles
    new_cols['fb'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Mar', 'Tck', 'Ant', 'Cnt', 'Pos'], ['Cro', 'Pas', 'Dec', 'Tea'], 42)
    new_cols['wba'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'Tck', 'Tec', 'OtB', 'Tea'], ['Fir', 'Mar', 'Pas', 'Ant', 'Cnt', 'Dec', 'Fla', 'Pos', 'Agi', 'Bal'], 48)
    
    # Midfielder roles
    new_cols['aps'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Tea', 'Vis'], ['Dri', 'Ant', 'Fla', 'Agi'], 48)
    new_cols['apa'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Tea', 'Vis'], ['Dri', 'Ant', 'Fla', 'Agi'], 48)
    new_cols['ad'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Mar', 'Tck', 'Ant', 'Cnt', 'Dec', 'Pos'], ['Cmp', 'Tea', 'Str'], 41)
    new_cols['ams'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Fir', 'Lon', 'Pas', 'Tec', 'Ant', 'Dec', 'Fla', 'OtB'], ['Dri', 'Cmp', 'Vis', 'Agi'], 48)
    new_cols['ama'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Fir', 'Lon', 'Pas', 'Tec', 'Ant', 'Dec', 'Fla', 'OtB'], ['Fin', 'Cmp', 'Vis', 'Agi'], 51)
    new_cols['bwmd'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Tck', 'Agg', 'Ant', 'Tea'], ['Mar', 'Bra', 'Cnt', 'Pos', 'Agi', 'Str'], 38)
    new_cols['bwms'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Tck', 'Agg', 'Ant', 'Tea'], ['Mar', 'Pas', 'Bra', 'Cnt', 'Agi', 'Str'], 38)
    new_cols['b2bs'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Pas', 'Tck', 'OtB', 'Tea'], ['Dri', 'Fin', 'Fir', 'Lon', 'Tec', 'Agg', 'Ant', 'Cmp', 'Dec', 'Pos', 'Bal', 'Str'], 44)
    new_cols['cars'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Fir', 'Pas', 'Tck', 'Dec', 'Pos', 'Tea'], ['Tec', 'Ant', 'Cmp', 'Cnt', 'OtB', 'Vis'], 44)
    new_cols['cmd'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Tck', 'Cnt', 'Dec', 'Pos', 'Tea'], ['Fir', 'Mar', 'Pas', 'Tec', 'Agg', 'Ant', 'Cmp'], 42)
    new_cols['cms'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Fir', 'Pas', 'Tck', 'Dec', 'Tea'], ['Tec', 'Ant', 'Cmp', 'Cnt', 'OtB', 'Vis'], 41)
    new_cols['cma'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Fir', 'Pas', 'Dec', 'OtB'], ['Lon', 'Tck', 'Tec', 'Ant', 'Cmp', 'Tea', 'Vis'], 39)
    new_cols['dlpd'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'Tea', 'Vis'], ['Tck', 'Ant', 'Pos', 'Bal'], 45)
    new_cols['dlps'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'Tea', 'Vis'], ['Ant', 'OtB', 'Pos', 'Bal'], 45)
    new_cols['dmd'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Tck', 'Ant', 'Cnt', 'Pos', 'Tea'], ['Mar', 'Pas', 'Agg', 'Cmp', 'Str', 'Dec'], 41)
    new_cols['dms'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Tck', 'Ant', 'Cnt', 'Pos', 'Tea'], ['Fir', 'Mar', 'Pas', 'Agg', 'Cmp', 'Dec', 'Str'], 42)
    new_cols['engs'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'Vis'], ['Dri', 'Ant', 'Fla', 'OtB', 'Tea', 'Agi'], 44)
    new_cols['ifs'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Fin', 'Fir', 'Tec', 'OtB', 'Agi'], ['Lon', 'Pas', 'Ant', 'Cmp', 'Fla', 'Vis', 'Bal'], 45)
    new_cols['ifa'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Fin', 'Fir', 'Tec', 'Ant', 'OtB', 'Agi'], ['Lon', 'Pas', 'Cmp', 'Fla', 'Bal'], 46)
    new_cols['mezs'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Pas', 'Tec', 'Dec', 'OtB'], ['Dri', 'Fir', 'Lon', 'Tck', 'Ant', 'Cmp', 'Vis', 'Bal'], 40)
    new_cols['meza'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Pas', 'Tec', 'Dec', 'OtB', 'Vis'], ['Fin', 'Fir', 'Lon', 'Ant', 'Cmp', 'Fla', 'Bal'], 45)
    
    # Forward roles
    new_cols['afa'] = role_score(['Acc', 'Pac', 'Fin'], ['Dri', 'Fir', 'Tec', 'Cmp', 'OtB'], ['Pas', 'Ant', 'Dec', 'Wor', 'Agi', 'Bal', 'Sta'], 37)
    new_cols['cfs'] = role_score(['Acc', 'Pac', 'Fin'], ['Dri', 'Fir', 'Hea', 'Lon', 'Pas', 'Tec', 'Ant', 'Cmp', 'Dec', 'OtB', 'Vis', 'Agi', 'Str'], ['Tea', 'Wor', 'Bal', 'Jum', 'Sta'], 59)
    new_cols['cfa'] = role_score(['Acc', 'Pac', 'Fin'], ['Dri', 'Fir', 'Hea', 'Tec', 'Ant', 'Cmp', 'OtB', 'Agi', 'Str'], ['Lon', 'Pas', 'Dec', 'Tea', 'Vis', 'Wor', 'Bal', 'Jum', 'Sta'], 51)
    new_cols['dlfs'] = role_score(['Acc', 'Pac', 'Fin'], ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Tea'], ['Ant', 'Fla', 'Vis', 'Bal', 'Str'], 41)
    new_cols['dlfa'] = role_score(['Acc', 'Pac', 'Fin'], ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Tea'], ['Dri', 'Ant', 'Fla', 'Vis', 'Bal', 'Str'], 42)
    new_cols['f9s'] = role_score(['Acc', 'Pac', 'Fin'], ['Dri', 'Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Vis', 'Agi'], ['Ant', 'Fla', 'Tea', 'Bal'], 46)
    new_cols['pa'] = role_score(['Acc', 'Pac', 'Fin'], ['Ant', 'Cmp', 'OtB'], ['Fir', 'Hea', 'Tec', 'Dec'], 28)
    new_cols['pfa'] = role_score(['Acc', 'Pac', 'Fin'], ['Agg', 'Ant', 'Bra', 'OtB', 'Tea', 'Wor', 'Sta'], ['Fir', 'Cmp', 'Cnt', 'Dec', 'Agi', 'Bal', 'Str'], 43)
    new_cols['tfa'] = role_score(['Acc', 'Pac', 'Fin'], ['Hea', 'Bra', 'Cmp', 'OtB', 'Bal', 'Jum', 'Str'], ['Fir', 'Agg', 'Ant', 'Dec', 'Tea'], 41)
    new_cols['trea'] = role_score(['Acc', 'Pac', 'Fin'], ['Dri', 'Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'Fla', 'OtB', 'Vis'], ['Ant', 'Agi', 'Bal'], 45)

    # Add missing roles that were in expected_roles but not calculated
    # Wingback roles
    new_cols['cwbs'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'Tck', 'Tec', 'OtB'], ['Fir', 'Mar', 'Pas', 'Ant', 'Cnt', 'Dec', 'Fla', 'Pos', 'Tea', 'Agi', 'Bal'], 46)
    new_cols['cwba'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'Tck', 'Tec', 'OtB'], ['Fir', 'Mar', 'Pas', 'Ant', 'Cnt', 'Dec', 'Fla', 'Pos', 'Tea', 'Agi', 'Bal'], 46)
    
    # Fullback duty variations
    new_cols['fbd'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Mar', 'Tck', 'Ant', 'Cnt', 'Pos'], ['Cro', 'Pas', 'Dec', 'Tea'], 42)
    new_cols['fbs'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Mar', 'Tck', 'Ant', 'Cnt', 'Pos'], ['Cro', 'Pas', 'Dec', 'Tea'], 42)
    new_cols['fba'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'Mar', 'Tck', 'Ant', 'Cnt', 'Pos'], ['Fir', 'Pas', 'Dec', 'Tea', 'OtB'], 45)
    
    # Inverted/attacking fullbacks
    new_cols['ifbd'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Mar', 'Pas', 'Tck', 'Tec', 'Ant', 'Cnt', 'Dec'], ['Fir', 'Cmp', 'OtB', 'Pos', 'Vis'], 44)
    new_cols['iwbd'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'Mar', 'Tck', 'Tec', 'Ant', 'Cnt', 'Dec'], ['Fir', 'Pas', 'Cmp', 'OtB', 'Pos', 'Vis'], 47)
    new_cols['iwbs'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'Mar', 'Tck', 'Tec', 'Ant', 'Cnt', 'Dec'], ['Fir', 'Pas', 'Cmp', 'OtB', 'Pos', 'Vis'], 47)
    new_cols['iwba'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'Tck', 'Tec', 'OtB'], ['Fir', 'Mar', 'Pas', 'Ant', 'Cnt', 'Dec', 'Cmp', 'Pos', 'Vis'], 44)
    
    # Centre-back variants
    new_cols['ld'] = role_score(['Acc', 'Pac', 'Jum', 'Cmp'], ['Hea', 'Mar', 'Tck', 'Pos', 'Str'], ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'], 40)
    new_cols['ls'] = role_score(['Acc', 'Pac', 'Jum', 'Cmp'], ['Hea', 'Mar', 'Tck', 'Pos', 'Str'], ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'], 40)
    new_cols['ncbd'] = role_score(['Acc', 'Pac', 'Jum', 'Cmp'], ['Hea', 'Mar', 'Tck', 'Pos', 'Str'], ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'], 40)
    new_cols['ncbs'] = role_score(['Acc', 'Pac', 'Jum', 'Cmp'], ['Hea', 'Mar', 'Tck', 'Pos', 'Str'], ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'], 40)
    new_cols['ncbc'] = role_score(['Acc', 'Pac', 'Jum', 'Cmp'], ['Hea', 'Mar', 'Tck', 'Pos', 'Str'], ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'], 40)
    new_cols['nfbd'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Mar', 'Tck', 'Ant', 'Cnt', 'Pos'], ['Cro', 'Pas', 'Dec', 'Tea'], 42)
    new_cols['wcbd'] = role_score(['Acc', 'Pac', 'Jum', 'Cmp'], ['Hea', 'Mar', 'Tck', 'Pos', 'Str'], ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'], 40)
    new_cols['wcbs'] = role_score(['Acc', 'Pac', 'Jum', 'Cmp'], ['Hea', 'Mar', 'Tck', 'Pos', 'Str'], ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'], 40)
    new_cols['wcba'] = role_score(['Acc', 'Pac', 'Jum', 'Cmp'], ['Hea', 'Mar', 'Tck', 'Pos', 'Str'], ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'], 40)
    new_cols['wbd'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'Tck', 'Tec', 'OtB', 'Tea'], ['Fir', 'Mar', 'Pas', 'Ant', 'Cnt', 'Dec', 'Fla', 'Pos', 'Agi', 'Bal'], 48)
    new_cols['wbs'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'Tck', 'Tec', 'OtB', 'Tea'], ['Fir', 'Mar', 'Pas', 'Ant', 'Cnt', 'Dec', 'Fla', 'Pos', 'Agi', 'Bal'], 48)
    
    # More midfielder roles
    new_cols['dwd'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Tck', 'Ant', 'Cnt', 'Pos', 'Tea'], ['Mar', 'Pas', 'Agg', 'Cmp', 'Str', 'Dec'], 41)
    new_cols['dws'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Tck', 'Ant', 'Cnt', 'Pos', 'Tea'], ['Fir', 'Mar', 'Pas', 'Agg', 'Cmp', 'Dec', 'Str'], 42)
    new_cols['hbd'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Tck', 'Agg', 'Ant', 'Tea'], ['Mar', 'Bra', 'Cnt', 'Pos', 'Agi', 'Str'], 38)
    new_cols['iws'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Pas', 'Tec', 'Dec', 'OtB'], ['Fir', 'Cmp', 'Vis', 'Agi', 'Bal'], 39)
    new_cols['iwa'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Pas', 'Tec', 'Dec', 'OtB'], ['Fin', 'Fir', 'Cmp', 'Vis', 'Agi', 'Bal'], 40)
    new_cols['raua'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Fir', 'Pas', 'Tec', 'Ant', 'Dec', 'OtB'], ['Cmp', 'Vis', 'Agi', 'Bal'], 43)
    new_cols['regs'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'Tea', 'Vis'], ['Ant', 'OtB', 'Pos', 'Bal'], 45)
    new_cols['rps'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'Tea', 'Vis'], ['Tck', 'Ant', 'Pos', 'Bal'], 45)
    new_cols['svs'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Vis'], ['Ant', 'Fla', 'Agi', 'Bal'], 44)
    new_cols['sva'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Vis'], ['Fin', 'Ant', 'Fla', 'Agi', 'Bal'], 45)
    new_cols['ssa'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Vis'], ['Fin', 'Ant', 'Fla', 'Agi', 'Bal'], 45)
    new_cols['wmd'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Tck', 'Ant', 'Cnt', 'Pos', 'Tea'], ['Mar', 'Pas', 'Agg', 'Cmp', 'Str', 'Dec'], 41)
    new_cols['wms'] = role_score(['Wor', 'Sta', 'Acc', 'Pac'], ['Tck', 'Ant', 'Cnt', 'Pos', 'Tea'], ['Fir', 'Mar', 'Pas', 'Agg', 'Cmp', 'Dec', 'Str'], 42)
    new_cols['wma'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Pas', 'Tec', 'Dec', 'OtB'], ['Fin', 'Fir', 'Cmp', 'Vis', 'Agi', 'Bal'], 40)
    new_cols['wps'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Vis'], ['Fin', 'Fir', 'Lon', 'Ant', 'Fla', 'Bal'], 45)
    new_cols['wpa'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Vis'], ['Fin', 'Fir', 'Lon', 'Ant', 'Fla', 'Bal'], 45)
    new_cols['wtfs'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Fin', 'Fir', 'Tec', 'OtB', 'Agi'], ['Lon', 'Pas', 'Ant', 'Cmp', 'Fla', 'Vis', 'Bal'], 45)
    new_cols['wtfa'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Dri', 'Fin', 'Fir', 'Tec', 'Ant', 'OtB', 'Agi'], ['Lon', 'Pas', 'Cmp', 'Fla', 'Bal'], 46)
    new_cols['ws'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'Tck', 'Tec', 'OtB'], ['Fir', 'Mar', 'Pas', 'Ant', 'Cnt', 'Dec', 'Fla', 'Pos', 'Tea', 'Agi', 'Bal'], 44)
    new_cols['wa'] = role_score(['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'Tec', 'OtB'], ['Fir', 'Pas', 'Ant', 'Dec', 'Fla', 'Tea', 'Agi', 'Bal'], 40)
    
    # Forward role variants
    new_cols['pfd'] = role_score(['Acc', 'Pac', 'Fin'], ['Agg', 'Ant', 'Bra', 'OtB', 'Tea', 'Wor', 'Sta'], ['Fir', 'Cmp', 'Cnt', 'Dec', 'Agi', 'Bal', 'Str'], 43)
    new_cols['pfs'] = role_score(['Acc', 'Pac', 'Fin'], ['Agg', 'Ant', 'Bra', 'OtB', 'Tea', 'Wor', 'Sta'], ['Fir', 'Cmp', 'Cnt', 'Dec', 'Agi', 'Bal', 'Str'], 43)
    new_cols['tfs'] = role_score(['Acc', 'Pac', 'Fin'], ['Hea', 'Bra', 'Cmp', 'OtB', 'Bal', 'Jum', 'Str'], ['Fir', 'Agg', 'Ant', 'Dec', 'Tea'], 41)

    # Add all expected role columns with default values for missing ones
    expected_roles = [
        'gkd','skd','sks','ska','bpdd','bpds','bpdc','cdd','cds','cdc','cwbs','cwba',
        'fbd','fbs','fba','ifbd','iwbd','iwbs','iwba','ld','ls','ncbd','ncbs','ncbc',
        'nfbd','wcbd','wcbs','wcba','wbd','wbs','wba','aps','apa','ad','ams','ama',
        'bwmd','bwms','b2bs','cars','cmd','cms','cma','dlpd','dlps','dmd','dms','dwd',
        'dws','engs','hbd','ifs','ifa','iws','iwa','mezs','meza','raua','regs','rps',
        'svs','sva','ssa','wmd','wms','wma','wps','wpa','wtfs','wtfa','ws','wa','afa',
        'cfs','cfa','dlfs','dlfa','f9s','pa','pfd','pfs','pfa','tfs','tfa','trea'
    ]
    
    # Set default values for roles not yet computed
    for role in expected_roles:
        if role not in new_cols:
            new_cols[role] = pd.Series([0.0] * len(df), index=df.index)

    # Make an easily-consumable 'Jmp' column for output mapped from 'Jum' (if present)
    if 'Jum' in df.columns:
        new_cols['Jmp'] = df['Jum']
    else:
        new_cols['Jmp'] = pd.Series([0] * len(df), index=df.index)

    # Create a DataFrame from new columns and concatenate with original
    new_df = pd.DataFrame(new_cols, index=df.index)
    result_df = pd.concat([df, new_df], axis=1)

    # Compute Best_Score and Best_Role
    # Include only calculated role scores, not raw FM attributes
    numeric_cols = result_df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Exclude player info columns AND raw FM attributes 
    raw_fm_attributes = [
        'Acc', 'Aer', 'Agg', 'Agi', 'Ant', 'App', 'Bal', 'Bra', 'Cmd', 'Cmp', 'Cnt', 'Cor', 
        'Cro', 'Dec', 'Det', 'Dri', 'Fin', 'Fir', 'Fla', 'Han', 'Hea', 'Jum', 'Kic', 'Ldr',
        'Lon', 'Mar', 'Nat', 'OtB', 'Pac', 'Pas', 'Pos', 'Ref', 'Sta', 'Str', 'Tck', 'Tea',
        'Tec', 'TRO', 'Vis', 'Wor', '1v1', 'Thr', 'Age', 'CA', 'PA'
    ]
    
    exclude_cols = raw_fm_attributes + ['Work', 'Spd', 'Jmp']  # Also exclude composite stats
    
    # Also exclude any UID columns (case-insensitive)
    score_cols = [col for col in numeric_cols if col not in exclude_cols and 'uid' not in col.lower()]
    
    if score_cols:
        result_df['Best_Score'] = result_df[score_cols].max(axis=1)
        result_df['Best_Role'] = result_df[score_cols].idxmax(axis=1)
    else:
        result_df['Best_Score'] = 0
        result_df['Best_Role'] = ''

    return result_df


def main(folder: str):
    latest = find_latest_file(folder)
    if not latest:
        print("No files found in", folder)
        return

    # read html tables; pick first table
    try:
        tables = pd.read_html(latest, header=0, keep_default_na=False)
    except Exception as e:
        print("Failed to read HTML:", e)
        return

    if not tables:
        print("No tables found in", latest)
        return

    squad_rawdata = tables[0]

    # compute scores; will handle missing columns gracefully
    squad_rawdata = compute_scores(squad_rawdata)
    
    # DEBUG: Check if best score columns exist
    print(f"DEBUG: After compute_scores, 'Highest Role Score' in columns: {'Highest Role Score' in squad_rawdata.columns}")
    print(f"DEBUG: After compute_scores, 'Resulting Role' in columns: {'Resulting Role' in squad_rawdata.columns}")

    # select columns to export (only include those present)
    # Full ordered list: basic player info, derived stats, jump, all role scores, some common composites, and final role picks
    wanted = [
        'Name','Age','Club','Position',
        'Spd','str','Work','Jmp',
        # goalkeeper and keeper variants
        'gkd','skd','sks','ska',
        # defenders
        'bpdd','bpds','bpdc','cdd','cds','cdc','cwbs','cwba','fbd','fbs','fba','ifbd','iwbd','iwbs','iwba',
        'ld','ls','ncbd','ncbs','ncbc','nfbd','wcbd','wcbs','wcba','wbd','wbs','wba',
        # midfield / wing / support
        'aps','apa','ad','ams','ama','bwmd','bwms','b2bs','cars','cmd','cms','cma','dlpd','dlps','dmd','dms','dwd','dws',
        'engs','hbd','ifs','ifa','iws','iwa','mezs','meza','raua','regs','rps','svs','sva','ssa','wmd','wms','wma','wps','wpa',
        'wtfs','wtfa','ws','wa','afa','cfs','cfa','dlfs','dlfa','f9s','pa','pfd','pfs','pfa','tfs','tfa','trea',
        # some additional common composites
        'fb','cb',
        # final picks
        'Best_Score','Best_Role'
    ]
    available = [c for c in wanted if c in squad_rawdata.columns]
    print(f"DEBUG: Available columns include 'Highest Role Score': {'Highest Role Score' in available}")
    print(f"DEBUG: Available columns include 'Resulting Role': {'Resulting Role' in available}")
    squad = squad_rawdata[available]
    print(f"DEBUG: Final squad dataframe columns: {len(squad.columns)}")
    print(f"DEBUG: Final squad has 'Highest Role Score': {'Highest Role Score' in squad.columns}")

    html = generate_html(squad)
    outname = uuid.uuid4().hex + ".html"
    outpath = os.path.join(folder, outname)
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(html)

    print("Wrote:", outpath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert FM exported HTML to scored sortable HTML.")
    default_folder = r"C:\Users\Fluff\OneDrive\Desktop\FM"
    parser.add_argument("--folder", "-f", default=default_folder, help="Folder to search for latest exported HTML")
    args = parser.parse_args()
    folder = args.folder.rstrip('\\/')
    main(folder)