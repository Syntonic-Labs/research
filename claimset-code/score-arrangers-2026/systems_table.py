"""Per-system coding table for the score-arrangers-2026 study: one row per arranging system (dossier), with its link
and, for each code, 1 if pass 1 coded the dossier with it and 0 if not. Reads $CLAIMSET_CODINGS; writes the table
as systems.csv in $CLAIMSET_RUN_DIR and its cells as results to $CLAIMSET_RESULTS."""
import csv, json, os
snap = json.load(open(os.environ["CLAIMSET_CODINGS"], encoding="utf-8"))
codes = [c for c in snap["codes"] if c["id"] != "TM12"] + [c for c in snap["codes"] if c["id"] == "TM12"]
name = {c["id"]: c["term"] for c in snap["codes"]}
has = {}
for row in snap["codings"]:
    if str(row.get("pass", 1)) == "1":
        has.setdefault(row["source"], set()).update(row["codes"])
src = {s["id"]: s for s in snap["sources"]}
order = sorted(has, key=lambda s: int(s[2:]))
cols = [name[c["id"]] for c in codes]
results, rows = [], []
for sid in order:
    s = src[sid]
    title = s["title"].removeprefix("Dossier: ")
    vals = [int(c["id"] in has[sid]) for c in codes]
    rows.append([title, s["uri"]] + vals)
    for c, v in zip(codes, vals):
        results.append({"variable": name[c["id"]], "value": v, "conditions": {"system": title, "link": s["uri"]}})
d = os.environ.get("CLAIMSET_RUN_DIR", ".")
with open(os.path.join(d, "systems.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["system", "link"] + cols); w.writerows(rows)
r = os.environ.get("CLAIMSET_RESULTS")
if r:
    json.dump(results, open(r, "w"), indent=0)
print(len(rows), "systems,", len(cols), "codes")
