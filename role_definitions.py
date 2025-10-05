"""
Role definitions and calculations for Football Manager data analysis.

This module contains all role calculations, mappings, and the logic
for computing player suitability scores for different tactical roles.
"""

from typing import Dict, List, Tuple, Callable
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class RoleDefinition:
    """Represents a single Football Manager role with its calculation logic."""
    
    def __init__(self, name: str, display_name: str, key_attrs: List[str], 
                 green_attrs: List[str], blue_attrs: List[str]):
        self.name = name
        self.display_name = display_name
        self.key_attrs = key_attrs
        self.green_attrs = green_attrs
        self.blue_attrs = blue_attrs
        self.total_weight = len(key_attrs) * 5 + len(green_attrs) * 3 + len(blue_attrs) * 1
    
    def calculate_score(self, player_data: pd.Series, get_attr_func: Callable) -> float:
        """Calculate the role score for a player."""
        key_sum = sum(get_attr_func(attr).iloc[0] if hasattr(get_attr_func(attr), 'iloc') else get_attr_func(attr) for attr in self.key_attrs)
        green_sum = sum(get_attr_func(attr).iloc[0] if hasattr(get_attr_func(attr), 'iloc') else get_attr_func(attr) for attr in self.green_attrs)
        blue_sum = sum(get_attr_func(attr).iloc[0] if hasattr(get_attr_func(attr), 'iloc') else get_attr_func(attr) for attr in self.blue_attrs)
        
        score = ((key_sum * 5) + (green_sum * 3) + (blue_sum * 1)) / self.total_weight
        return round(float(score), 1)


# Role display name mappings for better readability
ROLE_DISPLAY_NAMES = {
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
    'cb': 'CB'
}


# Full role descriptions for legends and tooltips
FULL_ROLE_DESCRIPTIONS = {
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


def get_role_definitions() -> Dict[str, RoleDefinition]:
    """Get all role definitions with their calculation parameters."""
    
    roles = {}
    
    # Goalkeeper roles
    roles['gkd'] = RoleDefinition('gkd', 'GKD', 
        ['Agi', 'Ref'], 
        ['Aer', 'Cmd', 'Han', 'Kic', 'Cnt', 'Pos'], 
        ['1v1', 'Thr', 'Ant', 'Dec'])
    
    roles['skd'] = RoleDefinition('skd', 'SKD',
        ['Agi', 'Ref'],
        ['Cmd', 'Kic', '1v1', 'Ant', 'Cnt', 'Pos'],
        ['Aer', 'Fir', 'Han', 'Pas', 'TRO', 'Dec', 'Vis', 'Acc'])
    
    roles['sks'] = RoleDefinition('sks', 'SKS',
        ['Agi', 'Ref'],
        ['Cmd', 'Kic', '1v1', 'Ant', 'Cnt', 'Pos'],
        ['Aer', 'Fir', 'Han', 'Pas', 'TRO', 'Dec', 'Vis', 'Acc'])
    
    roles['ska'] = RoleDefinition('ska', 'SKA',
        ['Agi', 'Ref'],
        ['Cmd', 'Kic', '1v1', 'Ant', 'Cnt', 'Pos'],
        ['Aer', 'Fir', 'Han', 'Pas', 'TRO', 'Dec', 'Vis', 'Acc'])
    
    # Defender roles - Ball Playing Defenders
    roles['bpdd'] = RoleDefinition('bpdd', 'BPDD',
        ['Acc', 'Pac', 'Jum', 'Cmp'],
        ['Hea', 'Mar', 'Pas', 'Tck', 'Pos', 'Str'],
        ['Fir', 'Tec', 'Agg', 'Ant', 'Bra', 'Cnt', 'Dec', 'Vis'])
    
    roles['bpds'] = RoleDefinition('bpds', 'BPDS',
        ['Acc', 'Pac', 'Jum', 'Cmp'],
        ['Hea', 'Pas', 'Tck', 'Pos', 'Str', 'Agg', 'Bra', 'Dec'],
        ['Fir', 'Tec', 'Ant', 'Cnt', 'Vis', 'Mar'])
    
    roles['bpdc'] = RoleDefinition('bpdc', 'BPDC',
        ['Acc', 'Pac', 'Jum', 'Cmp'],
        ['Mar', 'Pas', 'Tck', 'Pos', 'Ant', 'Cnt', 'Dec'],
        ['Fir', 'Tec', 'Bra', 'Vis', 'Str', 'Hea'])
    
    # Central Defenders
    roles['cdd'] = RoleDefinition('cdd', 'CDD',
        ['Acc', 'Pac', 'Jum', 'Cmp'],
        ['Hea', 'Mar', 'Tck', 'Pos', 'Str'],
        ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'])
    
    roles['cds'] = RoleDefinition('cds', 'CDS',
        ['Acc', 'Pac', 'Jum', 'Cmp'],
        ['Hea', 'Tck', 'Agg', 'Bra', 'Dec', 'Pos', 'Str'],
        ['Mar', 'Ant', 'Cnt'])
    
    roles['cdc'] = RoleDefinition('cdc', 'CDC',
        ['Acc', 'Pac', 'Jum', 'Cmp'],
        ['Mar', 'Tck', 'Ant', 'Cnt', 'Dec', 'Pos'],
        ['Hea', 'Bra', 'Str'])
    
    # Fullback roles
    roles['fbd'] = RoleDefinition('fbd', 'FBD',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Mar', 'Tck', 'Ant', 'Cnt', 'Pos'],
        ['Cro', 'Pas', 'Dec', 'Tea'])
    
    roles['fbs'] = RoleDefinition('fbs', 'FBS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Mar', 'Tck', 'Ant', 'Cnt', 'Pos'],
        ['Cro', 'Pas', 'Dec', 'Tea'])
    
    roles['fba'] = RoleDefinition('fba', 'FBA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Cro', 'Dri', 'Mar', 'Tck', 'Ant', 'Cnt', 'Pos'],
        ['Fir', 'Pas', 'Dec', 'Tea', 'OtB'])
    
    # Wing Back roles
    roles['wbd'] = RoleDefinition('wbd', 'WBD',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Cro', 'Dri', 'Tck', 'Tec', 'OtB', 'Tea'],
        ['Fir', 'Mar', 'Pas', 'Ant', 'Cnt', 'Dec', 'Fla', 'Pos', 'Agi', 'Bal'])
    
    roles['wbs'] = RoleDefinition('wbs', 'WBS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Cro', 'Dri', 'Tck', 'Tec', 'OtB', 'Tea'],
        ['Fir', 'Mar', 'Pas', 'Ant', 'Cnt', 'Dec', 'Fla', 'Pos', 'Agi', 'Bal'])
    
    roles['wba'] = RoleDefinition('wba', 'WBA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Cro', 'Dri', 'Tck', 'Tec', 'OtB', 'Tea'],
        ['Fir', 'Mar', 'Pas', 'Ant', 'Cnt', 'Dec', 'Fla', 'Pos', 'Agi', 'Bal'])
    
    # Complete Wing Back roles
    roles['cwbs'] = RoleDefinition('cwbs', 'CWBS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Cro', 'Dri', 'Tck', 'Tec', 'OtB'],
        ['Fir', 'Mar', 'Pas', 'Ant', 'Cnt', 'Dec', 'Fla', 'Pos', 'Tea', 'Agi', 'Bal'])
    
    roles['cwba'] = RoleDefinition('cwba', 'CWBA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Cro', 'Dri', 'Tck', 'Tec', 'OtB'],
        ['Fir', 'Mar', 'Pas', 'Ant', 'Cnt', 'Dec', 'Fla', 'Pos', 'Tea', 'Agi', 'Bal'])
    
    # Inverted roles
    roles['ifbd'] = RoleDefinition('ifbd', 'IFBD',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Mar', 'Pas', 'Tck', 'Tec', 'Ant', 'Cnt', 'Dec'],
        ['Fir', 'Cmp', 'OtB', 'Pos', 'Vis'])
    
    roles['iwbd'] = RoleDefinition('iwbd', 'IWBD',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Cro', 'Dri', 'Mar', 'Tck', 'Tec', 'Ant', 'Cnt', 'Dec'],
        ['Fir', 'Pas', 'Cmp', 'OtB', 'Pos', 'Vis'])
    
    roles['iwbs'] = RoleDefinition('iwbs', 'IWBS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Cro', 'Dri', 'Mar', 'Tck', 'Tec', 'Ant', 'Cnt', 'Dec'],
        ['Fir', 'Pas', 'Cmp', 'OtB', 'Pos', 'Vis'])
    
    roles['iwba'] = RoleDefinition('iwba', 'IWBA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Cro', 'Dri', 'Tck', 'Tec', 'OtB'],
        ['Fir', 'Mar', 'Pas', 'Ant', 'Cnt', 'Dec', 'Cmp', 'Pos', 'Vis'])
    
    # Additional defender variants
    roles['ld'] = RoleDefinition('ld', 'LD',
        ['Acc', 'Pac', 'Jum', 'Cmp'],
        ['Hea', 'Mar', 'Tck', 'Pos', 'Str'],
        ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'])
    
    roles['ls'] = RoleDefinition('ls', 'LS',
        ['Acc', 'Pac', 'Jum', 'Cmp'],
        ['Hea', 'Mar', 'Tck', 'Pos', 'Str'],
        ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'])
    
    # No-nonsense defenders
    roles['ncbd'] = RoleDefinition('ncbd', 'NCBD',
        ['Acc', 'Pac', 'Jum', 'Cmp'],
        ['Hea', 'Mar', 'Tck', 'Pos', 'Str'],
        ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'])
    
    roles['ncbs'] = RoleDefinition('ncbs', 'NCBS',
        ['Acc', 'Pac', 'Jum', 'Cmp'],
        ['Hea', 'Mar', 'Tck', 'Pos', 'Str'],
        ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'])
    
    roles['ncbc'] = RoleDefinition('ncbc', 'NCBC',
        ['Acc', 'Pac', 'Jum', 'Cmp'],
        ['Hea', 'Mar', 'Tck', 'Pos', 'Str'],
        ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'])
    
    roles['nfbd'] = RoleDefinition('nfbd', 'NFBD',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Mar', 'Tck', 'Ant', 'Cnt', 'Pos'],
        ['Cro', 'Pas', 'Dec', 'Tea'])
    
    # Wide centre backs
    roles['wcbd'] = RoleDefinition('wcbd', 'WCBD',
        ['Acc', 'Pac', 'Jum', 'Cmp'],
        ['Hea', 'Mar', 'Tck', 'Pos', 'Str'],
        ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'])
    
    roles['wcbs'] = RoleDefinition('wcbs', 'WCBS',
        ['Acc', 'Pac', 'Jum', 'Cmp'],
        ['Hea', 'Mar', 'Tck', 'Pos', 'Str'],
        ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'])
    
    roles['wcba'] = RoleDefinition('wcba', 'WCBA',
        ['Acc', 'Pac', 'Jum', 'Cmp'],
        ['Hea', 'Mar', 'Tck', 'Pos', 'Str'],
        ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'])
    
    # Midfielder roles - Advanced Playmaker
    roles['aps'] = RoleDefinition('aps', 'APS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Tea', 'Vis'],
        ['Dri', 'Ant', 'Fla', 'Agi'])
    
    roles['apa'] = RoleDefinition('apa', 'APA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Tea', 'Vis'],
        ['Dri', 'Ant', 'Fla', 'Agi'])
    
    # Anchor Man
    roles['ad'] = RoleDefinition('ad', 'AD',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Mar', 'Tck', 'Ant', 'Cnt', 'Dec', 'Pos'],
        ['Cmp', 'Tea', 'Str'])
    
    # Attacking Midfielder
    roles['ams'] = RoleDefinition('ams', 'AMS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Fir', 'Lon', 'Pas', 'Tec', 'Ant', 'Dec', 'Fla', 'OtB'],
        ['Dri', 'Cmp', 'Vis', 'Agi'])
    
    roles['ama'] = RoleDefinition('ama', 'AMA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Fir', 'Lon', 'Pas', 'Tec', 'Ant', 'Dec', 'Fla', 'OtB'],
        ['Fin', 'Cmp', 'Vis', 'Agi'])
    
    # Ball Winning Midfielder
    roles['bwmd'] = RoleDefinition('bwmd', 'BWMD',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Tck', 'Agg', 'Ant', 'Tea'],
        ['Mar', 'Bra', 'Cnt', 'Pos', 'Agi', 'Str'])
    
    roles['bwms'] = RoleDefinition('bwms', 'BWMS',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Tck', 'Agg', 'Ant', 'Tea'],
        ['Mar', 'Pas', 'Bra', 'Cnt', 'Agi', 'Str'])
    
    # Box to Box Midfielder
    roles['b2bs'] = RoleDefinition('b2bs', 'B2BS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Pas', 'Tck', 'OtB', 'Tea'],
        ['Dri', 'Fin', 'Fir', 'Lon', 'Tec', 'Agg', 'Ant', 'Cmp', 'Dec', 'Pos', 'Bal', 'Str'])
    
    # Carrilero
    roles['cars'] = RoleDefinition('cars', 'CARS',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Fir', 'Pas', 'Tck', 'Dec', 'Pos', 'Tea'],
        ['Tec', 'Ant', 'Cmp', 'Cnt', 'OtB', 'Vis'])
    
    # Central Midfielder
    roles['cmd'] = RoleDefinition('cmd', 'CMD',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Tck', 'Cnt', 'Dec', 'Pos', 'Tea'],
        ['Fir', 'Mar', 'Pas', 'Tec', 'Agg', 'Ant', 'Cmp'])
    
    roles['cms'] = RoleDefinition('cms', 'CMS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Fir', 'Pas', 'Tck', 'Dec', 'Tea'],
        ['Tec', 'Ant', 'Cmp', 'Cnt', 'OtB', 'Vis'])
    
    roles['cma'] = RoleDefinition('cma', 'CMA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Fir', 'Pas', 'Dec', 'OtB'],
        ['Lon', 'Tck', 'Tec', 'Ant', 'Cmp', 'Tea', 'Vis'])
    
    # Deep Lying Playmaker
    roles['dlpd'] = RoleDefinition('dlpd', 'DLPD',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'Tea', 'Vis'],
        ['Tck', 'Ant', 'Pos', 'Bal'])
    
    roles['dlps'] = RoleDefinition('dlps', 'DLPS',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'Tea', 'Vis'],
        ['Ant', 'OtB', 'Pos', 'Bal'])
    
    # Defensive Midfielder
    roles['dmd'] = RoleDefinition('dmd', 'DMD',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Tck', 'Ant', 'Cnt', 'Pos', 'Tea'],
        ['Mar', 'Pas', 'Agg', 'Cmp', 'Str', 'Dec'])
    
    roles['dms'] = RoleDefinition('dms', 'DMS',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Tck', 'Ant', 'Cnt', 'Pos', 'Tea'],
        ['Fir', 'Mar', 'Pas', 'Agg', 'Cmp', 'Dec', 'Str'])
    
    # Defensive Winger
    roles['dwd'] = RoleDefinition('dwd', 'DWD',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Tck', 'Ant', 'Cnt', 'Pos', 'Tea'],
        ['Mar', 'Pas', 'Agg', 'Cmp', 'Str', 'Dec'])
    
    roles['dws'] = RoleDefinition('dws', 'DWS',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Tck', 'Ant', 'Cnt', 'Pos', 'Tea'],
        ['Fir', 'Mar', 'Pas', 'Agg', 'Cmp', 'Dec', 'Str'])
    
    # Enganche
    roles['engs'] = RoleDefinition('engs', 'ENGS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'Vis'],
        ['Dri', 'Ant', 'Fla', 'OtB', 'Tea', 'Agi'])
    
    # Half Back
    roles['hbd'] = RoleDefinition('hbd', 'HBD',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Tck', 'Agg', 'Ant', 'Tea'],
        ['Mar', 'Bra', 'Cnt', 'Pos', 'Agi', 'Str'])
    
    # Inside Forward
    roles['ifs'] = RoleDefinition('ifs', 'IFS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Fin', 'Fir', 'Tec', 'OtB', 'Agi'],
        ['Lon', 'Pas', 'Ant', 'Cmp', 'Fla', 'Vis', 'Bal'])
    
    roles['ifa'] = RoleDefinition('ifa', 'IFA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Fin', 'Fir', 'Tec', 'Ant', 'OtB', 'Agi'],
        ['Lon', 'Pas', 'Cmp', 'Fla', 'Bal'])
    
    # Inverted Winger
    roles['iws'] = RoleDefinition('iws', 'IWS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Pas', 'Tec', 'Dec', 'OtB'],
        ['Fir', 'Cmp', 'Vis', 'Agi', 'Bal'])
    
    roles['iwa'] = RoleDefinition('iwa', 'IWA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Pas', 'Tec', 'Dec', 'OtB'],
        ['Fin', 'Fir', 'Cmp', 'Vis', 'Agi', 'Bal'])
    
    # Mezzala
    roles['mezs'] = RoleDefinition('mezs', 'MEZS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Pas', 'Tec', 'Dec', 'OtB'],
        ['Dri', 'Fir', 'Lon', 'Tck', 'Ant', 'Cmp', 'Vis', 'Bal'])
    
    roles['meza'] = RoleDefinition('meza', 'MEZA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Pas', 'Tec', 'Dec', 'OtB', 'Vis'],
        ['Fin', 'Fir', 'Lon', 'Ant', 'Cmp', 'Fla', 'Bal'])
    
    # Raumdeuter
    roles['raua'] = RoleDefinition('raua', 'RAUA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Fir', 'Pas', 'Tec', 'Ant', 'Dec', 'OtB'],
        ['Cmp', 'Vis', 'Agi', 'Bal'])
    
    # Regista
    roles['regs'] = RoleDefinition('regs', 'REGS',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'Tea', 'Vis'],
        ['Ant', 'OtB', 'Pos', 'Bal'])
    
    # Roaming Playmaker
    roles['rps'] = RoleDefinition('rps', 'RPS',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'Tea', 'Vis'],
        ['Tck', 'Ant', 'Pos', 'Bal'])
    
    # Segundo Volante
    roles['svs'] = RoleDefinition('svs', 'SVS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Vis'],
        ['Ant', 'Fla', 'Agi', 'Bal'])
    
    roles['sva'] = RoleDefinition('sva', 'SVA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Vis'],
        ['Fin', 'Ant', 'Fla', 'Agi', 'Bal'])
    
    # Shadow Striker
    roles['ssa'] = RoleDefinition('ssa', 'SSA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Vis'],
        ['Fin', 'Ant', 'Fla', 'Agi', 'Bal'])
    
    # Wide Midfielder
    roles['wmd'] = RoleDefinition('wmd', 'WMD',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Tck', 'Ant', 'Cnt', 'Pos', 'Tea'],
        ['Mar', 'Pas', 'Agg', 'Cmp', 'Str', 'Dec'])
    
    roles['wms'] = RoleDefinition('wms', 'WMS',
        ['Wor', 'Sta', 'Acc', 'Pac'],
        ['Tck', 'Ant', 'Cnt', 'Pos', 'Tea'],
        ['Fir', 'Mar', 'Pas', 'Agg', 'Cmp', 'Dec', 'Str'])
    
    roles['wma'] = RoleDefinition('wma', 'WMA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Pas', 'Tec', 'Dec', 'OtB'],
        ['Fin', 'Fir', 'Cmp', 'Vis', 'Agi', 'Bal'])
    
    # Wide Playmaker
    roles['wps'] = RoleDefinition('wps', 'WPS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Vis'],
        ['Fin', 'Fir', 'Lon', 'Ant', 'Fla', 'Bal'])
    
    roles['wpa'] = RoleDefinition('wpa', 'WPA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Vis'],
        ['Fin', 'Fir', 'Lon', 'Ant', 'Fla', 'Bal'])
    
    # Wide Target Forward
    roles['wtfs'] = RoleDefinition('wtfs', 'WTFS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Fin', 'Fir', 'Tec', 'OtB', 'Agi'],
        ['Lon', 'Pas', 'Ant', 'Cmp', 'Fla', 'Vis', 'Bal'])
    
    roles['wtfa'] = RoleDefinition('wtfa', 'WTFA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Dri', 'Fin', 'Fir', 'Tec', 'Ant', 'OtB', 'Agi'],
        ['Lon', 'Pas', 'Cmp', 'Fla', 'Bal'])
    
    # Winger
    roles['ws'] = RoleDefinition('ws', 'WS',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Cro', 'Dri', 'Tck', 'Tec', 'OtB'],
        ['Fir', 'Mar', 'Pas', 'Ant', 'Cnt', 'Dec', 'Fla', 'Pos', 'Tea', 'Agi', 'Bal'])
    
    roles['wa'] = RoleDefinition('wa', 'WA',
        ['Acc', 'Pac', 'Sta', 'Wor'],
        ['Cro', 'Dri', 'Tec', 'OtB'],
        ['Fir', 'Pas', 'Ant', 'Dec', 'Fla', 'Tea', 'Agi', 'Bal'])
    
    # Forward roles - Advanced Forward
    roles['afa'] = RoleDefinition('afa', 'AFA',
        ['Acc', 'Pac', 'Fin'],
        ['Dri', 'Fir', 'Tec', 'Cmp', 'OtB'],
        ['Pas', 'Ant', 'Dec', 'Wor', 'Agi', 'Bal', 'Sta'])
    
    # Complete Forward
    roles['cfs'] = RoleDefinition('cfs', 'CFS',
        ['Acc', 'Pac', 'Fin'],
        ['Dri', 'Fir', 'Hea', 'Lon', 'Pas', 'Tec', 'Ant', 'Cmp', 'Dec', 'OtB', 'Vis', 'Agi', 'Str'],
        ['Tea', 'Wor', 'Bal', 'Jum', 'Sta'])
    
    roles['cfa'] = RoleDefinition('cfa', 'CFA',
        ['Acc', 'Pac', 'Fin'],
        ['Dri', 'Fir', 'Hea', 'Tec', 'Ant', 'Cmp', 'OtB', 'Agi', 'Str'],
        ['Lon', 'Pas', 'Dec', 'Tea', 'Vis', 'Wor', 'Bal', 'Jum', 'Sta'])
    
    # Deep Lying Forward
    roles['dlfs'] = RoleDefinition('dlfs', 'DLFS',
        ['Acc', 'Pac', 'Fin'],
        ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Tea'],
        ['Ant', 'Fla', 'Vis', 'Bal', 'Str'])
    
    roles['dlfa'] = RoleDefinition('dlfa', 'DLFA',
        ['Acc', 'Pac', 'Fin'],
        ['Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Tea'],
        ['Dri', 'Ant', 'Fla', 'Vis', 'Bal', 'Str'])
    
    # False Nine
    roles['f9s'] = RoleDefinition('f9s', 'F9S',
        ['Acc', 'Pac', 'Fin'],
        ['Dri', 'Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'OtB', 'Vis', 'Agi'],
        ['Ant', 'Fla', 'Tea', 'Bal'])
    
    # Poacher
    roles['pa'] = RoleDefinition('pa', 'PA',
        ['Acc', 'Pac', 'Fin'],
        ['Ant', 'Cmp', 'OtB'],
        ['Fir', 'Hea', 'Tec', 'Dec'])
    
    # Pressing Forward
    roles['pfd'] = RoleDefinition('pfd', 'PFD',
        ['Acc', 'Pac', 'Fin'],
        ['Agg', 'Ant', 'Bra', 'OtB', 'Tea', 'Wor', 'Sta'],
        ['Fir', 'Cmp', 'Cnt', 'Dec', 'Agi', 'Bal', 'Str'])
    
    roles['pfs'] = RoleDefinition('pfs', 'PFS',
        ['Acc', 'Pac', 'Fin'],
        ['Agg', 'Ant', 'Bra', 'OtB', 'Tea', 'Wor', 'Sta'],
        ['Fir', 'Cmp', 'Cnt', 'Dec', 'Agi', 'Bal', 'Str'])
    
    roles['pfa'] = RoleDefinition('pfa', 'PFA',
        ['Acc', 'Pac', 'Fin'],
        ['Agg', 'Ant', 'Bra', 'OtB', 'Tea', 'Wor', 'Sta'],
        ['Fir', 'Cmp', 'Cnt', 'Dec', 'Agi', 'Bal', 'Str'])
    
    # Target Forward
    roles['tfs'] = RoleDefinition('tfs', 'TFS',
        ['Acc', 'Pac', 'Fin'],
        ['Hea', 'Bra', 'Cmp', 'OtB', 'Bal', 'Jum', 'Str'],
        ['Fir', 'Agg', 'Ant', 'Dec', 'Tea'])
    
    roles['tfa'] = RoleDefinition('tfa', 'TFA',
        ['Acc', 'Pac', 'Fin'],
        ['Hea', 'Bra', 'Cmp', 'OtB', 'Bal', 'Jum', 'Str'],
        ['Fir', 'Agg', 'Ant', 'Dec', 'Tea'])
    
    # Trequartista
    roles['trea'] = RoleDefinition('trea', 'TREA',
        ['Acc', 'Pac', 'Fin'],
        ['Dri', 'Fir', 'Pas', 'Tec', 'Cmp', 'Dec', 'Fla', 'OtB', 'Vis'],
        ['Ant', 'Agi', 'Bal'])
    
    return roles


def get_expected_role_order() -> List[str]:
    """Get the expected order of roles for display purposes."""
    return [
        # Goalkeepers
        'gkd', 'skd', 'sks', 'ska',
        # Defenders
        'bpdd', 'bpds', 'bpdc', 'cdd', 'cds', 'cdc', 'cwbs', 'cwba',
        'fbd', 'fbs', 'fba', 'ifbd', 'iwbd', 'iwbs', 'iwba',
        'ld', 'ls', 'ncbd', 'ncbs', 'ncbc', 'nfbd', 'wcbd', 'wcbs', 'wcba',
        'wbd', 'wbs', 'wba',
        # Midfielders
        'aps', 'apa', 'ad', 'ams', 'ama', 'bwmd', 'bwms', 'b2bs', 'cars',
        'cmd', 'cms', 'cma', 'dlpd', 'dlps', 'dmd', 'dms', 'dwd', 'dws',
        'engs', 'hbd', 'ifs', 'ifa', 'iws', 'iwa', 'mezs', 'meza', 'raua',
        'regs', 'rps', 'svs', 'sva', 'ssa', 'wmd', 'wms', 'wma', 'wps', 'wpa',
        'wtfs', 'wtfa', 'ws', 'wa',
        # Forwards
        'afa', 'cfs', 'cfa', 'dlfs', 'dlfa', 'f9s', 'pa', 'pfd', 'pfs', 'pfa',
        'tfs', 'tfa', 'trea'
    ]


def get_composite_scores() -> Dict[str, Dict[str, List[str]]]:
    """Get composite score definitions (combinations of basic attributes)."""
    return {
        'fb': {
            'key_attrs': ['Acc', 'Pac', 'Sta', 'Wor'],
            'green_attrs': ['Mar', 'Tck', 'Ant', 'Cnt', 'Pos'],
            'blue_attrs': ['Cro', 'Pas', 'Dec', 'Tea']
        },
        'cb': {
            'key_attrs': ['Acc', 'Pac', 'Jum', 'Cmp'],
            'green_attrs': ['Hea', 'Mar', 'Tck', 'Pos', 'Str'],
            'blue_attrs': ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec']
        }
    }


logger.info("Role definitions module loaded with all FM tactical roles")