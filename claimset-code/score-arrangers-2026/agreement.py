"""Agreement between the two coders of the score-arrangers-2026 study (plan PL2).

Reads $CLAIMSET_CODINGS. For each code, over the dossiers coded in both pass 1 and pass 2, computes Krippendorff's
alpha for two coders and nominal (present/absent) data, and the share of dossiers on which the coders agree.
Writes the results to $CLAIMSET_RESULTS.
"""

import json
import os
import sys
from collections import defaultdict


def alpha_binary(pairs):
    """Krippendorff's alpha, two coders, nominal data, no missing values: pairs is a list of (a, b) in {0, 1}."""
    n = 2 * len(pairs)
    if n == 0:
        return None
    n1 = sum(a + b for a, b in pairs)
    n0 = n - n1
    d_o = sum(a != b for a, b in pairs) * 2 / n  # disagreeing pairable values / n
    d_e = 2 * n0 * n1 / (n * (n - 1))
    if d_e == 0:
        return 1.0 if d_o == 0 else None
    return 1 - d_o / d_e


def main():
    snap = json.load(open(os.environ["CLAIMSET_CODINGS"], encoding="utf-8"))
    name = {c["id"]: c["term"] for c in snap["codes"]}
    has = {1: defaultdict(set), 2: defaultdict(set)}
    for row in snap["codings"]:
        p = row.get("pass", 1)
        if p in has:
            has[p][row["source"]].update(name.get(c, c) for c in row["codes"])
    both = sorted(set(has[1]) & set(has[2]))
    out = [{"variable": "dossiers coded by both coders", "value": len(both)}]
    for code in sorted(name.values()):
        pairs = [(int(code in has[1][s]), int(code in has[2][s])) for s in both]
        a = alpha_binary(pairs)
        if a is not None:
            out.append({"variable": "Krippendorff alpha", "value": round(a, 6), "conditions": {"code": code}})
        if pairs:
            out.append({"variable": "share of dossiers agreed", "value": sum(x == y for x, y in pairs) / len(pairs),
                        "conditions": {"code": code}})
    res = os.environ.get("CLAIMSET_RESULTS")
    if res:
        json.dump(out, open(res, "w", encoding="utf-8"), indent=1)
    else:
        print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
