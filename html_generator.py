"""
HTML generation module for Football Manager player analysis.

This module handles the creation of interactive HTML reports with styling,
JavaScript functionality, and data visualization.
"""

import pandas as pd
from typing import Dict, List, Tuple
import logging

from role_definitions import ROLE_DISPLAY_NAMES, FULL_ROLE_DESCRIPTIONS

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """Generates interactive HTML reports for FM player analysis."""
    
    def __init__(self):
        self.column_titles = self._get_column_title_mappings()
    
    def _get_column_title_mappings(self) -> Dict[str, str]:
        """Get mapping of internal column names to display names."""
        base_mappings = {
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
            'Best_Score': 'Best Score',
            'Best_Role': 'Best Role'
        }
        
        # Add role display names
        base_mappings.update(ROLE_DISPLAY_NAMES)
        
        return base_mappings
    
    def generate_html_report(self, dataframe: pd.DataFrame) -> str:
        """
        Generate complete HTML report from processed FM data.
        
        Args:
            dataframe: Processed DataFrame with all computed scores
            
        Returns:
            Complete HTML string for the report
        """
        logger.info(f"Generating HTML report for {len(dataframe)} players")
        
        # Prepare data for display
        display_df = self._prepare_display_data(dataframe)
        
        # Generate components
        table_html = self._generate_table_html(display_df)
        legend_html = self._generate_legend_html(display_df)
        
        # Combine into full HTML document
        html_content = self._generate_full_html(table_html, legend_html)
        
        logger.info("HTML report generated successfully")
        return html_content
    
    def _prepare_display_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Prepare DataFrame for display with proper column ordering and naming."""
        
        # Order columns for better display
        wanted_order = [
            'Name', 'Age', 'Club', 'Position',
            'Best_Score', 'Best_Role',
            'Spd', 'str', 'Work', 'Jmp'
        ]
        
        # Add all role columns that exist
        for role_code in ROLE_DISPLAY_NAMES.keys():
            if role_code in dataframe.columns:
                wanted_order.append(role_code)
        
        # Add any remaining columns
        for col in dataframe.columns:
            if col not in wanted_order:
                wanted_order.append(col)
        
        # Filter to only available columns
        ordered_cols = [col for col in wanted_order if col in dataframe.columns]
        display_df = dataframe[ordered_cols].copy()
        
        # Rename columns for display
        display_df.columns = [self.column_titles.get(col, col) for col in display_df.columns]
        
        logger.debug(f"Prepared display data with {len(display_df.columns)} columns")
        return display_df
    
    def _generate_table_html(self, display_df: pd.DataFrame) -> str:
        """Generate the main data table HTML."""
        return display_df.to_html(
            table_id="playerTable", 
            index=False, 
            escape=False,
            classes="display compact nowrap"
        )
    
    def _generate_legend_html(self, display_df: pd.DataFrame) -> str:
        """Generate the role legend HTML."""
        
        # Find role codes present in the table
        present_codes = []
        for orig_key, short in ROLE_DISPLAY_NAMES.items():
            if orig_key.islower() and orig_key != 'str':  # Exclude composite metrics
                code = short.upper()
                # Include if column exists in display table
                if (code in display_df.columns or 
                    orig_key in display_df.columns or 
                    short in display_df.columns):
                    present_codes.append(code)
        
        # Remove duplicates while preserving order
        present_codes = list(dict.fromkeys(present_codes))
        
        if not present_codes:
            return '<div class="legend" style="margin-bottom:6px; font-size:11px; color:#666;">Legend not available</div>'
        
        # Build role pairs with descriptions
        role_pairs = self._build_role_pairs(present_codes)
        
        # Split into two columns for better layout
        half = (len(role_pairs) + 1) // 2
        left_pairs = role_pairs[:half]
        right_pairs = role_pairs[half:]
        
        left_html = self._generate_legend_column(left_pairs)
        right_html = self._generate_legend_column(right_pairs)
        
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
        
        return legend_html
    
    def _build_role_pairs(self, present_codes: List[str]) -> List[Tuple[str, str]]:
        """Build list of (code, description) pairs for legend."""
        role_pairs = []
        suffix_map = {'A': 'Attack', 'D': 'Defend', 'S': 'Support'}
        
        for code in present_codes:
            if code in FULL_ROLE_DESCRIPTIONS:
                role_pairs.append((code, FULL_ROLE_DESCRIPTIONS[code]))
            else:
                # Fallback: split last letter as duty if it's A/D/S
                if len(code) > 1 and code[-1] in suffix_map:
                    base = code[:-1]
                    description = f"{base} {suffix_map[code[-1]]}"
                    role_pairs.append((code, description))
                else:
                    role_pairs.append((code, code))
        
        return role_pairs
    
    def _generate_legend_column(self, role_pairs: List[Tuple[str, str]]) -> str:
        """Generate HTML for one column of the legend."""
        items = []
        for code, description in role_pairs:
            item = (f'<div class="legend-row clickable" data-code="{code}" '
                   f'data-active="1" onclick="legendToggleRole(this)">'
                   f'<code>{code}</code> &nbsp;&rarr;&nbsp; <strong>{description}</strong>'
                   f'</div>')
            items.append(item)
        return ''.join(items)
    
    def _generate_css_styles(self) -> str:
        """Generate CSS styles for the HTML report."""
        return """
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            width: 100%;
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
        
        /* Legend styling */
        .legend { font-size: 11px; color: #333; }
        .legend-row { margin-bottom: 4px; }
        .legend-row.clickable { cursor: pointer; user-select: none; }
        .legend-row.inactive { opacity: 0.6; }
        .legend-row.inactive code { text-decoration: line-through; color:#888; background:#f0f0f0; }
        .legend small { color: #666; margin-left: 6px; }
        .legend code { 
            font-family: Consolas, "Courier New", monospace; 
            font-size: 10px; 
            color: #444; 
            background:#f7f7f7; 
            padding:2px 4px; 
            border-radius:3px; 
        }
        .legend-toggle { 
            margin-left: 8px; 
            padding:4px 8px; 
            font-size:11px; 
            cursor:pointer; 
            background:#ddd; 
            border-radius:4px; 
            border:1px solid #ccc; 
        }

        /* Best formations panel */
        #bestFormationsPanel { display:none; margin-top:10px; }
        #bestFormationsPanel .row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
        #bestFormationsResults { margin-top:8px; font-size:12px; }
        #bestFormationsResults table { width:100%; border-collapse: collapse; margin-bottom:14px; }
        #bestFormationsResults th, #bestFormationsResults td { border:1px solid #ddd; padding:6px; text-align:left; font-size:12px; }
        .muted { color:#666; }
        """
    
    def _generate_javascript(self) -> str:
        """Generate JavaScript functionality for the HTML report."""
        return """
        // Simple filtering without DataTables
        function filterByPosition(btn, position) {
            // reset active state
            document.querySelectorAll('.position-filter').forEach(b => b.classList.remove('active'));
            if (btn && btn.classList) btn.classList.add('active');

            const rows = document.querySelectorAll('#playerTable tbody tr');
            rows.forEach(row => {
                const positionCell = row.cells[3]; // Position is 4th column (index 3)
                if (!positionCell) return;
                let posText = (positionCell.textContent || positionCell.innerText || '').toUpperCase().trim();
                posText = posText.replace(/[^A-Z0-9]/g, ' ').trim();
                const tokens = posText.split(/\\s+/);
                let match = false;
                if (position === 'GK') {
                    match = tokens.includes('GK');
                } else if (position === 'D') {
                    match = tokens.some(t => t.startsWith('D') && t !== 'DM');
                } else if (position === 'M') {
                    match = tokens.includes('DM') || tokens.some(t => t.startsWith('M')) || tokens.some(t => t.startsWith('AM'));
                } else if (position === 'F') {
                    match = tokens.some(t => t.includes('ST'));
                }
                row.style.display = match ? '' : 'none';
            });
        }

        function clearFilters(btn) {
            document.querySelectorAll('.position-filter').forEach(b => b.classList.remove('active'));
            const rows = document.querySelectorAll('#playerTable tbody tr');
            rows.forEach(row => row.style.display = '');
        }
        
        // Color code score cells after page loads
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
                console && console.error && console.error('Coloring error:', e);
            }
        });

        // External toggle for legend
        function toggleLegendExternal(extBtn) {
            const legend = document.querySelector('.legend');
            if (!legend) return;
            const isHidden = window.getComputedStyle(legend).display === 'none';
            legend.style.display = isHidden ? 'block' : 'none';
            if (extBtn) extBtn.textContent = isHidden ? 'Hide legend' : 'Show legend';
        }

        // Best formations functionality
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

        // Column visibility via legend
        function setColumnVisibilityByIndex(colIndex, visible){
            if (colIndex == null || colIndex < 0) return;
            const table = document.getElementById('playerTable');
            if (!table) return;
            const th = table.querySelectorAll('thead th')[colIndex];
            if (th) th.style.display = visible ? '' : 'none';
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
        """
    
    def _generate_formation_analyzer(self) -> str:
        """Generate formation analysis textarea content."""
        return """
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
        """
    
    def _generate_full_html(self, table_html: str, legend_html: str) -> str:
        """Generate the complete HTML document."""
        
        css_styles = self._generate_css_styles()
        javascript = self._generate_javascript()
        formation_content = self._generate_formation_analyzer()
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>FM Player Analysis</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <style>
        {css_styles}
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
{formation_content}
            </textarea>
        </div>
    </div>
    
    <!-- Legend inserted here -->
    {legend_html}

    <div class="table-container">
        {table_html}
    </div>
    
    <script>
        {javascript}
    </script>
</body>
</html>
        """
        
        return html_template


def create_html_report(dataframe: pd.DataFrame) -> str:
    """
    Create an HTML report from processed FM data.
    
    Args:
        dataframe: Processed DataFrame with all computed scores
        
    Returns:
        Complete HTML string for the report
    """
    generator = HTMLGenerator()
    return generator.generate_html_report(dataframe)


logger.info("HTML generator module loaded successfully")