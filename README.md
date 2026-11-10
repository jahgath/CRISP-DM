# CRISP-DM · SEMMA · KDD — three data-mining projects, three datasets

SJSU Data Mining assignment: the same discipline applied with each methodology, one dataset each, taken through to deployment artifacts.

| Folder | Methodology | Dataset | Task | Notebook |
|---|---|---|---|---|
| [1_CRISP-DM](1_CRISP-DM) | CRISP-DM (6 phases) | Telco Customer Churn (Kaggle `blastchar/telco-customer-churn`) | churn classification + retention economics | `crisp_dm_telco_churn.ipynb` |
| [2_SEMMA](2_SEMMA) | SEMMA (Sample, Explore, Modify, Model, Assess) | UCI Student Performance (Kaggle `uciml/student-alcohol-consumption`) | final-grade prediction, with and without G1/G2 | `semma_student_performance.ipynb` |
| [3_KDD](3_KDD) | KDD (Fayyad et al.) | Online Retail (Kaggle `carrie1/ecommerce-data`) | segmentation, association rules, temporal repurchase prediction | `kdd_online_retail.ipynb` |

Each folder also holds `src/` (shared feature code), `deploy/` (FastAPI app, Dockerfile, requirements), and `artifacts/` (saved model, plots, model card or report).

## Articles (drafts)
- [Medium 1 — CRISP-DM](medium_1_crisp_dm_telco_churn.md)
- [Medium 3 — KDD](medium_3_kdd_online_retail.md)
- [Medium 2 — SEMMA](medium_2_semma_student_performance.md)

## Run
Open a notebook in Google Colab and Run all (the notebooks fetch data themselves where possible), or locally:
```
python -m venv .venv && . .venv/bin/activate
pip install pandas numpy scikit-learn scipy matplotlib seaborn statsmodels mlxtend joblib fastapi pydantic nbformat nbconvert ipykernel
cd 1_CRISP-DM && jupyter nbconvert --to notebook --execute --inplace crisp_dm_telco_churn.ipynb
```
`3_KDD/data/data.csv` (45 MB) is not in the repo; download it from Kaggle `carrie1/ecommerce-data`.

## Honest status
- **Critic loop:** reviews were done by a Claude subagent prompted as a world-renowned authority on the methodology (not GPT-5). Round 1 for CRISP-DM is in [critic_log/](critic_log); it found real problems (e.g. test set reused after selection, deployed rule flags 63% of customers, Docker image never built) that are **not yet fixed in the notebook**. SEMMA and KDD have not been critiqued yet.
- **SAS / SPSS were not run.** The SEMMA project is a Python re-implementation with a node-mapping table to SAS Enterprise Miner.
- Docker images have not been built; API handlers were exercised in-process only.
- Videos and Medium publication are pending.
- The SEMMA notebook is executed with zero errors; its own results are candid that no champion is statistically distinguishable from its strongest baseline on the 79-row test set.
