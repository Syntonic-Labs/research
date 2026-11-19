"""Draw the second coder's sample (plan PL1/PL2 design): 25% of the dossiers, Python random.sample with seed 2026,
over dossier source IDs SR1..SRn in capture order. Usage: sample.py N (number of dossiers)."""
import json, os, random, sys
n = int(sys.argv[1])
ids = [f"SR{i}" for i in range(1, n + 1)]
k = round(0.25 * n)
random.seed(2026)
s = sorted(random.sample(ids, k), key=lambda x: int(x[2:]))
d = os.environ.get("CLAIMSET_RUN_DIR", ".")
json.dump(s, open(os.path.join(d, "sample.json"), "w"))
print(" ".join(s))
r = os.environ.get("CLAIMSET_RESULTS")
if r:
    json.dump([{"variable": "dossiers in second-coder sample", "value": k},
               {"variable": "dossiers captured", "value": n}], open(r, "w"))
