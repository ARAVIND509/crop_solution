import pandas as pd

# Load your current dataset
df = pd.read_csv("data/clean_final_dataset.csv")

# Take only first 70000 rows
df = df.head(70000)

# Save new dataset
df.to_csv("data/final_70000_dataset.csv", index=False)

print("✅ Trimmed to 70,000 rows successfully")