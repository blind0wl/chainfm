#!/usr/bin/env python3

import pandas as pd
import sys
sys.dont_write_bytecode = True

def main():
    print("=== Checking available attributes in test.html ===")
    
    # Read the HTML file
    try:
        df = pd.read_html("test.html")[0]
        print(f"DataFrame has {len(df.columns)} columns")
    except Exception as e:
        print(f"Error reading file: {e}")
        return
        
        # Print all column names
        print("\nAll available columns:")
        for i, col in enumerate(df.columns):
            print(f"{i+1:2d}: {col}")
        
        # Check for common FM attributes
        fm_attrs = ['Pac', 'Acc', 'Sta', 'Wor', 'Fin', 'Fir', 'Hea', 'Lon', 'Pas', 'Tck', 'Tec', 
                   'Agg', 'Ant', 'Bra', 'Cmp', 'Cnt', 'Dec', 'Det', 'Fla', 'Ldr', 'OtB', 'Pos', 
                   'Tea', 'Vis', 'Agi', 'Bal', 'Jum', 'Str', 'Dri', 'Mar', 'Cro']
        
        print(f"\nChecking for common FM attributes:")
        present = []
        missing = []
        
        for attr in fm_attrs:
            if attr in df.columns:
                present.append(attr)
            else:
                missing.append(attr)
        
        print(f"\nPresent ({len(present)}): {', '.join(present)}")
        print(f"\nMissing ({len(missing)}): {', '.join(missing)}")
        
        # Sample values for a few key attributes
        print(f"\nSample values for first 3 players:")
        sample_attrs = [attr for attr in ['Pac', 'Acc', 'Fin', 'Pas', 'Tck', 'Dri'] if attr in df.columns]
        if sample_attrs:
            print(df[['Name'] + sample_attrs].head(3).to_string())

if __name__ == "__main__":
    main()