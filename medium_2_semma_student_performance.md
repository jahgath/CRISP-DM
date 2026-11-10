# SEMMA on Student Grades: When the Early-Warning Model Barely Beats "Just Guess the Average"

*Sample, Explore, Modify, Model, Assess on the UCI Student Performance data, with a Python re-implementation of the SAS workflow. Code: https://github.com/jahgath/CRISP-DM/tree/main/2_SEMMA*

---

**Honest scope note first:** I did **not** run SAS. I had no SAS Enterprise Miner or Viya trial licence, so this is a Python (scikit-learn) re-implementation of the SEMMA workflow, node by node, with a mapping table to the SAS nodes. The numbers are not SAS output, and the SAS-style score code I generated was only checked for arithmetic in Python, never run in SAS.

SEMMA is SAS's five-stage process for data-mining projects: **S**ample, **E**xplore, **M**odify, **M**odel, **A**ssess. It is narrower than CRISP-DM (no business-understanding or deployment phase), and tightly tied to a tool workflow of nodes on a canvas. That makes it a good fit for a clean modeling exercise, and a good place to be careful about the Assess step.

## The dataset and the trap in it

UCI *Student Performance* (Cortez & Silva, 2008): two Portuguese secondary schools, **395 math students**, 33 columns. The target is `G3`, the final grade (0–20).

The trap is `G1` and `G2`, the first- and second-period grades. They predict `G3` extremely well, because they are earlier measurements of the same thing. A model that uses them looks superb and is nearly useless: if you already know G2, you're almost done. The question that matters is *"who will fail before we have grades?"*

So I never report one model. Every stage runs on three information scenarios:

| Scenario | Inputs | Use case |
|---|---|---|
| **A: early warning** | demographics, family, habits, absences (no grades) | start of year, the meaningful case |
| **B: after period 1** | A + G1 | mid-year intervention |
| **C: after period 2** | A + G1 + G2 | upper bound / sanity check |

Each scenario has two baselines: predict the training mean, and "copy the latest known grade".

## S: Sample

- 60/20/20 train/validation/test split (237 / 79 / 79), stratified on pass/fail (fail = G3 < 10, 32.9% of students).
- Why stratify? Over 500 simulated seeds, a plain random split put the validation fail rate on average 3.9 points away from the true rate (95th percentile: 10.1 points). With 79 validation rows, 10 points is about 8 students, enough to change which model looks best.
- Partitions are representative: near-identical G3 distributions, and the largest standardised mean difference on any numeric input is 0.2 standard deviations.
- A warning carried forward: 38 students (9.6%) have G3 = 0, and 25 of them had a non-zero G2, meaning they stopped or skipped the final assessment.

## E: Explore (training data only)

- Grades dominate: Spearman ρ with G3 is 0.95 for G2 and 0.88 for G1. The strongest non-grade variable is past `failures` (−0.38).
- After Benjamini–Hochberg correction, nine non-grade variables relate to G3, but only `failures` and `goout` relate to pass/fail. Effects are small.
- **`absences` is a trap.** It has the highest mutual information with G3 (0.19) but a Spearman p-value of 0.95, because the relationship is non-monotone. The explanation: **all 38 students with G3 = 0 have `absences = 0`**. In the training data, 31% of zero-absence students have G3 = 0, versus 0% of students with at least one absence. "Zero absences" here is partly a recording artefact for students who didn't complete the course, not perfect attendance. I don't know how the school recorded it. The pattern is certain; the cause is my inference.

That finding matters later: a model using `absences` can partly *recognise dropouts after the fact*, which is impossible in a real start-of-year deployment.

## M: Modify

Variable clustering confirmed the obvious redundancy (mother's and father's education, ρ = 0.67; weekday and weekend alcohol, ρ = 0.64). I added combined versions and kept the originals, and I did not test whether the combinations help, so I make no claim that they do. Absences got a log transform (skew 3.43 → 0.14). Lasso on scenario A kept 19 of 46 encoded columns. Its signs deserve caution: family support and school support came out *negative*, which almost certainly reflects struggling students *receiving* support, not support lowering grades. Don't read any of these coefficients as advice.

## M: Model

I compared OLS, ridge, lasso, a decision tree, a random forest and gradient boosting for regression, plus classifier equivalents for pass/fail, using validation scores and repeated cross-validation.

The pattern is the same in every scenario:

- **Within a scenario, the top tree ensembles are ties.** Validation RMSE differences are 0.01–0.07 while CV standard deviations are 0.24–0.35. The "champion" is set by a rule I fixed in advance, not by a meaningful gap.
- **Scenario A is hard.** The best validation R² is 0.21. Pooled CV RMSE is 3.96 against 4.64 for the mean predictor, about 15% better.
- **Grades make the problem easy but not much more informative than copying them.** In scenario B, the one-line rule "G1 < 10" scores AUC 0.920 on validation, the same as the ensembles.
- **Trees beat linear models, but partly through the artefact.** Without absence features, the forest's CV RMSE in scenario A rises from 3.96 to 4.39 while ridge hardly moves (4.23 → 4.31). The ensemble's edge over ridge disappears.

## A: Assess

Champions were chosen on validation only, then each scenario's champion was scored **once** on the locked test set (n = 79, 26 failures), with bootstrap confidence intervals.

| Scenario | Test RMSE [95% CI] | Strongest baseline RMSE | Fail AUC [95% CI] |
|---|---|---|---|
| A | 4.18 [3.16, 5.06] | 4.31 (mean) | 0.66 [0.54, 0.79] |
| B | 2.64 [2.05, 3.30] | 2.80 (copy G1) | 0.94 [0.89, 0.98] |
| C | 1.24 [0.96, 1.54] | 1.53 (copy G2) | 0.99 [0.96, 1.00] |

The honest reading:

1. **No champion is statistically distinguishable from its strongest baseline.** Every paired-bootstrap interval for the RMSE gain includes zero (for example, scenario B: −0.34 to +0.63). The point estimates favour the models, and the pooled CV agrees in direction, but with 79 test rows I can't claim the models beat "copy the last grade".
2. **The meaningful case, scenario A, is modest.** Test AUC is 0.66 and test R² about 0.06. The CV suggested better. Two reasons: hyper-parameters were tuned on training rows that also appear in the pooled CV folds (optimistic), and the test set is tiny. On 316 out-of-fold predictions, flagging the top 20% gives precision 0.59 (base rate 0.33) and recall 0.36. That is a prioritisation aid for outreach, not a reliable predictor.
3. **The G1/G2 answer:** adding G1 cuts RMSE from about 4.2 to 2.6 and AUC from 0.66 to 0.94. Adding G2 reaches RMSE 1.24 and AUC 0.99. That is mostly because earlier grades are measurements of the same quantity. Read scenario C as an upper bound, A as the real problem, and B as the practical compromise, since a mid-year intervention still has time to act.
4. **Calibration (A):** predicted probabilities only span about 0.18–0.56. The model never expresses high confidence, which is sensible given how little signal it has.

## Deployment artefacts (what SEMMA doesn't ask for, but I did)

SEMMA stops at Assess, but the project includes a saved pipeline for each scenario, a small FastAPI service, a Dockerfile, a model card, and SAS-style score code files. The API was tested by calling its handlers directly, and I did not build the Docker image. The score code is verified against scikit-learn only, and the SAS syntax was never run.

The model card states the limits plainly: small sample, two schools in one region and one school year, sensitive attributes (sex, age, address, parental education and job) used as inputs with **no fairness audit performed**, and an intended use limited to prioritising support outreach, not grading, tracking or admissions.

## SEMMA vs CRISP-DM, from this project

- SEMMA's stages map cleanly onto CRISP-DM's data understanding, data preparation, modeling and evaluation. What's missing is the front (business objectives, success criteria) and the back (deployment, monitoring).
- That gap showed up concretely: nothing in SEMMA made me ask *what decision this model supports*. I added the three-scenario design and the model-card intended use myself.
- The upside is tight focus. Each stage has a clear question and a matching tool node.

## How to repeat this in SAS

The notebook includes a node-by-node mapping: Input Data Source → Data Partition (stratified) → StatExplore and MultiPlot → Impute, Transform Variables, Variable Selection → Regression, Decision Tree, Gradient Boosting → Model Comparison (selection statistic: validation) → Score. If you have a SAS licence, those are the nodes to drag onto the canvas.

## Takeaways

1. Define the information scenario before modeling. A model that uses G2 answers a different question from one that doesn't.
2. Always compare to a one-line baseline *with a confidence interval*. Here, that turned "RMSE 1.24" into "not provably better than copying G2".
3. Stratify small splits. A 10-point swing in the validation fail rate is about eight students.
4. Look for artefacts when a variable has high mutual information but no monotone trend. `absences = 0` was a recording artefact, not good attendance.
5. With 79 test rows, report the intervals, and let them temper the headline.

---
*Tags: semma, data-mining, education, machine-learning, python*
