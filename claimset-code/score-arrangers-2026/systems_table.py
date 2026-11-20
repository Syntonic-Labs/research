"""Per-system coding table for the score-arrangers-2026 study: one row per arranging system (dossier), with its link
and, for each code (full match first, then output, input, method, availability, pricing, platform), a tick if pass 1 coded the dossier with it; results give 1 or 0. Reads $CLAIMSET_CODINGS; writes the table
as systems.csv in $CLAIMSET_RUN_DIR and its cells as results to $CLAIMSET_RESULTS."""
import csv, json, os
snap = json.load(open(os.environ["CLAIMSET_CODINGS"], encoding="utf-8"))
ORDER = ["TM12", "TM2", "TM3", "TM4", "TM5", "TM6", "TM7", "TM8", "TM9", "TM10", "TM11",
         "TM14", "TM15", "TM16", "TM17", "TM18", "TM19", "TM20", "TM21", "TM22", "TM23"]
byid = {c["id"]: c for c in snap["codes"]}
codes = [byid[i] for i in ORDER if i in byid]
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
    rows.append([title, s["uri"]] + ["\u2713" if v else "" for v in vals])
    for c, v in zip(codes, vals):
        results.append({"variable": name[c["id"]], "value": v, "conditions": {"system": title, "link": s["uri"]}})
d = os.environ.get("CLAIMSET_RUN_DIR", ".")
with open(os.path.join(d, "systems.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["system", "link"] + cols); w.writerows(rows)
r = os.environ.get("CLAIMSET_RESULTS")
if r:
    json.dump(results, open(r, "w"), indent=0)
print(len(rows), "systems,", len(cols), "codes")
