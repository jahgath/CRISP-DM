# Predicting Telecom Churn with CRISP-DM: A Model That Wins on Paper and What the Numbers Really Say

*All six CRISP-DM phases, from business case to a Dockerised API, on 7,043 telecom customers. Code: [REPO_URL]/1_CRISP-DM*

---

Most churn tutorials stop at "we got 0.85 AUC". That is where the interesting part starts. This post walks through a full CRISP-DM project on the IBM/Kaggle **Telco Customer Churn** dataset and tries to be honest about where the model helps and where it doesn't.

If you only read one thing: **a good ranking model and a good business decision are not the same thing**, and CRISP-DM is the process that forces you to notice the difference.

## Why CRISP-DM

CRISP-DM has six phases: Business Understanding, Data Understanding, Data Preparation, Modeling, Evaluation, Deployment. The arrows between them go both ways. In this project that was not decoration: a data-quality finding in phase 2 changed phase 3, and an evaluation concern in phase 5 sent me back to phase 4.

## Phase 1: Business Understanding

Before touching data I wrote down:

- **Objective:** cut revenue lost to voluntary churn by targeting retention offers at customers who are likely to leave *and* worth keeping.
- **Success criteria (measurable):** ROC-AUC ≥ 0.80 on a hold-out set; lift@20% ≥ 2; campaign profit higher than both "no campaign" and "offer everyone"; drivers explainable to retention staff.
- **Cost model (assumptions, flagged as such):** an offer costs $20; a saved churner is worth 12 months of their monthly charges; the offer works on 30% of true churners.
- **Risks:** leakage through `TotalCharges`, class imbalance (26.5% churn), no timestamps (so no true temporal validation), and fairness for senior citizens.
- **Contingency:** if the model barely beats a one-line rule, ship the rule.

The cost numbers are invented. That is fine as long as you say so and test how sensitive the conclusion is to them. The notebook does.

## Phase 2: Data Understanding

One table, 21 columns. The audit turned up one real problem: `TotalCharges` is stored as text, and 11 rows are blank. All 11 have `tenure = 0`, meaning brand-new customers who have not been billed. None churned. So these are not errors to drop; they are zeros.

The exploration confirmed the intuitive story with numbers:

| Segment | Churn rate |
|---|---|
| Month-to-month contract | 42.7% |
| One-year contract | 11.3% |
| Two-year contract | 2.8% |
| Fiber-optic internet | 41.9% |
| No internet | 7.4% |
| Electronic check | 45.3% |
| Automatic bank/card payment | 15–17% |

Gender is noise (chi-square p = 0.49). Senior citizens churn at roughly twice the rate of others (44% vs 23% in the test set).

## Phase 3: Data Preparation

Three decisions mattered:

1. **Cleaning is documented, not silent.** The 11 blank `TotalCharges` become 0, with the reason written next to the code. "No internet service" and "No phone service" are collapsed to "No" because they duplicate other columns.
2. **Feature construction:** number of add-on services, tenure in years and buckets, average monthly amount paid, a `charge_drift` feature (current price minus historical average), autopay flag, family flag.
3. **No leakage.** All scaling and encoding live inside a scikit-learn `Pipeline`, fitted on training folds only. The data is split once, stratified, 80/20. The 20% test set is never used to fit models, tune hyper-parameters or choose the threshold. (Later analyses such as permutation importance and the fairness audit do read it, which a CRISP-DM critic review flagged as too loose to call "used once".)

The feature code is written to `src/features.py` and imported by both the notebook and the API, which removes the classic training/serving skew.

## Phase 4: Modeling

I compared a dummy baseline, logistic regression, random forest and gradient boosting (HistGB) with stratified 5-fold CV on the training set:

| Model | CV ROC-AUC | CV PR-AUC |
|---|---|---|
| Dummy | 0.500 | 0.265 |
| Logistic regression | 0.846 ± 0.012 | 0.660 |
| Random forest | 0.844 ± 0.010 | 0.656 |
| HistGB | 0.845 ± 0.009 | 0.653 |

After randomised hyper-parameter search, out-of-fold AUC was **0.8471 for HistGB and 0.8466 for logistic regression**. That is a tie. HistGB was picked by the rule I fixed in advance (best out-of-fold AUC), but logistic regression is just as defensible, and a lot easier to explain to a call-centre manager. If you take one modeling lesson: three very different model families landing on the same AUC usually means the data, not the algorithm, is the ceiling.

The decision threshold was chosen to maximise expected profit on **out-of-fold training predictions**, not on the test set.

## Phase 5: Evaluation

On the locked test set:

- **ROC-AUC 0.846** (95% bootstrap CI 0.825–0.867), PR-AUC 0.661 against a 0.265 prevalence
- **Lift@20% = 2.51**: the top fifth of ranked customers contains half of all churners

So the technical criteria are met. Now the business criterion, which is where it gets uncomfortable.

At the profit-optimal threshold the model earns **$76.4k**, versus **$69.8k** for offering everyone and **$68.5k** for the contract-type rule. It wins, but by about 9%. Why so small? With a $20 offer and roughly $720 × 30% of expected value per saved churner, contacting someone pays off even at ~9% churn probability. The optimal threshold is 0.09, which flags **63% of customers** (890 of 1,409). That is nearly "offer to everyone".

The model earns its keep when **capacity is limited**, which is how real retention teams work. Contacting the same number of customers:

| Contact share | Model | Random | Contract rule |
|---|---|---|---|
| 10% | $27.3k | $7.9k | $11.6k |
| 20% | $47.3k | $12.9k | $25.0k |
| 30% | $62.3k | $17.3k | $37.5k |

At 20% effort the model roughly doubles the contract rule's profit. That is the honest headline, and it is more modest and more useful than "0.85 AUC".

**Explainability.** Logistic-regression coefficients and permutation importance agree: month-to-month contract, short tenure, fiber optic and paperless billing raise risk; two-year contract, phone service and online security protect.

**Fairness.** Recall gaps between groups are small (gender 0.8 points, senior 4.4, partner 4.3). The bigger disparity is in who gets flagged: 83% of seniors versus 59% of non-seniors (false-positive rates 71% vs 49%), driven by their higher base churn and the very low threshold. My recommendation is to use the score to prioritise outreach and never to withhold service or change prices by demographic group.

**Limitations I would put on the first slide of a real project:** costs and success rate are assumptions; predicting who will churn is not predicting who is *persuadable* (an A/B test of the offer is the real next step); there are no timestamps, so expect decay; and a single 80/20 split gives one estimate, with a CI that reflects test-sample noise only.

**Next-step decision:** pilot, with an A/B-tested offer, rather than a full roll-out.

## Phase 6: Deployment

"Deployment" is more than saving a pickle:

- **Artifact:** one joblib file containing preprocessing, model, threshold and metadata.
- **Service:** a FastAPI app with `/predict` and `/health`, validated request schema, and a Dockerfile. The handlers were smoke-tested on a held-out customer.
- **Monitoring:** a Population Stability Index (PSI) check on the score distribution. Test-versus-train PSI is 0.003 (no drift). When I simulated a promotion that raised charges 25% and pushed customers to month-to-month contracts, the PSI jumped to 0.26 and the alert fired. Rule of thumb: above 0.25, investigate.
- **Retraining:** quarterly or on alert; a challenger is promoted only if it wins on AUC *and* profit.

The final report and project review close the loop: what went well (leak-proof pipeline, decisions tied to a cost model), what was hard (assumed economics are the largest uncertainty, and they are commercial, not statistical), and what I would change (log campaign responses from day one so you can build an uplift model).

## Takeaways

1. Write success criteria in business units before modeling. It is the only way to notice that a 0.85 AUC buys a 9% improvement under some assumptions and a 2x improvement under others.
2. A tie between model families is information. Prefer the one you can explain.
3. Put preprocessing inside the pipeline and choose thresholds on out-of-fold data. Most "great" results that fail in production die here.
4. Fairness is usually about *who gets flagged*, not just recall. Look at flag rates and false-positive rates.
5. Deployment is monitoring plus a retraining rule, not a file.

*Notebook, API and Docker files are in the repo above. Open the notebook in Colab and Run all; it downloads the data itself.*

---
*Tags: data-science, crisp-dm, churn, machine-learning, python*
