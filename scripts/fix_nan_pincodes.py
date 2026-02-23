import pandas as pd

INPUT_FILE = "5c2f62fe-5afa-4119-a499-fec9d604d5bd.csv"
OUTPUT_FILE = "indian_pincodes_ready.csv"

df = pd.read_csv(INPUT_FILE)

# Convert NaN to None (so DB stores NULL)
df = df.where(pd.notnull(df), None)

df.to_csv(OUTPUT_FILE, index=False)

print("✅ File ready for Supabase upload: indian_pincodes_ready.csv")
