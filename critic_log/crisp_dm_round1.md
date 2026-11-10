# CRISP-DM project — Critic round 1

**Critic:** Claude subagent, prompted as "a world-renowned speaker and the leading authority on CRISP-DM who has written many award-winning books on the subject" (not GPT-5).
**Target:** `1_CRISP-DM/crisp_dm_telco_churn.ipynb` as executed on 2026-11-09. Cell-level review; the critic did not run the code.
**Verdict:** Competent, honest in places, but the "all 6 phases, every output" claim fails. It reads like a clean Kaggle pipeline with CRISP-DM headings, and several QA ticks are contradicted by the notebook's own code and outputs.

Scores: Business Understanding 6, Data Understanding 5, Data Preparation 5, Modeling 6, Evaluation 6, Deployment 4.

## Blockers
- **B1. "Test set used once" is false.** The test set is also used by the sensitivity grid (threshold optimised on test), permutation importance, the fairness audit, the drift simulation and the stored `test_auc`. Reword the claim or move that work to OOF predictions.
- **B2. The operating point is degenerate and the API contradicts the plan.** The confusion matrix `[[503 532],[16 358]]` flags 890 of 1,409 customers (63%) at threshold 0.09. The narrative said 61%, which is accuracy. Section 6.1 promises ranking by `score × MonthlyCharges` under capacity, but `/predict` only returns `p >= 0.09`. Implement and test the capacity-ranked batch scorer.
- **B3. Promised deliverables do not exist.** `artifacts/model_card.md`, `README.md`, the article and `critic_log/` were absent.
- **B4. Deployment was never exercised as deployed.** No Docker build, no uvicorn, no HTTP call. Training ran on Python 3.14 but the Dockerfile uses `python:3.11-slim` with pins that may not resolve. Build the container, curl `/predict`, and assert it matches the notebook score.

## Major
- **M1.** Several narrative claims have no printed support: the gender chi-square (gender is not in `cats`), "two-year ~3%" and "senior ~2×" (plots only), and "drivers agree" (permutation values never printed; LR top-6 omits PaymentMethod, which the verdict lists). No quantitative rule for "drivers stable".
- **M2.** Collinear duplicate features (`tenure`/`tenure_years`, `MonthlyCharges`/`avg_monthly_paid`, `TotalCharges` kept despite the DQ table) corrupt explainability. Drop duplicates or group them for permutation importance.
- **M3.** The fairness criterion is gamed by the threshold: recall gaps are trivial when 96% of churners are flagged. The false-positive-rate gap for seniors is 22 points (0.710 vs 0.487) and still got a tick. No CIs on groups (seniors n=222).
- **M4.** Model choice is a tie (OOF AUC LogReg 0.8466 vs HistGB 0.8471) resolved against the project's own explainability criterion. Random forest dropped from tuning without justification, although 4.3 says "two best families". Report LR test profit alongside HistGB.
- **M5.** The same CV folds are used for tuning, OOF assessment, model choice and threshold choice; no nested CV.
- **M6.** The business case is thinly supported: unsourced $20 / 30% assumptions; only the model column is sensitivity-tested; `model_beats_offer_all` computed but never shown; no interval on the 9% margin; no CI on lift; single random-baseline draw; the `prob×value` ranking loses to `prob` at 30% contact and this is not discussed.
- **M7.** Monitoring is a function, not a system: reference scores are in-sample, the "ALERT" demo is hand-engineered (PSI 0.2594 vs 0.25), nothing logs requests or joins labels, the A/B plan has no holdout size or power calculation.

## Minor
Decorative imputer; `charge_drift` kept despite r = 0.002 with churn and no ablation; 3.1 promises a post-modeling selection revisit that never happens; `tenure` outcome-contamination flagged then not addressed; class-weighted LR/RF compared with unweighted HistGB at an implicit 0.5 threshold; confusing Cramér's V `k` formula; rounded p-values print 0.0 with no multiplicity note; production model trained on 80% only; `extra="allow"` plus free-string categoricals silently scores typos; no artifact versioning.

## Phase gaps (CRISP-DM generic outputs)
- **1:** no stakeholders/sponsor, no project cost-benefit, no timeline or dependencies; criterion 3 not measurable; AUC ≥ 0.80 unjustified.
- **2:** `describe` omits TotalCharges and categoricals; no numeric correlation/collinearity check; no data-requirements statement; unverified licence/provenance claim; exploration report relies on plots.
- **3:** thin inclusion/exclusion rationale; no reformatted-data description; no derived-attributes table; no feature ablation.
- **4:** no parameter-settings record; rule baseline never in the CV table; calibration plotted but not quantified (no Brier/ECE baseline).
- **5:** verdict table too generous; re-issue with CIs and honest warnings.
- **6:** final report is one paragraph; project review generic.

**Is it deployable?** Not as claimed. Round-2 gate: B1–B4 closed, with printed evidence for every narrative number.

---
## Status (maintained by the author)
- Fixed so far: article figure corrected from 61% to 63% flagged; article no longer claims the test set was used once.
- Not yet fixed in the notebook: everything above. Revision round 2 is pending.
