"""
HTML generation module for Football Manager player analysis.

This module handles the creation of interactive HTML reports with styling,
JavaScript functionality, and data visualization.
"""

import pandas as pd
import json
from typing import Dict, List, Tuple
import logging

from role_definitions import ROLE_DISPLAY_NAMES, FULL_ROLE_DESCRIPTIONS

logger = logging.getLogger(__name__)

POSITION_ROLE_GROUPS = {
    "Attacking Midfielder (Central)": ["AMA", "AMS", "APA", "APS", "TFS", "TFA", "TREA", "SSA"],
    "Striker": ["DLFA", "DLFS", "DLPD", "DLPS", "AFA", "TFA", "TFS", "PA", "CFA", "CFS", "PFD", "PFS", "PFA", "TFEA", "F9S"],
    "Midfield (Central)": ["CMA", "CMD", "CMS", "DLPD", "DLPS", "B2BS", "APA", "APS", "BWMD", "BWMS", "RPS", "MEZS", "MEZA", "CARS"],
    "Defender (Left/Right)": ["FBA", "FBD", "FBS", "WBD", "WBS", "WBA", "NFBD", "CWBA", "CWBS", "IWBD", "IWBS", "IWBA", "IFBD", "IFBS"],
    "Defender (Central)": ["CDC", "CDD", "CDS", "LD", "LS", "BPDC", "BPDD", "BPDS", "NCBD", "NCBS", "NCBC", "WCBD", "WCBS", "WCBA"],
    "Goalkeeper": ["GKD", "SKD", "SKS", "SKA"]
}


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
        """Generate the grouped role legend HTML."""
        present_codes = set()
        for orig_key, short in ROLE_DISPLAY_NAMES.items():
            code = short.upper()
            if code in display_df.columns or orig_key in display_df.columns or short in display_df.columns:
                present_codes.add(code)
        group_html = []
        for group, codes in POSITION_ROLE_GROUPS.items():
            codes_in_table = [c for c in codes if c in present_codes]
            if not codes_in_table:
                continue
            items = []
            for code in codes_in_table:
                desc = FULL_ROLE_DESCRIPTIONS.get(code, code)
                items.append(f'<div class="legend-row clickable" data-code="{code}" data-active="1" onclick="legendToggleRole(this)"><code>{code}</code> &nbsp;&rarr;&nbsp; <strong>{desc}</strong></div>')
            group_html.append(f'<div class="legend-group" style="margin-bottom:10px;"><div style="display:flex;align-items:center;gap:8px;"><strong>{group}</strong><button class="legend-toggle" onclick="enableRoleGroup(\'{group}\')">Show all</button><button class="legend-toggle" onclick="disableRoleGroup(\'{group}\')">Hide all</button></div><div style="margin-left:12px;">' + ''.join(items) + '</div></div>')
        if not group_html:
            return '<div class="legend" style="margin-bottom:6px; font-size:11px; color:#666;">Legend not available</div>'
        legend_html = f'<div class="legend" style="margin-bottom:6px; display:none;">'
        legend_html += '<div style="display:flex; align-items:center; gap:16px; margin-bottom:8px;">'
        legend_html += '<button class="legend-toggle" onclick="enableAllRoles()">Show All</button>'
        legend_html += '<button class="legend-toggle" onclick="disableAllRoles()">Hide All</button>'
        legend_html += '</div>'
        legend_html += '<div style="display:flex; flex-wrap:wrap; gap:24px;">'
        for group_html_block in group_html:
            # Replace Show all/Hide all with Show/Hide
            group_html_block = group_html_block.replace('Show all', 'Show').replace('Hide all', 'Hide')
            legend_html += f'<div style="flex:1 1 320px; min-width:220px;">{group_html_block}</div>'
        legend_html += '</div></div>'
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
        /* Sortable header indicators */
    #playerTable th.sortable { cursor: pointer; }
    #playerTable th.sortable:hover { background-color: #3b5168; }
    /* Use literal symbols to avoid Python string escape issues */
    #playerTable th.sort-asc::after { content: " ▲"; font-size: 10px; margin-left: 4px; }
    #playerTable th.sort-desc::after { content: " ▼"; font-size: 10px; margin-left: 4px; }
        
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

        // ---------- Sorting utilities ----------
        function parseNumberLike(text) {
            if (text == null) return NaN;
            let t = String(text).trim().toUpperCase();
            if (!t) return NaN;
            // Remove currency, commas and percent
            t = t.replace(/[£$,%\s]/g, '');
            // Handle ranges like "12-14" by taking the average
            if (/^-?\d+(?:\.\d+)?\s*[-–]\s*-?\d+(?:\.\d+)?$/.test(t)) {
                const parts = t.split(/[-–]/).map(s => parseFloat(s));
                if (!isNaN(parts[0]) && !isNaN(parts[1])) return (parts[0] + parts[1]) / 2;
            }
            // Suffixes K/M/B
            const m = t.match(/^(-?\d+(?:\.\d+)?)([KMB])?$/);
            if (m) {
                let n = parseFloat(m[1]);
                const suf = m[2];
                if (suf === 'K') n *= 1e3;
                else if (suf === 'M') n *= 1e6;
                else if (suf === 'B') n *= 1e9;
                return n;
            }
            // Fallback: just parseFloat beginning of string
            const n = parseFloat(t);
            return isNaN(n) ? NaN : n;
        }

        function getCellText(row, idx) {
            if (!row) return '';
            const cell = row.cells[idx];
            if (!cell) return '';
            return (cell.textContent || cell.innerText || '').trim();
        }

        function detectNumericColumn(table, colIndex) {
            const rows = Array.from(table.querySelectorAll('tbody tr'));
            let seen = 0, numeric = 0;
            for (let i = 0; i < rows.length && seen < 30; i++) {
                const txt = getCellText(rows[i], colIndex);
                if (txt !== '') {
                    seen++;
                    const val = parseNumberLike(txt);
                    if (!isNaN(val)) numeric++;
                }
            }
            return numeric > 0 && numeric >= Math.max(1, Math.floor(seen * 0.6));
        }

        function sortTableByColumn(table, colIndex, desc) {
            const tbody = table.querySelector('tbody');
            if (!tbody) return;
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const isNumeric = detectNumericColumn(table, colIndex);
            const withIndex = rows.map((row, i) => ({ row, i }));

            withIndex.sort((a, b) => {
                const ta = getCellText(a.row, colIndex);
                const tb = getCellText(b.row, colIndex);
                if (isNumeric) {
                    const va = parseNumberLike(ta);
                    const vb = parseNumberLike(tb);
                    const aNaN = isNaN(va), bNaN = isNaN(vb);
                    if (aNaN && bNaN) return a.i - b.i; // stable
                    if (aNaN) return 1; // NaN to bottom
                    if (bNaN) return -1;
                    return va === vb ? (a.i - b.i) : (va - vb);
                } else {
                    const sa = ta.toLowerCase();
                    const sb = tb.toLowerCase();
                    const cmp = sa.localeCompare(sb);
                    return cmp === 0 ? (a.i - b.i) : cmp;
                }
            });

            if (desc) withIndex.reverse();
            // Reattach in sorted order
            withIndex.forEach(w => tbody.appendChild(w.row));
        }

        function clearSortIndicators(table) {
            table.querySelectorAll('thead th').forEach(th => {
                th.classList.remove('sort-asc', 'sort-desc');
            });
        }

        function initSorting() {
            const table = document.getElementById('playerTable');
            if (!table) return;
            const headers = table.querySelectorAll('thead th');
            headers.forEach((th, idx) => {
                th.classList.add('sortable');
                th.addEventListener('click', function() {
                    const currentlyAsc = th.classList.contains('sort-asc');
                    const currentlyDesc = th.classList.contains('sort-desc');
                    const nextDesc = currentlyAsc && !currentlyDesc ? true : !currentlyDesc ? false : false; // toggle asc->desc, unsorted->asc, desc->asc
                    // Determine direction: cycles asc -> desc -> asc
                    const desc = currentlyAsc ? true : (currentlyDesc ? false : false);
                    // Apply sort
                    sortTableByColumn(table, idx, desc);
                    // Update indicators
                    clearSortIndicators(table);
                    th.classList.add(desc ? 'sort-desc' : 'sort-asc');
                });
            });
        }

        function defaultSortByHeaderName(name, desc){
            const table = document.getElementById('playerTable');
            if (!table) return;
            const idxMap = headerIndex();
            const key = String(name || '').trim().toUpperCase();
            const indices = idxMap[key];
            if (!indices || indices.length === 0) return;
            const colIndex = Array.isArray(indices) ? indices[0] : indices;
            sortTableByColumn(table, colIndex, !!desc);
            clearSortIndicators(table);
            const th = table.querySelectorAll('thead th')[colIndex];
            if (th) th.classList.add(desc ? 'sort-desc' : 'sort-asc');
        }

        // External toggle for legend
        function toggleLegendExternal(extBtn) {
            const legend = document.querySelector('.legend');
            if (!legend) return;
            const isHidden = window.getComputedStyle(legend).display === 'none';
            legend.style.display = isHidden ? 'block' : 'none';
            if (extBtn) extBtn.textContent = isHidden ? 'Hide legend' : 'Show legend';
        }

        // Initialize sorting and best formations functionality
        document.addEventListener('DOMContentLoaded', function() {
            try { initSorting(); } catch (e) { console && console.error && console.error('Sorting init error:', e); }
            // Apply role tooltips on headers
            try { applyRoleHeaderTooltips(); } catch (e) { console && console.error && console.error('Header tooltip error:', e); }
            try { defaultSortByHeaderName('Best Score', true); } catch (e) { console && console.error && console.error('Default sort error:', e); }
        });

        // Best formations functionality
        function toggleBestFormations(){
            const p = document.getElementById('bestFormationsPanel');
            if (!p) return;
            const isHidden = window.getComputedStyle(p).display === 'none';
            p.style.display = isHidden ? 'block' : 'none';
        }
        
        // Role header tooltips
        function applyRoleHeaderTooltips(){
            try {
                const table = document.getElementById('playerTable');
                if (!table || typeof ROLE_TITLES !== 'object') return;
                const headers = table.querySelectorAll('thead th');
                headers.forEach(th => {
                    const key = (th.textContent || '').trim().toUpperCase();
                    if (ROLE_TITLES[key]) {
                        th.title = ROLE_TITLES[key];
                    }
                });
            } catch (e) {
                console && console.warn && console.warn('Tooltip application failed', e);
            }
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

        // Group show/hide logic
        function enableRoleGroup(group) {
            const codes = POSITION_ROLE_GROUPS[group];
            if (!codes) return;
            codes.forEach(function(code) {
                setColumnVisibilityByCode(code, true);
                document.querySelectorAll('.legend-row[data-code="'+code+'"]').forEach(function(row) {
                    updateLegendRowState(row, true);
                });
            });
        }
        function disableRoleGroup(group) {
            const codes = POSITION_ROLE_GROUPS[group];
            if (!codes) return;
            codes.forEach(function(code) {
                setColumnVisibilityByCode(code, false);
                document.querySelectorAll('.legend-row[data-code="'+code+'"]').forEach(function(row) {
                    updateLegendRowState(row, false);
                });
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
        
        role_titles_json = json.dumps(FULL_ROLE_DESCRIPTIONS)
        position_role_groups_json = json.dumps(POSITION_ROLE_GROUPS)
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
    <div class="table-container">{table_html}</div>
    <script>
        // Map of role codes to full names for header tooltips
        const ROLE_TITLES = {role_titles_json};
        // Position to role group mapping for legend controls
        const POSITION_ROLE_GROUPS = {position_role_groups_json};
        {javascript}
        // Group show/hide logic
        function enableRoleGroup(group) {{
            const codes = POSITION_ROLE_GROUPS[group];
            if (!codes) return;
            codes.forEach(function(code) {{
                setColumnVisibilityByCode(code, true);
                document.querySelectorAll('.legend-row[data-code="'+code+'"]').forEach(function(row) {{
                    updateLegendRowState(row, true);
                }});
            }});
        }}
        function disableRoleGroup(group) {{
            const codes = POSITION_ROLE_GROUPS[group];
            if (!codes) return;
            codes.forEach(function(code) {{
                setColumnVisibilityByCode(code, false);
                document.querySelectorAll('.legend-row[data-code="'+code+'"]').forEach(function(row) {{
                    updateLegendRowState(row, false);
                }});
            }});
        }}
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