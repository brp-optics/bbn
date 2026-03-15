import pandas as pd
import sys


# Enter the names of SSA-style name files to load when python is called. 
if len(sys.argv) < 2:
   print("""Please enter names of SSA-style name files to load. 
Ex.: python "AL.txt" "AK.txt" ...""")
   sys.exit(1)

files=sys.argv[1:]


dfs = []
for file in files:
    dfs.append(pd.read_csv(file, names=("State", "Sex", "Year", "Name", "Count")))

df = pd.concat(dfs, ignore_index=True)

df = (df.groupby(["Sex", "Year", "Name"], as_index=False)["Count"].sum())

df_2024 = df[df["Year"] == 2024]
df_2024m = df_2024[df_2024["Sex"] == "M"]
df_2024f = df_2024[df_2024["Sex"] == "F"]

rank_2024m = (df_2024m.groupby("Name", as_index=False)["Count"]
    .sum()
    .sort_values("Count", ascending=False)
    .rename(columns={"Count": "Count2024"})
)
rank_2024f = (df_2024f.groupby("Name", as_index=False)["Count"]
    .sum()
    .sort_values("Count", ascending=False)
    .rename(columns={"Count": "Count2024"})
)

rank_2024m["Rank2024"] = range(1, len(rank_2024m) + 1)
rank_2024f["Rank2024"] = range(1, len(rank_2024f) + 1)

df_m = df[df["Sex"]=="M"].merge(rank_2024m[["Name", "Count2024", "Rank2024"]], on="Name", how="left")
df_f = df[df["Sex"]=="F"].merge(rank_2024f[["Name", "Count2024", "Rank2024"]], on="Name", how="left")

df_m = df_m.drop_duplicates(["Name", "Sex"])
df_f = df_f.drop_duplicates(["Name", "Sex"])

df_m = df_m.sort_values(["Rank2024", "Name"], na_position="last")
df_f = df_f.sort_values(["Rank2024", "Name"], na_position="last")

df_m = df_m[["Name","Count2024"]]
df_f = df_f[["Name","Count2024"]]


df_m.to_csv("M.csv", index=False)
df_f.to_csv("F.csv", index=False)