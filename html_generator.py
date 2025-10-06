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
    "Goalkeeper": ["GKD", "SKD", "SKS", "SKA"],
    "Defender (Left/Right)": ["FBA", "FBD", "FBS", "WBD", "WBS", "WBA", "NFBD", "CWBA", "CWBS", "IWBD", "IWBS", "IWBA", "IFBD", "IFBS"],
    "Defender (Central)": ["CDC", "CDD", "CDS", "LD", "LS", "BPDC", "BPDD", "BPDS", "NCBD", "NCBS", "NCBC", "WCBD", "WCBS", "WCBA"],
    "Defensive Midfielder": ["DMD", "DMS", "DLPD", "DLPS", "BWMD", "BWMS", "AD", "HBD", "REGS", "RPS", "SVS", "SVA"],
    "Midfield (Central)": ["CMA", "CMD", "CMS", "DLPD", "DLPS", "B2BS", "APA", "APS", "BWMD", "BWMS", "RPS", "MEZS", "MEZA", "CARS"],
    "Midfielder (Left/Right)": ["WMD", "WMS", "WMA", "WS", "WA", "DWD", "DWS", "WPS", "WPA", "IWA", "IWS"],
    "Attacking Midfielder (Central)": ["AMA", "AMS", "APA", "APS", "ENGS", "TREA", "SSA"],
    "Attacking Midfielder (Left/Right)": ["WS", "WA", "APA", "APS", "IFA", "IFS", "TREA", "WTFS", "WTFA", "RAUA", "IWA", "IWS"],
    "Striker": ["DLFA", "DLFS", "DLPD", "DLPS", "AFA", "TFA", "TFS", "PA", "CFA", "CFS", "PFD", "PFS", "PFA", "TFEA", "F9S"]        
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

        # Add position filter buttons above the table
        position_filters_html = self._generate_position_filters_html()
        
        # Combine into full HTML document
        html_content = self._generate_full_html(position_filters_html + table_html, legend_html)
        
        logger.info("HTML report generated successfully")
        return html_content
    def _generate_position_filters_html(self) -> str:
        """Generate HTML for position filter buttons above the table."""
        # Position definitions and display names
        positions = [
            ("GK", "Goalkeeper"),
            ("DL", "DL / WB (L)"),
            ("DC", "DC"),
            ("DR", "DR / WB (R)"),
            ("DM", "DM"),
            ("ML", "ML"),
            ("MC", "MC"),
            ("MR", "MR"),
            ("AML", "AML"),
            ("AMC", "AMC"),
            ("AMR", "AMR"),
            ("ST", "ST")
        ]
        html = ['<div class="controls" style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;align-items:center;">']
        for code, label in positions:
            html.append(f'<button class="position-filter" onclick="filterByPositionBtn(this, \'{code}\')">{label}</button>')
        html.append('<button class="position-filter" style="background:#aaa;color:#fff;" onclick="clearFilters(this)">Clear</button>')
        html.append('</div>')
        return ''.join(html)
    
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
        legend_html = f'<div id="legend" class="legend" style="margin-bottom:6px; display:none;">'
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
        
        /* Table sorting indicators */
        th.sort-asc::after { content: ' ▲'; color: #3498db; }
        th.sort-desc::after { content: ' ▼'; color: #3498db; }
        th:hover { background-color: #f8f9fa; }
        
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
        js = """
        // Position filter logic for FM report
        function filterByPositionBtn(btn, position) {
            try {
                document.querySelectorAll('.position-filter').forEach(b => b.classList.remove('active'));
                if (btn && btn.classList) btn.classList.add('active');
                const table = document.getElementById('playerTable');
                if (!table) { console.error('No #playerTable found'); return; }
                // Find the position column index dynamically
                const headers = Array.from(table.querySelectorAll('thead th'));
                let posIdx = headers.findIndex(th => th.textContent.trim().toLowerCase() === 'pos' || th.textContent.trim().toLowerCase() === 'position');
                if (posIdx === -1) posIdx = 3; // fallback to 4th column
                const rows = document.querySelectorAll('#playerTable tbody tr');
                rows.forEach(row => {
                    const positionCell = row.cells[posIdx];
                    if (!positionCell) return;
                    let posText = (positionCell.textContent || positionCell.innerText || '').toUpperCase().trim();
                    let positions = [];
                    posText.split(',').forEach(part => {
                        part = part.trim();
                        let matchCompound = part.match(/^([A-Z/]+)\s*(\((.*?)\))?/);
                        if (matchCompound) {
                            let bases = matchCompound[1].split('/').map(b => b.trim()).filter(Boolean);
                            let sides = matchCompound[3] ? matchCompound[3].split(/[, ]+/).map(s => s.trim()).filter(Boolean) : [];
                            bases.forEach(base => {
                                positions.push({base, sides});
                            });
                        } else {
                            let m = part.match(/^([A-Z]+)\s*(\((.*?)\))?/);
                            if (m) {
                                let base = m[1];
                                let sides = m[3] ? m[3].split(/[, ]+/).map(s => s.trim()).filter(Boolean) : [];
                                positions.push({base, sides});
                            }
                        }
                    });
                    let match = false;
                    function sideMatch(sides, targets) {
                        return sides.some(side => targets.some(t => side.includes(t)));
                    }
                    switch (position) {
                        case 'GK':
                            match = positions.some(p => p.base === 'GK');
                            break;
                        case 'DL':
                            match = positions.some(p => (p.base === 'D' || p.base === 'WB') && sideMatch(p.sides, ['L']));
                            break;
                        case 'DC':
                            match = positions.some(p => p.base === 'D' && sideMatch(p.sides, ['C', 'RC', 'LC', 'RLC']));
                            break;
                        case 'DR':
                            match = positions.some(p => (p.base === 'D' || p.base === 'WB') && sideMatch(p.sides, ['R']));
                            break;
                        case 'DM':
                            match = positions.some(p => p.base === 'DM');
                            break;
                        case 'ML':
                            match = positions.some(p => p.base === 'M' && sideMatch(p.sides, ['L']));
                            break;
                        case 'MC':
                            match = positions.some(p => p.base === 'M' && sideMatch(p.sides, ['C', 'RC', 'LC', 'RLC']));
                            break;
                        case 'MR':
                            match = positions.some(p => p.base === 'M' && sideMatch(p.sides, ['R']));
                            break;
                        case 'AML':
                            match = positions.some(p => p.base === 'AM' && sideMatch(p.sides, ['L']));
                            break;
                        case 'AMC':
                            match = positions.some(p => p.base === 'AM' && sideMatch(p.sides, ['C', 'RC', 'LC', 'RLC']));
                            break;
                        case 'AMR':
                            match = positions.some(p => p.base === 'AM' && sideMatch(p.sides, ['R']));
                            break;
                        case 'ST':
                            match = positions.some(p => p.base === 'ST');
                            break;
                        default:
                            match = false;
                    }
                    row.style.display = match ? '' : 'none';
                });
            } catch (err) {
                console.error('Position filter error:', err);
            }
            
            // Hide all legend roles first
            document.querySelectorAll('.legend-row.clickable').forEach(row => {
                row.dataset.active = '0';
                row.classList.add('inactive');
                setColumnVisibilityByCode(row.dataset.code, false);
            });
            
            // Enable corresponding legend group based on position
            const legendMapping = {
                'GK': 'Goalkeeper',
                'DL': 'Defender (Left/Right)',
                'DC': 'Defender (Central)',
                'DR': 'Defender (Left/Right)',
                'DM': 'Defensive Midfielder',
                'ML': 'Midfielder (Left/Right)',
                'MC': 'Midfield (Central)',
                'MR': 'Midfielder (Left/Right)',
                'AML': 'Attacking Midfielder (Left/Right)',
                'AMC': 'Attacking Midfielder (Central)',
                'AMR': 'Attacking Midfielder (Left/Right)',
                'ST': 'Striker'
            };
            
            const legendGroup = legendMapping[position];
            if (legendGroup) {
                enableRoleGroup(legendGroup);
            }
            
            // Re-apply current sort after filtering
            setTimeout(() => reapplyCurrentSort(), 100);
        }

        function clearFilters(btn) {
            document.querySelectorAll('.position-filter').forEach(b => b.classList.remove('active'));
            const rows = document.querySelectorAll('#playerTable tbody tr');
            rows.forEach(row => row.style.display = '');
            
            // Re-enable all legend roles when clearing filters
            enableAllRoles();
            
            // Re-apply current sort after clearing filters
            setTimeout(() => reapplyCurrentSort(), 100);
        }

        // Color code score cells after page loads
        document.addEventListener('DOMContentLoaded', function() {
            try {
                const table = document.getElementById('playerTable');
                if (!table) { console.error('No #playerTable found for coloring'); return; }
                const cells = table.querySelectorAll('td');
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
                
                // Initialize legend - disable all roles at page load
                disableAllRoles();
                
                // Add sorting functionality to table headers
                initializeTableSorting();
                
            } catch (e) {
                console.error('Coloring error:', e);
            }
        });

        // Table sorting functionality
        function initializeTableSorting() {
            const table = document.getElementById('playerTable');
            if (!table) return;
            
            const headers = table.querySelectorAll('thead th');
            headers.forEach((header, index) => {
                header.style.cursor = 'pointer';
                header.style.userSelect = 'none';
                header.addEventListener('click', () => sortTableByColumn(table, index));
            });
            
            // Auto-sort by Best Score column initially
            const bestScoreIndex = Array.from(headers).findIndex(th => 
                th.textContent.trim().toUpperCase() === 'BEST SCORE'
            );
            if (bestScoreIndex >= 0) {
                sortTableByColumn(table, bestScoreIndex, true); // true = descending
            }
        }
        
        function sortTableByColumn(table, columnIndex, descending = undefined) {
            const tbody = table.querySelector('tbody');
            if (!tbody) return;
            
            const headers = table.querySelectorAll('thead th');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const currentHeader = headers[columnIndex];
            
            // Determine sort direction BEFORE clearing classes
            if (descending === undefined) {
                // Toggle: if currently desc, make asc; if currently asc or no sort, make desc
                descending = !currentHeader.classList.contains('sort-desc');
            }
            
            // Clear previous sort indicators
            headers.forEach(th => {
                th.classList.remove('sort-asc', 'sort-desc');
            });
            
            // Add sort indicator
            currentHeader.classList.add(descending ? 'sort-desc' : 'sort-asc');
            
            // Sort rows
            rows.sort((a, b) => {
                const aCell = a.cells[columnIndex];
                const bCell = b.cells[columnIndex];
                
                if (!aCell || !bCell) return 0;
                
                const aText = aCell.textContent.trim();
                const bText = bCell.textContent.trim();
                
                // Try numeric comparison first
                const aNum = parseNumberLike(aText);
                const bNum = parseNumberLike(bText);
                
                let comparison;
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    comparison = aNum - bNum;
                } else {
                    comparison = aText.localeCompare(bText);
                }
                
                return descending ? -comparison : comparison;
            });
            
            // Re-append sorted rows
            rows.forEach(row => tbody.appendChild(row));
        }
        
        function parseNumberLike(text) {
            if (text == null) return NaN;
            let t = String(text).trim().toUpperCase();
            if (!t) return NaN;
            
            // Remove currency, commas and percent
            t = t.replace(/[£$,%\\s]/g, '');
            
            // Handle ranges like "12-14" by taking the average
            if (/^-?\\\\d+(?:\\\\.\\\\d+)?\\\\s*[-–]\\\\s*-?\\\\d+(?:\\\\.\\\\d+)?$/.test(t)) {
                const parts = t.split(/[-–]/).map(s => parseFloat(s));
                if (!isNaN(parts[0]) && !isNaN(parts[1])) return (parts[0] + parts[1]) / 2;
            }
            
            // Handle suffixes K/M/B
            const m = t.match(/^(-?\\\\d+(?:\\\\.\\\\d+)?)([KMB])?$/);
            if (m) {
                let n = parseFloat(m[1]);
                const suf = m[2];
                if (suf === 'K') n *= 1e3;
                else if (suf === 'M') n *= 1e6;
                else if (suf === 'B') n *= 1e9;
                return n;
            }
            
            return parseFloat(t);
        }
        
        function reapplyCurrentSort() {
            const table = document.getElementById('playerTable');
            if (!table) return;
            
            const headers = Array.from(table.querySelectorAll('thead th'));
            const sortedHeader = headers.find(th => 
                th.classList.contains('sort-asc') || th.classList.contains('sort-desc')
            );
            
            if (sortedHeader) {
                const columnIndex = headers.indexOf(sortedHeader);
                const isDescending = sortedHeader.classList.contains('sort-desc');
                sortTableByColumn(table, columnIndex, isDescending);
            }
        }

        // Legend toggle functionality
        function toggleLegendExternal(button) {
            const legend = document.getElementById('legend');
            if (legend) {
                const isHidden = legend.style.display === 'none';
                legend.style.display = isHidden ? 'block' : 'none';
                
                // Update button text
                if (button) {
                    button.textContent = isHidden ? 'Hide legend' : 'Show legend';
                }
            }
        }

        // Best formations functionality
        function toggleBestFormations() {
            const panel = document.getElementById('bestFormationsPanel');
            if (panel) {
                const isHidden = panel.style.display === 'none' || !panel.style.display;
                panel.style.display = isHidden ? 'block' : 'none';
            } else {
                console.error('bestFormationsPanel not found');
            }
        }

        // Legend role management functions
        function legendToggleRole(element) {
            const code = element.dataset.code;
            const isActive = element.dataset.active === '1';
            
            if (isActive) {
                element.dataset.active = '0';
                element.classList.add('inactive');
                setColumnVisibilityByCode(code, false);
            } else {
                element.dataset.active = '1';
                element.classList.remove('inactive');
                setColumnVisibilityByCode(code, true);
            }
        }

        function enableAllRoles() {
            document.querySelectorAll('.legend-row.clickable').forEach(row => {
                row.dataset.active = '1';
                row.classList.remove('inactive');
                setColumnVisibilityByCode(row.dataset.code, true);
            });
        }

        function disableAllRoles() {
            document.querySelectorAll('.legend-row.clickable').forEach(row => {
                row.dataset.active = '0';
                row.classList.add('inactive');
                setColumnVisibilityByCode(row.dataset.code, false);
            });
        }

        function enableRoleGroup(groupName) {
            const group = Array.from(document.querySelectorAll('.legend-group')).find(g => 
                g.querySelector('strong').textContent === groupName
            );
            if (group) {
                group.querySelectorAll('.legend-row.clickable').forEach(row => {
                    row.dataset.active = '1';
                    row.classList.remove('inactive');
                    setColumnVisibilityByCode(row.dataset.code, true);
                });
            }
        }

        function disableRoleGroup(groupName) {
            const group = Array.from(document.querySelectorAll('.legend-group')).find(g => 
                g.querySelector('strong').textContent === groupName
            );
            if (group) {
                group.querySelectorAll('.legend-row.clickable').forEach(row => {
                    row.dataset.active = '0';
                    row.classList.add('inactive');
                    setColumnVisibilityByCode(row.dataset.code, false);
                });
            }
        }

        function setColumnVisibilityByCode(code, visible) {
            const table = document.getElementById('playerTable');
            if (!table) return;

            // Find column index by code
            const headers = Array.from(table.querySelectorAll('thead th'));
            const colIndex = headers.findIndex(th => th.textContent.trim() === code);
            
            if (colIndex >= 0) {
                // Toggle header visibility
                headers[colIndex].style.display = visible ? '' : 'none';
                
                // Toggle body cell visibility
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(row => {
                    if (row.cells[colIndex]) {
                        row.cells[colIndex].style.display = visible ? '' : 'none';
                    }
                });
                
                // Re-apply current sort after column visibility change
                setTimeout(() => reapplyCurrentSort(), 50);
            }
        }

        // Best formations computation
        // Role name mapping from formation specs to table column codes
        const ROLE_NAME_TO_CODE = {
            // Goalkeepers
            'Goalkeeper (D)': 'GKD',
            'Sweeper Keeper (S)': 'SKS',
            'Sweeper Keeper (A)': 'SKA',
            
            // Defenders
            'Full Back (S)': 'FBS',
            'Full Back (D)': 'FBD',
            'Full Back (A)': 'FBA',
            'Wing Back (S)': 'WBS',
            'Wing Back (D)': 'WBD',
            'Wing Back (A)': 'WBA',
            'Central Defender (D)': 'CDD',
            'Central Defender (C)': 'CDC',
            'Central Defender (S)': 'CDS',
            'Central Def (D)': 'CDD',
            'Central Def (C)': 'CDC',
            'Ball-Playing Def (D)': 'BPDD',
            'Ball-Playing Def (S)': 'BPDS',
            'Ball-Playing Def (C)': 'BPDC',
            'Wide Centre-Back (S)': 'WCBS',
            'Wide Centre-Back (D)': 'WCBD',
            'Wide Centre-Back (A)': 'WCBA',
            
            // Defensive Midfielders
            'Def Mid (D)': 'DMD',
            'Def Mid (S)': 'DMS',
            'Deep-Lying Playmaker (S)': 'DLPS',
            'Deep-Lying Playmaker (D)': 'DLPD',
            'Ball-Winning Mid (D)': 'BWMD',
            'Ball-Winning Mid (S)': 'BWMS',
            'Anchor Man (D)': 'AD',
            'Half Back (D)': 'HBD',
            
            // Central Midfielders
            'Box-to-Box Mid (S)': 'B2BS',
            'Central Mid (S)': 'CMS',
            'Central Mid (D)': 'CMD',
            'Central Mid (A)': 'CMA',
            'Advanced Playmaker (S)': 'APS',
            'Advanced Playmaker (A)': 'APA',
            'Mezzala (S)': 'MEZS',
            'Mezzala (A)': 'MEZA',
            'Carrilero (S)': 'CARS',
            'Regista (S)': 'REGS',
            'Roaming Playmaker (S)': 'RPS',
            
            // Wide Midfielders
            'Winger (S)': 'WS',
            'Winger (A)': 'WA',
            'Wide Mid (S)': 'WMS',
            'Wide Mid (D)': 'WMD',
            'Wide Mid (A)': 'WMA',
            'Inside Forward (A)': 'IFA',
            'Inside Forward (S)': 'IFS',
            'Inverted Winger (A)': 'IWA',
            'Inverted Winger (S)': 'IWS',
            'Wide Playmaker (S)': 'WPS',
            'Wide Playmaker (A)': 'WPA',
            
            // Attacking Midfielders
            'Att Mid (S)': 'AMS',
            'Att Mid (A)': 'AMA',
            'Attacking Mid (S)': 'AMS',
            'Attacking Mid (A)': 'AMA',
            'Trequartista (A)': 'TREA',
            'Enganche (S)': 'ENGS',
            'Shadow Striker (A)': 'SSA',
            
            // Forwards
            'Advanced Forward (A)': 'AFA',
            'Target Forward (S)': 'TFS',
            'Target Forward (A)': 'TFA',
            'Deep-Lying Forward (S)': 'DLFS',
            'Deep-Lying Forward (A)': 'DLFA',
            'Complete Forward (S)': 'CFS',
            'Complete Forward (A)': 'CFA',
            'Pressing Forward (A)': 'PFA',
            'Pressing Forward (S)': 'PFS',
            'Pressing Forward (D)': 'PFD',
            'Poacher (A)': 'PA',
            'False Nine (S)': 'F9S'
        };

        function computeTopFormations() {
            const resultsDiv = document.getElementById('bestFormationsResults');
            const specTextarea = document.getElementById('formationSpec');
            const table = document.getElementById('playerTable');
            
            if (!resultsDiv || !specTextarea || !table) {
                console.error('Missing required elements for formation computation');
                return;
            }
            
            resultsDiv.innerHTML = '<p>Computing formations...</p>';
            
            try {
                const specText = specTextarea.textContent || specTextarea.value;
                const formations = parseFormations(specText);
                const players = getVisiblePlayers(table);
                
                if (formations.length === 0 || players.length === 0) {
                    resultsDiv.innerHTML = '<p class="muted">No formations (' + formations.length + ') or players (' + players.length + ') available for analysis.</p>';
                    return;
                }
                
                const results = analyzeFormations(formations, players);
                displayFormationResults(results.slice(0, 3), resultsDiv);
                
            } catch (error) {
                console.error('Error computing formations:', error);
                resultsDiv.innerHTML = '<p class="muted">Error computing formations. Please try again.</p>';
            }
        }
        
        function parseFormations(specText) {
            const formations = [];
            let current = null;
            
            // Split by actual newlines, not literal \\n
            specText.split('\\n').forEach(line => {
                line = line.trim();
                if (!line) return;
                
                const m = line.match(/^(\\\\d+)\\\\. (.+)$/);
                if (m) {
                    if (current) formations.push(current);
                    current = { name: m[2], positions: [] };
                } else if (current) {
                    // More flexible parsing for formation lines - handle both en dash (–) and regular hyphen (-)
                    const pm = line.match(/^([A-Z\\/\\\\s]+)\\\\s*[–\\u2013\\\\-]\\\\s*(.+)$/);
                    if (pm) {
                        let pos = pm[1].trim();
                        let role = pm[2].trim();
                        current.positions.push({ pos, role });
                    }
                }
            });
            
            if (current) formations.push(current);
            
            return formations;
        }
        
        function getVisiblePlayers(table) {
            const players = [];
            const headers = Array.from(table.querySelectorAll('thead th'));
            
            // Look for both "Name" and "Player" columns
            const nameIdx = headers.findIndex(th => {
                const text = th.textContent.trim().toLowerCase();
                return text === 'name' || text === 'player';
            });
            const posIdx = headers.findIndex(th => th.textContent.trim().toLowerCase() === 'pos');
            
            if (nameIdx === -1 || posIdx === -1) {
                return players;
            }
            
            const rows = Array.from(table.querySelectorAll('tbody tr'));
            
            let visibleRows = 0;
            rows.forEach(row => {
                if (row.style.display !== 'none') {
                    visibleRows++;
                    const name = row.cells[nameIdx]?.textContent?.trim() || '';
                    const pos = row.cells[posIdx]?.textContent?.trim() || '';
                    
                    const scores = {};

                    
                    headers.forEach((header, idx) => {
                        const headerText = header.textContent.trim();
                        // Skip non-role columns (name, position, age, club, etc.)
                        const skipColumns = ['player', 'name', 'pos', 'age', 'club', 'best score', 'best role'];
                        if (!skipColumns.includes(headerText.toLowerCase()) && 
                            headerText.length <= 4 && 
                            headerText.length >= 1) {
                            const cellText = row.cells[idx]?.textContent?.trim() || '';
                            const score = parseFloat(cellText);
                            if (!isNaN(score)) {
                                scores[headerText] = score;

                            }
                        }
                    });
                    
                    players.push({ name, pos, scores });
                }
            });
            
            return players;
        }
        
        function analyzeFormations(formations, players) {
            const results = [];
            
            formations.forEach(formation => {

                
                // Use proper assignment algorithm to avoid duplicates
                const assignment = assignPlayersToFormation(formation, players);
                
                let totalScore = 0;
                let validPositions = 0;
                const assignments = [];
                
                assignment.forEach(assign => {
                    if (assign.player) {
                        totalScore += assign.score;
                        validPositions++;
                        assignments.push({
                            position: assign.position,
                            role: assign.role,
                            player: assign.player.name,
                            score: assign.score
                        });
                    } else {
                        // Count unfilled positions as 0 in the total score
                        totalScore += 0;
                    }
                });
                
                // Calculate average using ALL positions (filled + unfilled)
                const totalPositions = formation.positions.length;
                const avgScore = totalPositions > 0 ? totalScore / totalPositions : 0;
                
                results.push({
                    formation: formation.name,
                    avgScore: avgScore,
                    totalScore: totalScore,
                    validPositions: validPositions,
                    totalPositions: formation.positions.length,
                    assignments: assignments
                });
            });
            
            return results.sort((a, b) => b.avgScore - a.avgScore);
        }
        
        function assignPlayersToFormation(formation, players) {
            const assignments = [];
            const usedPlayers = new Set();
            
            // Sort positions by specificity (harder to fill positions first)
            const sortedPositions = [...formation.positions].sort((a, b) => {
                const aCount = getEligiblePlayersCount(players, a.pos);
                const bCount = getEligiblePlayersCount(players, b.pos);
                return aCount - bCount; // Fewer eligible players = higher priority
            });
            
            sortedPositions.forEach(formPos => {
                // Find best available player for this position
                let bestPlayer = null;
                let bestScore = -1;
                
                players.forEach(player => {
                    if (!usedPlayers.has(player.name) && isPlayerEligibleForPosition(player, formPos.pos)) {
                        const roleScore = player.scores[formPos.role];
                        const defaultScore = calculateDefaultScore(player, formPos.role);
                        const finalScore = roleScore || defaultScore;
                        
                        if (finalScore > bestScore) {
                            bestScore = finalScore;
                            bestPlayer = player;
                        }
                    }
                });
                
                if (bestPlayer) {
                    usedPlayers.add(bestPlayer.name);
                    assignments.push({
                        position: formPos.pos,
                        role: formPos.role,
                        player: bestPlayer,
                        score: bestScore
                    });
                } else {
                    assignments.push({
                        position: formPos.pos,
                        role: formPos.role,
                        player: null,
                        score: 0
                    });
                }
            });
            
            return assignments;
        }
        
        function getEligiblePlayersCount(players, position) {
            return players.filter(p => isPlayerEligibleForPosition(p, position)).length;
        }
        
        function findBestPlayerForPosition(players, formationPos, role) {
            let bestPlayer = null;
            let bestScore = -1;
            
            players.forEach(player => {
                const eligible = isPlayerEligibleForPosition(player, formationPos);
                if (eligible) {
                    let score = getPlayerRoleScore(player, role);
                    

                    
                    if (score > bestScore) {
                        bestScore = score;
                        bestPlayer = player;
                    }
                } else {
                    // Player not eligible
                }
            });
            
            return bestPlayer ? { player: bestPlayer, score: bestScore } : null;
        }
        
        function isPlayerEligibleForPosition(player, formationPos) {
            const playerPositions = player.pos.split(',').map(p => p.trim());
            const targetPos = formationPos.toUpperCase().trim();
            
            const isEligible = playerPositions.some(pos => {
                // First check if the position has sides in parentheses at the end
                const fullPosMatch = pos.match(/^(.+?)\\\\s*\\\\(([LRC]+)\\\\)$/);
                if (fullPosMatch) {
                    // Position like "D/WB (R)" or "M/AM (C)"
                    const rolesPart = fullPosMatch[1].trim(); // "D/WB" or "M/AM"
                    const sides = fullPosMatch[2]; // "R" or "C"
                    
                    // Split roles by "/" and check each one
                    const roles = rolesPart.split('/').map(r => r.trim());
                    
                    return roles.some(role => {
                        return checkRoleMatch(role, sides, targetPos);
                    });
                } else {
                    // Position without explicit sides like "DM", "GK"
                    return checkRoleMatch(pos, '', targetPos);
                }
            });
            
            return isEligible;
        }
        
        function checkRoleMatch(playerRole, playerSides, targetPos) {
            if (targetPos.includes('/')) {
                // Multi-role formation position like "D/WB L"
                const targetParts = targetPos.split('/');
                return targetParts.some(part => {
                    const partMatch = part.trim().match(/^([A-Z]+)\\\\s*([LRC])?$/);
                    if (partMatch) {
                        const targetRole = partMatch[1];
                        const targetSide = partMatch[2];
                        return checkSingleRoleMatch(playerRole, playerSides, targetRole, targetSide);
                    }
                    return false;
                });
            } else {
                // Single formation position like "MC", "DC", "D L", "GK", "ST C"
                const targetMatch = targetPos.match(/^([A-Z]+)\\\\s*([LRC])?$/);
                if (targetMatch) {
                    const targetRole = targetMatch[1];
                    const targetSide = targetMatch[2];
                    return checkSingleRoleMatch(playerRole, playerSides, targetRole, targetSide);
                }
            }
            return false;
        }
        
        function checkSingleRoleMatch(playerRole, playerSides, targetRole, targetSide) {
            // Handle compound positions like DC, MC vs D, M
            let roleMatches = false;
            
            if (targetRole === 'DC' && playerRole === 'D') {
                // DC (Central Defender) matches D players who can play center
                roleMatches = !playerSides || playerSides.includes('C') || playerSides.includes('RC') || playerSides.includes('LC');
            } else if (targetRole === 'MC' && playerRole === 'M') {
                // MC (Central Midfielder) matches M players who can play center  
                roleMatches = !playerSides || playerSides.includes('C') || playerSides.includes('RC') || playerSides.includes('LC');
            } else if (targetRole === 'AMC' && playerRole === 'AM') {
                // AMC (Central Attacking Mid) matches AM players who can play center
                roleMatches = !playerSides || playerSides.includes('C') || playerSides.includes('RC') || playerSides.includes('LC');
            } else {
                // Direct role match
                roleMatches = playerRole === targetRole;
            }
            
            // Check side compatibility
            let sideMatches = true;
            if (targetSide && playerSides) {
                sideMatches = playerSides.includes(targetSide);
            }
            
            return roleMatches && sideMatches;
        }
        
        function getPlayerRoleScore(player, formationRole) {
            // Try exact match first (in case formation role is already a code)
            if (player.scores[formationRole] !== undefined) {

                return player.scores[formationRole];
            }
            
            // Try mapped code
            const code = ROLE_NAME_TO_CODE[formationRole];
            if (code && player.scores[code] !== undefined) {

                return player.scores[code];
            }
            
            // No direct match found, use position-relevant scoring

            return calculatePositionRelevantScore(player, formationRole);
        }
        
        function calculatePositionRelevantScore(player, formationRole) {
            // Group roles by position type for more relevant averaging
            const positionGroups = {
                'goalkeeper': ['GKD', 'SKS', 'SKA', 'SKD'],
                'defender': ['FBD', 'FBS', 'FBA', 'WBD', 'WBS', 'WBA', 'CDD', 'CDC', 'CDS', 'BPDD', 'BPDS', 'BPDC', 'WCBD', 'WCBS', 'WCBA', 'LD', 'LS'],
                'defensiveMid': ['DMD', 'DMS', 'DLPD', 'DLPS', 'BWMD', 'BWMS', 'AD', 'HBD', 'REGS'],
                'centralMid': ['CMS', 'CMD', 'CMA', 'B2BS', 'APS', 'APA', 'MEZS', 'MEZA', 'CARS', 'RPS'],
                'wideMid': ['WS', 'WA', 'WMS', 'WMD', 'WMA', 'IFA', 'IFS', 'IWA', 'IWS', 'WPS', 'WPA'],
                'attackingMid': ['AMS', 'AMA', 'TREA', 'ENGS', 'SSA'],
                'forward': ['AFA', 'TFS', 'TFA', 'DLFS', 'DLFA', 'CFS', 'CFA', 'PFA', 'PFS', 'PFD', 'PA', 'F9S']
            };
            
            // Determine which group this role belongs to
            const code = ROLE_NAME_TO_CODE[formationRole];
            let relevantGroup = null;
            
            for (const [groupName, roles] of Object.entries(positionGroups)) {
                if (code && roles.includes(code)) {
                    relevantGroup = roles;
                    break;
                }
            }
            
            if (relevantGroup) {
                // Average only scores from the same position group
                const relevantScores = relevantGroup
                    .map(role => player.scores[role])
                    .filter(score => score !== undefined);
                
                if (relevantScores.length > 0) {
                    const average = relevantScores.reduce((a, b) => a + b, 0) / relevantScores.length;

                    return average;
                }
            }
            
            // Fallback to overall average
            const allScores = Object.values(player.scores);
            const average = allScores.length > 0 ? allScores.reduce((a, b) => a + b, 0) / allScores.length : 0;

            return average;
        }
        
        function calculateDefaultScore(player, role) {
            const scores = Object.values(player.scores);
            const average = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;

            return average;
        }
        
        function displayFormationResults(results, container) {
            if (results.length === 0) {
                container.innerHTML = '<p class="muted">No suitable formations found.</p>';
                return;
            }
            
            let html = '<table><thead><tr><th>Rank</th><th>Formation</th><th>Avg Score</th><th>Details</th></tr></thead><tbody>';
            
            results.forEach((result, idx) => {
                html += '<tr>' +
                    '<td>' + (idx + 1) + '</td>' +
                    '<td><strong>' + result.formation + '</strong></td>' +
                    '<td>' + result.avgScore.toFixed(1) + '</td>' +
                    '<td>' + result.validPositions + '/' + (result.totalPositions || result.assignments.length) + ' positions filled</td>' +
                '</tr>';
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;
        }

        // Make functions globally available
        window.filterByPositionBtn = filterByPositionBtn;
        window.clearFilters = clearFilters;
        window.toggleLegendExternal = toggleLegendExternal;
        window.toggleBestFormations = toggleBestFormations;
        window.legendToggleRole = legendToggleRole;
        window.enableAllRoles = enableAllRoles;
        window.disableAllRoles = disableAllRoles;
        window.enableRoleGroup = enableRoleGroup;
        window.disableRoleGroup = disableRoleGroup;
        window.setColumnVisibilityByCode = setColumnVisibilityByCode;
        window.computeTopFormations = computeTopFormations;
        window.sortTableByColumn = sortTableByColumn;
        window.reapplyCurrentSort = reapplyCurrentSort;
        """
        return js
    
    def _generate_formation_analyzer(self) -> str:
        # Generate formation analysis textarea content from external file.
        try:
            # Try to load formations from external file
            import os
            formations_file = os.path.join(os.path.dirname(__file__), 'formations.txt')
            
            if os.path.exists(formations_file):
                with open(formations_file, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # Fallback to built-in formations if file doesn't exist
                logger.warning("formations.txt not found, using built-in formations")
                return self._get_fallback_formations()
                
        except Exception as e:
            logger.error(f"Error loading formations file: {e}, using fallback")
            return self._get_fallback_formations()
    
    def _get_fallback_formations(self) -> str:
        # Fallback formations if external file is not available
        return """1. 4-4-2
GK = GKD
D (L) = FBS
D (C) = CDD
D (C) = CDD
D (R) = FBS
M (R) = WS
M (C) = B2BS
M (C) = BWMD
M (L) = WA
ST (C) = AFA
ST (C) = DLFS

2. 4-2-3-1 Wide
GK = SKS
D/WB (R) = WBS
D (C) = BPDD
D (C) = CDD
D/WB (L) = WBS
DM = DLPS
DM = DMD
AM (R) = IFA
AM (C) = AMS
AM (L) = WA
ST (C) = PFA

3. 4-3-3 DM Wide
GK = SKS
D/WB (R) = WBS
D (C) = CDD
D (C) = CDD
D/WB (L) = WBS
DM = AD
M (C) = B2BS
M (C) = APS
AM (R) = IFA
AM (L) = WA
ST (C) = AFA"""
        
    def _generate_full_html(self, table_html: str, legend_html: str) -> str:
    # Generate the complete HTML document.
        
        css_styles = self._generate_css_styles()
        javascript = self._generate_javascript()
        formation_content = self._generate_formation_analyzer()
        
        # Properly escape the formation content for HTML textarea
        formation_content_escaped = formation_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')
        
        role_titles_json = json.dumps(FULL_ROLE_DESCRIPTIONS)
        position_role_groups_json = json.dumps(POSITION_ROLE_GROUPS)
        html_template = (
            f'<!DOCTYPE html>'
            f'<html>'
            f'<head>'
            f'<title>FM Player Analysis</title>'
            f'<meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            f'<style>{css_styles}</style>'
            f'</head>'
            f'<body>'
            f'<div class="header">'
            f'<h1>Football Manager Player Analysis</h1>'
            f'<p>Comprehensive role suitability analysis for your squad</p>'
            f'</div>'
            f'<div class="controls" style="margin-bottom:16px;">'
            f'<button id="externalLegendToggle" class="legend-toggle" style="margin-left:12px;" onclick="toggleLegendExternal(this)">Show legend</button>'
            f'<button class="legend-toggle" style="margin-left:8px;" onclick="toggleBestFormations()">Best formations</button>'
            f'</div>'
            f'{legend_html}'
            f'<div id="bestFormationsPanel" style="display:none;">'
            f'<div class="row">'
            f'<span class="muted">Top 3 matches based on Pos eligibility and Best Score (0–20):</span>'
            f'<button onclick="computeTopFormations()">Compute top 3</button>'
            f'</div>'
            f'<div id="bestFormationsResults"></div>'
            f'<textarea id="formationSpec" style="display:none;">{formation_content_escaped}</textarea>'
            f'</div>'
            f'<div class="table-container">{table_html}</div>'
            f'<script>'
            f'const ROLE_TITLES = {role_titles_json};'
            f'const POSITION_ROLE_GROUPS = {position_role_groups_json};'
            f'{javascript}'
            f'</script>'
            f'</body>'
            f'</html>'
        )
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