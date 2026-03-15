import pandas as pd
import sys
import numpy as np


# Enter the names of SSA-style name files to load when python is called. 
if len(sys.argv) < 2:
   print("""Please enter names of SSA-style name files to load. 
Ex.: python "AL.txt" "AK.txt" ...""")
   sys.exit(1)

files=sys.argv[1:]


# Concatenate files
dfs = []
for file in files:
    dfs.append(pd.read_csv(file, names=("State", "Sex", "Year", "Name", "Count")))

df = pd.concat(dfs, ignore_index=True)


# Sum counts across states by year + name for 2024 rank
df = (df.groupby(["Sex", "Year", "Name"], as_index=False)["Count"].sum())
df_2024 = df[df["Year"] == 2024]

# Compute 2024 rank per sex
def rank_2024(df_2024_sex):
    rank = (df_2024_sex.groupby("Name", as_index=False)["Count"]
            .sum()
            .sort_values("Count", ascending=False)
            .rename(columns={"Count":"Count2024"}))
    rank["Rank2024"] = range(1, len(rank)+1)
    return rank

rank_2024m = rank_2024(df_2024[df_2024["Sex"]=="M"])
rank_2024f = rank_2024(df_2024[df_2024["Sex"]=="F"])


# Sum total counts across all years
df_total = df.groupby(["Sex","Name"], as_index=False)["Count"].sum()


# Merge 2024 rank with total counts

df_m = df_total[df_total["Sex"]=="M"].merge(
    rank_2024m[["Name","Count2024","Rank2024"]],
    on="Name", how="left"
)

df_f = df_total[df_total["Sex"]=="F"].merge(
    rank_2024f[["Name","Count2024","Rank2024"]],
    on="Name", how="left"
)


# Capitalize names for merging with dataset3
df_m["Name"] = df_m["Name"].str.capitalize()
df_f["Name"] = df_f["Name"].str.capitalize()


# I would like to have side-by-side origin information. Load datset3 from Anwarvic.

df_origins = pd.read_csv("dataset3.csv")

# Clean and select useful columns
df_origins = df_origins[["name","gender","meaning","origin","pronounciation"]].copy()

# Capitalize names to match SSA
df_origins["Name_clean"] = df_origins["name"].str.capitalize()

# Uppercase gender to match SSA ("M"/"F")
df_origins["Sex"] = df_origins["gender"].str.upper()

# Clean origin field
df_origins["Origin_clean"] = df_origins["origin"].str.strip("[]")


# Merge origins df with ssa df
def merge_origins(ssa_df):
    merged = ssa_df.merge(
        df_origins[["Name_clean","Sex","meaning","Origin_clean","pronounciation"]],
        left_on=["Name","Sex"], right_on=["Name_clean","Sex"], how="left"
    )
    # Fill missing values
    for col in ["meaning","Origin_clean","pronounciation"]:
        merged[col] = merged[col].fillna("Unknown")
    return merged

df_m = merge_origins(df_m)
df_f = merge_origins(df_f)


# Sort by 2024 rank, then total Count
for df_sex in [df_m, df_f]:
    df_sex["Rank2024_sort"] = df_sex["Rank2024"].fillna(np.inf)

df_m = df_m.sort_values(by=["Rank2024_sort","Count"], ascending=[True,False])
df_f = df_f.sort_values(by=["Rank2024_sort","Count"], ascending=[True,False])

final_cols = ["Name","Count2024","Count","meaning","Origin_clean","pronounciation"]
df_m = df_m[final_cols]
df_f = df_f[final_cols]

# Export to tsv
df_m.to_csv("M_with_origins.tsv", sep="\t", index=False)
df_f.to_csv("F_with_origins.tsv", sep="\t", index=False)

print("Export complete: M_with_origins.tsv, F_with_origins.tsv")

