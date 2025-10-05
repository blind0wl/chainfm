from chainfm import *
import pandas as pd

df = pd.read_html('test.html')[0]
df_with_scores = compute_scores(df)

# Check Tyler Williams (defender)
tyler = df_with_scores[df_with_scores['Name'] == 'Tyler Williams']
print("Tyler Williams (Defender) scores:")
print(f"bpdd: {tyler['bpdd'].iloc[0]:.1f}")
print(f"cms: {tyler['cms'].iloc[0]:.1f}")  
print(f"afa: {tyler['afa'].iloc[0]:.1f}")
print(f"His best role: {tyler['Resulting Role'].iloc[0]} ({tyler['Highest Role Score'].iloc[0]:.1f})")

# Check a midfielder if available
midfielders = df_with_scores[df_with_scores['Position'].str.contains('M', na=False)]
if not midfielders.empty:
    mid = midfielders.iloc[0]
    print(f"\n{mid['Name']} (Midfielder) scores:")
    print(f"cms: {mid['cms']:.1f}")
    print(f"apa: {mid['apa']:.1f}")
    print(f"His best role: {mid['Resulting Role']} ({mid['Highest Role Score']:.1f})")