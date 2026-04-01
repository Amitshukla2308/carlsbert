# EvoCoder Contrastive Training Pairs

**Generated:** 2026-04-01 20:41

## Dataset Summary

| Metric | Value |
|--------|-------|
| Total triplets | 13,292 |
| Unique anchors | 3,244 |
| Unique positives | 2,717 |
| Cross-service positives | 495 (3.7%) |
| Average positive weight | 15.0 |
| Skipped (no positive w>=5) | 955 |
| Skipped (no hard negatives) | 4 |

## Positive Weight Distribution

| Weight Range | Count | % |
|-------------|-------|---|
| 5-10 | 7,775 | 58.5% |
| 11-20 | 3,449 | 25.9% |
| 21-50 | 1,574 | 11.8% |
| 51+ | 494 | 3.7% |

## Design Choices

- **Positive selection:** Co-change weight >= 5 and module exists in current MG
- **Hard negatives:** Same service as anchor, NOT in any co-change partner set
  (structurally close but evolutionarily independent = hardest negatives)
- **Cap:** Max 5 positives per anchor to avoid over-representing high-degree modules
- **Use case:** Contrastive fine-tuning of code embedding model (e.g. LoRA on CodeXEmbed)
  where positive pairs should have closer embeddings than negative pairs

## File Format

JSONL with fields:
```json
{"anchor": "Module.Name", "positive": "Module.Name", "negative": "Module.Name",
  "pos_weight": int, "anchor_service": str, "cross_service_positive": bool}
```
