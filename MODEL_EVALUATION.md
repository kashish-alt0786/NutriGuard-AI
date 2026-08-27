# Model Evaluation

## Food Recognition

The application uses the published Food-101 image classifier and a broader zero-shot fallback. The evaluation dashboard is designed to report measured benchmark results rather than inventing values.

| Metric | Result |
|---|---|
| Top-1 accuracy | Benchmark required; not inferred from confidence |
| Top-5 accuracy | Benchmark required; not inferred from confidence |
| Food-101 classes | 101 |
| Confidence distribution | Captured from inference runs; benchmark artifact recommended |
| Correct predictions | Record against a labelled validation set |
| Incorrect predictions | Record against a labelled validation set |

**Important:** model confidence is not the same thing as accuracy. Top-1 and Top-5 accuracy should be calculated on a labelled image test set.

## Nutrition Matching

For each submitted food item, the pipeline can classify the match as:

- **Exact database match** — direct canonical food-name match.
- **Alias match** — common wording mapped to a canonical database record.
- **USDA fallback** — no local match, followed by USDA FoodData Central lookup when configured.
- **Unmatched** — neither local nor USDA lookup produced a usable nutrition record.

These rates should be calculated from application logs or a labelled test set; they are not hard-coded.

## End-to-End Pipeline

```text
Image
 ↓
Food Recognition
 ↓
Food Name Normalization
 ↓
Nutrition Database
 ↓
Nutrition Analysis
 ↓
Risk-Aware Educational Guidance
```

## Serving Size / Portion Adjustment

Nutrition records are treated as base values (typically per 100 g) and scaled to the selected serving amount.

Example interface:

```text
Food: Rice
Serving: 100 g / 150 g / 200 g / Custom
```

Calories, carbohydrates, protein, fat, fiber and estimated glycemic load are scaled proportionally for local records. Actual nutrition varies with ingredients, preparation and portion measurement.

## Recommended Benchmark Protocol

To complete the numerical evaluation, create a small labelled image set containing foods from the supported recognition vocabulary. For every image, store the ground-truth food label and compare it with the model's top-1 and top-5 predictions. Separately test a representative list of manually entered foods and calculate the four nutrition-matching rates.
