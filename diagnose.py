from chainfm import *
import pandas as pd

def diagnose_calculations():
    print("=== DIAGNOSTIC: Role Calculation Analysis ===")
    
    df = pd.read_html('test.html')[0]
    
    # Pick a midfielder who should have some reasonable scores
    midfielders = df[df['Position'].str.contains('M', na=False)]
    if midfielders.empty:
        print("No midfielders found, using any outfield player")
        outfield = df[df['Position'] != 'GK']
        if not outfield.empty:
            player = outfield.iloc[0]
        else:
            print("Only goalkeepers in data!")
            return
    else:
        player = midfielders.iloc[0]
    
    print(f"\nAnalyzing: {player['Name']} ({player['Position']})")
    print(f"Key attributes:")
    print(f"  Pac: {player['Pac']}, Acc: {player['Acc']}, Sta: {player['Sta']}, Wor: {player['Wor']}")
    print(f"  Pas: {player['Pas']}, Tck: {player['Tck']}, Dec: {player['Dec']}, Tea: {player['Tea']}")
    
    # Calculate CM Support manually
    cms_key = player['Acc'] + player['Pac'] + player['Sta'] + player['Wor']
    cms_green = player['Fir'] + player['Pas'] + player['Tck'] + player['Dec'] + player['Tea']
    cms_blue = player['Tec'] + player['Ant'] + player['Cmp'] + player['Cnt'] + player['OtB'] + player['Vis']
    cms_score = (((cms_key * 5) + (cms_green * 3) + (cms_blue * 1)) / 41)
    
    print(f"\nManual CM Support calculation:")
    print(f"  Key attributes (x5): {cms_key}")
    print(f"  Green attributes (x3): {cms_green}")
    print(f"  Blue attributes (x1): {cms_blue}")
    print(f"  Final score: {cms_score:.1f}")
    
    # Now compute with our function
    df_single = pd.DataFrame([player])
    df_with_scores = compute_scores(df_single)
    actual_cms = df_with_scores['cms'].iloc[0]
    
    print(f"  Our function result: {actual_cms:.1f}")
    print(f"  Match: {'✅' if abs(cms_score - actual_cms) < 0.1 else '❌'}")

if __name__ == "__main__":
    diagnose_calculations()