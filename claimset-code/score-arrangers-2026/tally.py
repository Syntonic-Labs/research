"""Counts of arranging systems by code, for the score-arrangers-2026 study (plan PL2).

Reads the codings in force from $CLAIMSET_CODINGS. One source is one arranging system's dossier. A system has a
code when any coding of pass 1 of its dossier names it. Writes the counts to $CLAIMSET_RESULTS.
"""

import json
import os
import sys
from collections import defaultdict

METHODS = ["ML method", "rules method", "unclear method"]
AVAIL = ["commercially available", "free or open-source", "research prototype"]
PRICING = ["one-time purchase", "subscription", "free tier", "price not stated"]
PLATFORMS = ["desktop application", "web service", "DAW plugin", "notation-app plugin or feature", "mobile app",
             "code or model only"]


def main():
    path = os.environ.get("CLAIMSET_CODINGS")
    if not path:
        sys.exit("CLAIMSET_CODINGS is not set")
    snap = json.load(open(path, encoding="utf-8"))
    name = {c["id"]: c["term"] for c in snap["codes"]}
    has = defaultdict(set)
    for row in snap["codings"]:
        if str(row.get("pass", 1)) != "1":
            continue
        has[row["source"]]  # every coded source is a system, even with no code
        for c in row["codes"]:
            has[row["source"]].add(name.get(c, c))
    systems = list(has.values())
    out = [{"variable": "number of arranging systems", "value": len(systems)}]
    for code in sorted(name.values()):
        out.append({"variable": "systems with code", "value": sum(code in s for s in systems),
                    "conditions": {"code": code}})
    for m in METHODS:
        for a in AVAIL:
            out.append({"variable": "systems by method and availability",
                        "value": sum(m in s and a in s for s in systems),
                        "conditions": {"method": m, "availability": a}})
    for pl in PLATFORMS:
        for m in METHODS:
            out.append({"variable": "systems by platform and method",
                        "value": sum(pl in s and m in s for s in systems),
                        "conditions": {"platform": pl, "method": m}})
    for pr in PRICING:
        for m in METHODS:
            out.append({"variable": "systems by pricing and method",
                        "value": sum(pr in s and m in s for s in systems),
                        "conditions": {"pricing": pr, "method": m}})
    target = [s for s in systems if "notated output" in s and "user-chosen instrumentation" in s]
    for inp in ("score input", "other input"):
        for m in METHODS:
            n = sum(m in s and (("score input" in s) == (inp == "score input")) for s in target)
            out.append({"variable": "notated chosen-instrument systems by input and method", "value": n,
                        "conditions": {"input": inp, "method": m}})
    for s_count, label in ((sum(len({m for m in METHODS if m in s}) != 1 for s in systems), "method"),
                           (sum(len({a for a in AVAIL if a in s}) != 1 for s in systems), "availability")):
        out.append({"variable": "systems without exactly one code of a group", "value": s_count,
                    "conditions": {"group": label}})
    res = os.environ.get("CLAIMSET_RESULTS")
    if res:
        json.dump(out, open(res, "w", encoding="utf-8"), indent=1)
    else:
        print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
