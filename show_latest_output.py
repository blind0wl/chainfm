import glob, os, pandas as pd

files = [p for p in glob.glob('*.html') if os.path.basename(p).lower() != 'test.html']
if not files:
    print('No HTML outputs found')
    raise SystemExit(1)
latest = max(files, key=os.path.getctime)
print('Latest HTML:', latest)
# read table
try:
    df = pd.read_html(latest, header=0, keep_default_na=False)[0]
except Exception as e:
    print('Failed to read latest HTML:', e)
    raise
print('\nColumns:', df.columns.tolist())
cols = ['Name','Spd','Work','gkd','wba']
available = [c for c in cols if c in df.columns]
print('\nSample values:')
print(df[available].head())
