import pandas as pd

tables = pd.read_html('test.html', header=0, keep_default_na=False)
df = tables[0]
print('COLUMNS:', df.columns.tolist())
print('\nDTYPES:\n', df.dtypes)

cols_to_check = ['Pac','Acc','Wor','Sta','Agi','Ref','Kic','Pos','Fin','Cmp']
for c in cols_to_check:
    if c in df.columns:
        vals = df[c].head(10).tolist()
        coerced = pd.to_numeric(df[c], errors='coerce').head(10).tolist()
        print(f"\nCOL: {c}")
        print('  raw:', vals)
        print('  coerced:', coerced)
    else:
        print(f"\nCOL: {c} not present")

print('\nSAMPLE ROW (first):')
print(df.iloc[0].to_dict())
