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
    'SVS': 'Segundo Volante Support',
    'SVA': 'Segundo Volante Attack',
    'SSA': 'Shadow Striker Attack',
    'WMD': 'Wide Midfielder Defend',
    'WMS': 'Wide Midfielder Support',
    'WMA': 'Wide Midfielder Attack',
    'WPS': 'Wide Playmaker Support',
    'WPA': 'Wide Playmaker Attack',
    'WTFS': 'Wide Target Forward Support',
    'WTFA': 'Wide Target Forward Attack',
    'WS': 'Winger Support',
    'WA': 'Winger Attack',
    'PA': 'Poacher Attack',
    'PFD': 'Pressing Forward Defend',
    'PFS': 'Pressing Forward Support',
    'PFA': 'Pressing Forward Attack',
    'TFS': 'Target Forward Support',
    'TFA': 'Target Forward Attack',
    'TREA': 'Trequartista Attack',
    'FB': 'Full Back Composite',
    'CB': 'Centre Back Composite',
}


def get_role_definitions() -> Dict[str, RoleDefinition]:
    """Get all role definitions with their calculation parameters."""
    
    roles = {}

    # Roles imported from roles_summary.csv
    roles['afa'] = RoleDefinition('afa', 'AFA', ['Acc', 'Fin', 'Pac'], ['Cmp', 'Dri', 'Fir', 'OtB', 'Tec'], ['Agi', 'Ant', 'Bal', 'Dec', 'Pas', 'Sta', 'Wor'])
    roles['apa'] = RoleDefinition('apa', 'APA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cmp', 'Dec', 'Fir', 'OtB', 'Pas', 'Tea', 'Tec', 'Vis'], ['Agi', 'Ant', 'Dri', 'Fla'])
    roles['aps'] = RoleDefinition('aps', 'APS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cmp', 'Dec', 'Fir', 'OtB', 'Pas', 'Tea', 'Tec', 'Vis'], ['Agi', 'Ant', 'Dri', 'Fla'])
    roles['ad'] = RoleDefinition('ad', 'AD', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Cnt', 'Dec', 'Mar', 'Pos', 'Tck'], ['Cmp', 'Str', 'Tea'])
    roles['ama'] = RoleDefinition('ama', 'AMA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Dec', 'Dri', 'Fir', 'Fla', 'Lon', 'OtB', 'Pas', 'Tec'], ['Agi', 'Cmp', 'Fin', 'Vis'])
    roles['ams'] = RoleDefinition('ams', 'AMS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Dec', 'Fir', 'Fla', 'Lon', 'OtB', 'Pas', 'Tec'], ['Agi', 'Cmp', 'Dri', 'Vis'])
    roles['bpdc'] = RoleDefinition('bpdc', 'BPDC', ['Acc', 'Cmp', 'Jum', 'Pac'], ['Ant', 'Cnt', 'Dec', 'Mar', 'Pas', 'Pos', 'Tck'], ['Bra', 'Fir', 'Hea', 'Str', 'Tec', 'Vis'])
    roles['bpdd'] = RoleDefinition('bpdd', 'BPDD', ['Acc', 'Cmp', 'Jum', 'Pac'], ['Hea', 'Mar', 'Pas', 'Pos', 'Str', 'Tck'], ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec', 'Fir', 'Tec', 'Vis'])
    roles['bpds'] = RoleDefinition('bpds', 'BPDS', ['Acc', 'Cmp', 'Jum', 'Pac'], ['Agg', 'Bra', 'Dec', 'Hea', 'Pas', 'Pos', 'Str', 'Tck'], ['Ant', 'Cnt', 'Fir', 'Mar', 'Tec', 'Vis'])
    roles['bwmd'] = RoleDefinition('bwmd', 'BWMD', ['Acc', 'Pac', 'Sta', 'Wor'], ['Agg', 'Ant', 'Tck', 'Tea'], ['Agi', 'Bra', 'Cnt', 'Mar', 'Pos', 'Str'])
    roles['bwms'] = RoleDefinition('bwms', 'BWMS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Agg', 'Ant', 'Tck', 'Tea'], ['Agi', 'Bra', 'Cnt', 'Mar', 'Pas', 'Str'])
    roles['b2bs'] = RoleDefinition('b2bs', 'B2BS', ['Acc', 'Pac', 'Sta', 'Wor'], ['OtB', 'Pas', 'Tck', 'Tea'], ['Agg', 'Ant', 'Bal', 'Cmp', 'Dec', 'Dri', 'Fin', 'Fir', 'Lon', 'Pos', 'Str', 'Tec'])
    roles['cars'] = RoleDefinition('cars', 'CARS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Dec', 'Fir', 'Pas', 'Pos', 'Tck', 'Tea'], ['Ant', 'Cnt', 'Cmp', 'OtB', 'Tec', 'Vis'])
    roles['cdc'] = RoleDefinition('cdc', 'CDC', ['Acc', 'Cmp', 'Jum', 'Pac'], ['Ant', 'Cnt', 'Dec', 'Mar', 'Pos', 'Tck'], ['Bra', 'Hea', 'Str'])
    roles['cdd'] = RoleDefinition('cdd', 'CDD', ['Acc', 'Cmp', 'Jum', 'Pac'], ['Hea', 'Mar', 'Pos', 'Str', 'Tck'], ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec'])
    roles['cds'] = RoleDefinition('cds', 'CDS', ['Acc', 'Cmp', 'Jum', 'Pac'], ['Agg', 'Bra', 'Dec', 'Hea', 'Pos', 'Str', 'Tck'], ['Ant', 'Cnt', 'Mar'])
    roles['cma'] = RoleDefinition('cma', 'CMA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Dec', 'Fir', 'OtB', 'Pas'], ['Ant', 'Cmp', 'Lon', 'Tck', 'Tea', 'Tec', 'Vis'])
    roles['cmd'] = RoleDefinition('cmd', 'CMD', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cnt', 'Dec', 'Pos', 'Tck', 'Tea'], ['Agg', 'Ant', 'Cmp', 'Fir', 'Mar', 'Pas', 'Tec'])
    roles['cms'] = RoleDefinition('cms', 'CMS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Dec', 'Fir', 'Pas', 'Tck', 'Tea'], ['Ant', 'Cnt', 'Cmp', 'OtB', 'Tec', 'Vis'])
    roles['cfa'] = RoleDefinition('cfa', 'CFA', ['Acc', 'Fin', 'Pac'], ['Agi', 'Ant', 'Cmp', 'Dri', 'Fir', 'Hea', 'OtB', 'Str', 'Tec'], ['Bal', 'Dec', 'Jum', 'Lon', 'Pas', 'Sta', 'Tea', 'Vis', 'Wor'])
    roles['cfs'] = RoleDefinition('cfs', 'CFS', ['Acc', 'Fin', 'Pac'], ['Agi', 'Ant', 'Cmp', 'Dec', 'Dri', 'Fir', 'Hea', 'Lon', 'OtB', 'Pas', 'Str', 'Tec', 'Vis'], ['Bal', 'Jum', 'Sta', 'Tea', 'Wor'])
    roles['cwba'] = RoleDefinition('cwba', 'CWBA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'Fla', 'OtB', 'Tea', 'Tec'], ['Agi', 'Ant', 'Bal', 'Dec', 'Fir', 'Mar', 'Pas', 'Pos', 'Tck'])
    roles['cwbs'] = RoleDefinition('cwbs', 'CWBS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'OtB', 'Tea', 'Tec'], ['Agi', 'Ant', 'Bal', 'Dec', 'Fir', 'Fla', 'Mar', 'Pas', 'Pos', 'Tck'])
    roles['dlfa'] = RoleDefinition('dlfa', 'DLFA', ['Acc', 'Fin', 'Pac'], ['Cmp', 'Dec', 'Fir', 'OtB', 'Pas', 'Tea', 'Tec'], ['Ant', 'Bal', 'Dri', 'Fla', 'Str', 'Vis'])
    roles['dlfs'] = RoleDefinition('dlfs', 'DLFS', ['Acc', 'Fin', 'Pac'], ['Cmp', 'Dec', 'Fir', 'OtB', 'Pas', 'Tea', 'Tec'], ['Ant', 'Bal', 'Fla', 'Str', 'Vis'])
    roles['dlpd'] = RoleDefinition('dlpd', 'DLPD', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cmp', 'Dec', 'Fir', 'Pas', 'Tea', 'Tec', 'Vis'], ['Ant', 'Bal', 'Pos', 'Tck'])
    roles['dlps'] = RoleDefinition('dlps', 'DLPS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cmp', 'Dec', 'Fir', 'Pas', 'Tea', 'Tec', 'Vis'], ['Ant', 'Bal', 'OtB', 'Pos'])
    roles['dmd'] = RoleDefinition('dmd', 'DMD', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Cnt', 'Pos', 'Tck', 'Tea'], ['Agg', 'Cmp', 'Dec', 'Mar', 'Pas'])
    roles['dms'] = RoleDefinition('dms', 'DMS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Cnt', 'Pos', 'Tck', 'Tea'], ['Agg', 'Cmp', 'Dec', 'Fir', 'Mar', 'Pas', 'Str'])
    roles['dwd'] = RoleDefinition('dwd', 'DWD', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'OtB', 'Pos', 'Tea', 'Tec'], ['Agg', 'Cnt', 'Cro', 'Dec', 'Dri', 'Fir', 'Mar', 'Tck'])
    roles['dws'] = RoleDefinition('dws', 'DWS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'OtB', 'Tea', 'Tec'], ['Agg', 'Ant', 'Cnt', 'Cmp', 'Dec', 'Dri', 'Fir', 'Mar', 'Pas', 'Pos', 'Tck'])
    roles['engs'] = RoleDefinition('engs', 'ENGS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cmp', 'Dec', 'Fir', 'Pas', 'Tec', 'Vis'], ['Agi', 'Ant', 'Dri', 'Fla', 'OtB', 'Tea'])
    roles['f9s'] = RoleDefinition('f9s', 'F9S', ['Acc', 'Fin', 'Pac'], ['Agi', 'Cmp', 'Dec', 'Dri', 'Fir', 'OtB', 'Pas', 'Tec', 'Vis'], ['Ant', 'Bal', 'Fla', 'Tea'])
    roles['fba'] = RoleDefinition('fba', 'FBA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Cro', 'Mar', 'Pos', 'Tck', 'Tea'], ['Agi', 'Cnt', 'Dec', 'Dri', 'Fir', 'OtB', 'Pas', 'Tec'])
    roles['fbd'] = RoleDefinition('fbd', 'FBD', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Cnt', 'Mar', 'Pos', 'Tck'], ['Cro', 'Dec', 'Pas', 'Tea'])
    roles['fbs'] = RoleDefinition('fbs', 'FBS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Cnt', 'Mar', 'Pos', 'Tck', 'Tea'], ['Cro', 'Dec', 'Dri', 'Pas', 'Tec'])
    roles['gkd'] = RoleDefinition('gkd', 'GKD', ['Agi', 'Ref'], ['Aer', 'Cmd', 'Cnt', 'Han', 'Kic', 'Pos'], ['1v1', 'Ant', 'Dec', 'Thr'])
    roles['hbd'] = RoleDefinition('hbd', 'HBD', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Cnt', 'Cmp', 'Dec', 'Mar', 'Pos', 'Tck', 'Tea'], ['Agg', 'Bra', 'Fir', 'Jum', 'Pas', 'Str'])
    roles['ifa'] = RoleDefinition('ifa', 'IFA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Agi', 'Ant', 'Dri', 'Fin', 'Fir', 'OtB', 'Tec'], ['Bal', 'Cmp', 'Fla', 'Lon', 'Pas'])
    roles['ifs'] = RoleDefinition('ifs', 'IFS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Agi', 'Dri', 'Fin', 'Fir', 'OtB', 'Tec'], ['Ant', 'Bal', 'Cmp', 'Fla', 'Lon', 'Pas', 'Vis'])
    roles['ifbd'] = RoleDefinition('ifbd', 'IFBD', ['Acc', 'Pac', 'Sta', 'Wor'], ['Hea', 'Mar', 'Pos', 'Str', 'Tck'], ['Agg', 'Agi', 'Ant', 'Bra', 'Cnt', 'Cmp', 'Dec', 'Dri', 'Fir', 'Jum', 'Pas', 'Tec'])
    roles['iwa'] = RoleDefinition('iwa', 'IWA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Agi', 'Cro', 'Dri', 'Pas', 'Tec'], ['Ant', 'Bal', 'Cmp', 'Dec', 'Fir', 'Fla', 'Lon', 'OtB', 'Vis'])
    roles['iws'] = RoleDefinition('iws', 'IWS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Agi', 'Cro', 'Dri', 'Pas', 'Tec'], ['Bal', 'Cmp', 'Dec', 'Fir', 'Lon', 'OtB', 'Vis'])
    roles['iwba'] = RoleDefinition('iwba', 'IWBA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cmp', 'Dec', 'Fir', 'OtB', 'Pas', 'Tck', 'Tea', 'Tec', 'Vis'], ['Agi', 'Ant', 'Cnt', 'Cro', 'Dri', 'Fla', 'Lon', 'Mar', 'Pos'])
    roles['iwbd'] = RoleDefinition('iwbd', 'IWBD', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Dec', 'Pas', 'Pos', 'Tck', 'Tea'], ['Agi', 'Cnt', 'Cmp', 'Fir', 'Mar', 'OtB', 'Tec'])
    roles['iwbs'] = RoleDefinition('iwbs', 'IWBS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cmp', 'Dec', 'Fir', 'Pas', 'Tck', 'Tea'], ['Agi', 'Ant', 'Cnt', 'Mar', 'OtB', 'Pos', 'Tec', 'Vis'])
    roles['ld'] = RoleDefinition('ld', 'LD', ['Acc', 'Cmp', 'Jum', 'Pac'], ['Dec', 'Fir', 'Hea', 'Mar', 'Pas', 'Pos', 'Str', 'Tck', 'Tea', 'Tec'], ['Ant', 'Bra', 'Cnt', 'Sta'])
    roles['ls'] = RoleDefinition('ls', 'LS', ['Acc', 'Cmp', 'Jum', 'Pac'], ['Dec', 'Fir', 'Hea', 'Mar', 'Pas', 'Pos', 'Str', 'Tck', 'Tea', 'Tec'], ['Ant', 'Bra', 'Cnt', 'Dri', 'Sta', 'Vis'])
    roles['meza'] = RoleDefinition('meza', 'MEZA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Dec', 'Dri', 'OtB', 'Pas', 'Tec', 'Vis'], ['Ant', 'Bal', 'Cmp', 'Fin', 'Fir', 'Fla', 'Lon'])
    roles['mezs'] = RoleDefinition('mezs', 'MEZS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Dec', 'OtB', 'Pas', 'Tec'], ['Ant', 'Bal', 'Cmp', 'Dri', 'Fir', 'Lon', 'Tck', 'Vis'])
    roles['ncbc'] = RoleDefinition('ncbc', 'NCBC', ['Acc', 'Cmp', 'Jum', 'Pac'], ['Ant', 'Cnt', 'Mar', 'Pos', 'Tck'], ['Bra', 'Hea', 'Str'])
    roles['ncbd'] = RoleDefinition('ncbd', 'NCBD', ['Acc', 'Cmp', 'Jum', 'Pac'], ['Hea', 'Mar', 'Pos', 'Str', 'Tck'], ['Agg', 'Ant', 'Bra', 'Cnt'])
    roles['ncbs'] = RoleDefinition('ncbs', 'NCBS', ['Acc', 'Cmp', 'Jum', 'Pac'], ['Agg', 'Bra', 'Hea', 'Pos', 'Str', 'Tck'], ['Ant', 'Cnt', 'Mar'])
    roles['nfbd'] = RoleDefinition('nfbd', 'NFBD', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Mar', 'Pos', 'Str', 'Tck'], ['Agg', 'Bra', 'Cnt', 'Hea', 'Tea'])
    roles['pa'] = RoleDefinition('pa', 'PA', ['Acc', 'Fin', 'Pac'], ['Ant', 'Cmp', 'OtB'], ['Dec', 'Fir', 'Hea', 'Tec'])
    roles['pfa'] = RoleDefinition('pfa', 'PFA', ['Acc', 'Fin', 'Pac'], ['Agg', 'Ant', 'Bra', 'OtB', 'Sta', 'Tea', 'Wor'], ['Agi', 'Bal', 'Cnt', 'Cmp', 'Dec', 'Fir', 'Str'])
    roles['pfd'] = RoleDefinition('pfd', 'PFD', ['Acc', 'Fin', 'Pac'], ['Agg', 'Ant', 'Bra', 'Dec', 'Sta', 'Tea', 'Wor'], ['Agi', 'Bal', 'Cnt', 'Cmp', 'Fir', 'Str'])
    roles['pfs'] = RoleDefinition('pfs', 'PFS', ['Acc', 'Fin', 'Pac'], ['Agg', 'Ant', 'Bra', 'Dec', 'Sta', 'Tea', 'Wor'], ['Agi', 'Bal', 'Cnt', 'Cmp', 'Fir', 'OtB', 'Pas', 'Str'])
    roles['raua'] = RoleDefinition('raua', 'RAUA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Bal', 'Cnt', 'Cmp', 'Dec', 'Fin', 'OtB'], ['Fir', 'Tec'])
    roles['regs'] = RoleDefinition('regs', 'REGS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cmp', 'Dec', 'Fir', 'Fla', 'OtB', 'Pas', 'Tea', 'Tec', 'Vis'], ['Ant', 'Bal', 'Dri', 'Lon'])
    roles['rps'] = RoleDefinition('rps', 'RPS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Cmp', 'Dec', 'Fir', 'OtB', 'Pas', 'Tea', 'Tec', 'Vis'], ['Agi', 'Bal', 'Cnt', 'Dri', 'Lon', 'Pos'])
    roles['sva'] = RoleDefinition('sva', 'SVA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Fin', 'Lon', 'OtB', 'Pas', 'Pos', 'Tck'], ['Bal', 'Cnt', 'Cmp', 'Dec', 'Fir', 'Mar'])
    roles['svs'] = RoleDefinition('svs', 'SVS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Mar', 'OtB', 'Pas', 'Pos', 'Tck'], ['Ant', 'Bal', 'Cnt', 'Cmp', 'Dec', 'Fin', 'Fir', 'Lon', 'Str'])
    roles['ssa'] = RoleDefinition('ssa', 'SSA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Cmp', 'Dri', 'Fin', 'Fir', 'OtB'], ['Agi', 'Bal', 'Cnt', 'Dec', 'Pas', 'Tec'])
    roles['ska'] = RoleDefinition('ska', 'SKA', ['Agi', 'Ref'], ['1v1', 'Ant', 'Cmd', 'Cnt', 'Kic', 'Pos'], ['Acc', 'Aer', 'Dec', 'Fir', 'Han', 'Pas', 'TRO', 'Vis'])
    roles['skd'] = RoleDefinition('skd', 'SKD', ['Agi', 'Ref'], ['1v1', 'Ant', 'Cmd', 'Cnt', 'Kic', 'Pos'], ['Acc', 'Aer', 'Dec', 'Fir', 'Han', 'Pas', 'TRO', 'Vis'])
    roles['sks'] = RoleDefinition('sks', 'SKS', ['Agi', 'Ref'], ['1v1', 'Ant', 'Cmd', 'Cnt', 'Kic', 'Pos'], ['Acc', 'Aer', 'Dec', 'Fir', 'Han', 'Pas', 'TRO', 'Vis'])
    roles['tfa'] = RoleDefinition('tfa', 'TFA', ['Acc', 'Fin', 'Pac'], ['Bal', 'Bra', 'Cmp', 'Hea', 'Jum', 'OtB', 'Str'], ['Agg', 'Ant', 'Dec', 'Fir', 'Tea'])
    roles['tfs'] = RoleDefinition('tfs', 'TFS', ['Acc', 'Fin', 'Pac'], ['Bal', 'Bra', 'Hea', 'Jum', 'Str', 'Tea'], ['Agg', 'Ant', 'Cmp', 'Dec', 'Fir', 'OtB'])
    roles['trea'] = RoleDefinition('trea', 'TREA', ['Acc', 'Fin', 'Pac'], ['Cmp', 'Dec', 'Dri', 'Fir', 'Fla', 'OtB', 'Pas', 'Tec', 'Vis'], ['Agi', 'Ant', 'Bal'])
    roles['wcba'] = RoleDefinition('wcba', 'WCBA', ['Acc', 'Cmp', 'Jum', 'Pac'], ['Cro', 'Dri', 'Hea', 'Mar', 'OtB', 'Sta', 'Str', 'Tck'], ['Agg', 'Agi', 'Ant', 'Bra', 'Cnt', 'Dec', 'Fir', 'Pas', 'Pos', 'Tec', 'Wor'])
    roles['wcbd'] = RoleDefinition('wcbd', 'WCBD', ['Acc', 'Cmp', 'Jum', 'Pac'], ['Hea', 'Mar', 'Pos', 'Str', 'Tck'], ['Agg', 'Agi', 'Ant', 'Bra', 'Cnt', 'Dec', 'Dri', 'Fir', 'Pas', 'Tec', 'Wor'])
    roles['wcbs'] = RoleDefinition('wcbs', 'WCBS', ['Acc', 'Cmp', 'Jum', 'Pac'], ['Dri', 'Hea', 'Mar', 'Pos', 'Str', 'Tck'], ['Agg', 'Agi', 'Ant', 'Bra', 'Cnt', 'Cro', 'Dec', 'Fir', 'OtB', 'Pas', 'Sta', 'Tec', 'Wor'])
    roles['wma'] = RoleDefinition('wma', 'WMA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dec', 'Fir', 'Pas', 'Tea'], ['Ant', 'Cmp', 'OtB', 'Tck', 'Tec', 'Vis'])
    roles['wmd'] = RoleDefinition('wmd', 'WMD', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cnt', 'Dec', 'Pas', 'Pos', 'Tck', 'Tea'], ['Ant', 'Cmp', 'Cro', 'Fir', 'Mar', 'Tec'])
    roles['wms'] = RoleDefinition('wms', 'WMS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Dec', 'Pas', 'Tck', 'Tea'], ['Ant', 'Cnt', 'Cmp', 'Cro', 'Fir', 'OtB', 'Pos', 'Tec', 'Vis'])
    roles['wpa'] = RoleDefinition('wpa', 'WPA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cmp', 'Dec', 'Dri', 'Fir', 'OtB', 'Pas', 'Tea', 'Tec', 'Vis'], ['Agi', 'Ant', 'Fla'])
    roles['wps'] = RoleDefinition('wps', 'WPS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cmp', 'Dec', 'Fir', 'Pas', 'Tea', 'Tec', 'Vis'], ['Agi', 'Dri', 'OtB'])
    roles['wtfa'] = RoleDefinition('wtfa', 'WTFA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Bra', 'Hea', 'Jum', 'OtB', 'Str'], ['Ant', 'Bal', 'Cro', 'Fin', 'Fir', 'Tea'])
    roles['wtfs'] = RoleDefinition('wtfs', 'WTFS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Bra', 'Hea', 'Jum', 'Str', 'Tea'], ['Ant', 'Bal', 'Cro', 'Fir', 'OtB'])
    roles['wa'] = RoleDefinition('wa', 'WA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Agi', 'Cro', 'Dri', 'Tec'], ['Ant', 'Bal', 'Fir', 'Fla', 'OtB', 'Pas'])
    roles['ws'] = RoleDefinition('ws', 'WS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Agi', 'Cro', 'Dri', 'Tec'], ['Bal', 'Fir', 'OtB', 'Pas'])
    roles['wba'] = RoleDefinition('wba', 'WBA', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'OtB', 'Tck', 'Tea', 'Tec'], ['Agi', 'Ant', 'Bal', 'Cnt', 'Dec', 'Fir', 'Fla', 'Mar', 'Pas', 'Pos'])
    roles['wbd'] = RoleDefinition('wbd', 'WBD', ['Acc', 'Pac', 'Sta', 'Wor'], ['Ant', 'Mar', 'Pos', 'Tck', 'Tea'], ['Agi', 'Bal', 'Cnt', 'Cro', 'Dec', 'Dri', 'Fir', 'OtB', 'Pas', 'Tec'])
    roles['wbs'] = RoleDefinition('wbs', 'WBS', ['Acc', 'Pac', 'Sta', 'Wor'], ['Cro', 'Dri', 'Mar', 'OtB', 'Tck', 'Tea'], ['Agi', 'Ant', 'Bal', 'Cnt', 'Dec', 'Fir', 'Pas', 'Pos', 'Tec'])

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


# def get_composite_scores() -> Dict[str, Dict[str, List[str]]]:
#     """Get composite score definitions (combinations of basic attributes)."""
#     return {
#         'fb': {
#             'key_attrs': ['Acc', 'Pac', 'Sta', 'Wor'],
#             'green_attrs': ['Mar', 'Tck', 'Ant', 'Cnt', 'Pos'],
#             'blue_attrs': ['Cro', 'Pas', 'Dec', 'Tea']
#         },
#         'cb': {
#             'key_attrs': ['Acc', 'Pac', 'Jum', 'Cmp'],
#             'green_attrs': ['Hea', 'Mar', 'Tck', 'Pos', 'Str'],
#             'blue_attrs': ['Agg', 'Ant', 'Bra', 'Cnt', 'Dec']
#         }
#     }


logger.info("Role definitions module loaded with all FM tactical roles")