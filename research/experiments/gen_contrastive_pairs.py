"""
Generate contrastive training pairs from co-change data for EvoCoder.

Produces (anchor_module, positive_module, negative_module) triplets where:
- anchor: any module with co-change data
- positive: module with high co-change weight to anchor (frequently change together)
- negative: same-service module with ZERO co-change to anchor (structurally close but
  evolutionarily independent — hard negative)

Output: JSONL file with triplets + metadata for future contrastive fine-tuning.
"""
import json, random, time
from collections import defaultdict

COCHANGE_PATH = "/home/beast/projects/workspaces/juspay/artifacts/cochange_index.json"
GRAPH_PATH = "/home/beast/projects/workspaces/juspay/artifacts/graph_with_summaries.json"
OUT_PATH = "/home/beast/carlsbert/research/data/contrastive_pairs.jsonl"
STATS_PATH = "/home/beast/carlsbert/research/data/contrastive_pairs_stats.md"

MIN_POS_WEIGHT = 5    # minimum co-change weight for positive pairs
MIN_NEG_POOL = 3      # minimum negatives available per anchor

random.seed(42)


def cc_to_mg(cc_key):
    parts = cc_key.split("::")
    for i, part in enumerate(parts):
        if part and part[0].isupper():
            return ".".join(parts[i:])
    return cc_key


def extract_service(cc_key):
    return cc_key.split("::")[0]


def main():
    t0 = time.time()

    # Load co-change
    print("Loading co-change index...")
    with open(COCHANGE_PATH) as f:
        ci = json.load(f)
    edges = ci["edges"]
    print(f"  {len(edges)} modules")

    # Load graph for module metadata
    print("Loading graph...")
    with open(GRAPH_PATH) as f:
        g = json.load(f)
    mg_modules = set(n.get("module", "") for n in g["nodes"] if n.get("module"))
    mod_to_svc = {}
    for n in g["nodes"]:
        m = n.get("module", "")
        if m:
            mod_to_svc[m] = n.get("service", "")
    print(f"  {len(mg_modules)} MG modules")

    # Build service → modules index
    svc_to_mods = defaultdict(set)
    for m, s in mod_to_svc.items():
        if s:
            svc_to_mods[s].add(m)

    # Build CC→MG mapping
    cc_to_mg_map = {}
    mg_to_cc_map = {}
    for cc_key in edges:
        mg_name = cc_to_mg(cc_key)
        cc_to_mg_map[cc_key] = mg_name
        if mg_name in mg_modules:
            mg_to_cc_map[mg_name] = cc_key

    print(f"  {len(mg_to_cc_map)} mapped modules")

    # Generate triplets
    print("Generating contrastive triplets...")
    triplets = []
    skipped_no_positive = 0
    skipped_no_negative = 0

    for anchor_mg, anchor_cc in mg_to_cc_map.items():
        anchor_svc = mod_to_svc.get(anchor_mg, "")
        if not anchor_svc:
            continue

        # Get positive candidates (high co-change weight, also in MG)
        positives = []
        anchor_partners = set()  # all co-change partners (for negative filtering)
        for nb in edges.get(anchor_cc, []):
            nb_mg = cc_to_mg(nb["module"])
            anchor_partners.add(nb_mg)
            if nb["weight"] >= MIN_POS_WEIGHT and nb_mg in mg_modules:
                positives.append((nb_mg, nb["weight"]))

        if not positives:
            skipped_no_positive += 1
            continue

        # Get negative candidates: same service, NOT in co-change partners
        same_svc_mods = svc_to_mods.get(anchor_svc, set())
        negatives = [m for m in same_svc_mods
                     if m != anchor_mg and m not in anchor_partners]

        if len(negatives) < MIN_NEG_POOL:
            skipped_no_negative += 1
            continue

        # Generate triplets: for each positive, sample a random negative
        for pos_mg, pos_weight in positives[:5]:  # cap at 5 positives per anchor
            neg_mg = random.choice(negatives)
            pos_svc = mod_to_svc.get(pos_mg, "")
            neg_svc = mod_to_svc.get(neg_mg, "")

            triplets.append({
                "anchor": anchor_mg,
                "positive": pos_mg,
                "negative": neg_mg,
                "pos_weight": pos_weight,
                "anchor_service": anchor_svc,
                "positive_service": pos_svc,
                "negative_service": neg_svc,
                "cross_service_positive": anchor_svc != pos_svc,
            })

    print(f"  Generated {len(triplets)} triplets")
    print(f"  Skipped (no positive): {skipped_no_positive}")
    print(f"  Skipped (no negative): {skipped_no_negative}")

    # Write triplets
    with open(OUT_PATH, "w") as f:
        for t in triplets:
            f.write(json.dumps(t) + "\n")
    print(f"  Written to {OUT_PATH}")

    # Statistics
    cross_svc_pos = sum(1 for t in triplets if t["cross_service_positive"])
    weights = [t["pos_weight"] for t in triplets]
    avg_weight = sum(weights) / len(weights) if weights else 0
    unique_anchors = len(set(t["anchor"] for t in triplets))
    unique_positives = len(set(t["positive"] for t in triplets))

    # Weight distribution
    w_buckets = defaultdict(int)
    for w in weights:
        if w <= 10: w_buckets["5-10"] += 1
        elif w <= 20: w_buckets["11-20"] += 1
        elif w <= 50: w_buckets["21-50"] += 1
        else: w_buckets["51+"] += 1

    stats = f"""# EvoCoder Contrastive Training Pairs

**Generated:** {time.strftime("%Y-%m-%d %H:%M")}

## Dataset Summary

| Metric | Value |
|--------|-------|
| Total triplets | {len(triplets):,} |
| Unique anchors | {unique_anchors:,} |
| Unique positives | {unique_positives:,} |
| Cross-service positives | {cross_svc_pos:,} ({cross_svc_pos/len(triplets)*100:.1f}%) |
| Average positive weight | {avg_weight:.1f} |
| Skipped (no positive w>={MIN_POS_WEIGHT}) | {skipped_no_positive:,} |
| Skipped (no hard negatives) | {skipped_no_negative:,} |

## Positive Weight Distribution

| Weight Range | Count | % |
|-------------|-------|---|
| 5-10 | {w_buckets["5-10"]:,} | {w_buckets["5-10"]/len(triplets)*100:.1f}% |
| 11-20 | {w_buckets["11-20"]:,} | {w_buckets["11-20"]/len(triplets)*100:.1f}% |
| 21-50 | {w_buckets["21-50"]:,} | {w_buckets["21-50"]/len(triplets)*100:.1f}% |
| 51+ | {w_buckets["51+"]:,} | {w_buckets["51+"]/len(triplets)*100:.1f}% |

## Design Choices

- **Positive selection:** Co-change weight >= {MIN_POS_WEIGHT} and module exists in current MG
- **Hard negatives:** Same service as anchor, NOT in any co-change partner set
  (structurally close but evolutionarily independent = hardest negatives)
- **Cap:** Max 5 positives per anchor to avoid over-representing high-degree modules
- **Use case:** Contrastive fine-tuning of code embedding model (e.g. LoRA on CodeXEmbed)
  where positive pairs should have closer embeddings than negative pairs

## File Format

JSONL with fields:
```json
{{"anchor": "Module.Name", "positive": "Module.Name", "negative": "Module.Name",
  "pos_weight": int, "anchor_service": str, "cross_service_positive": bool}}
```
"""

    with open(STATS_PATH, "w") as f:
        f.write(stats)
    print(f"  Stats written to {STATS_PATH}")
    print(f"\nDone in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
