# Knowledge report — KDD on Online Retail (UK)

Generated 2026-11-09 23:32. Snapshot 2011-09-01; outcomes Sep-Nov 2011.

## Data
UK, clean product lines: 478,836; with customer: 348,870; customers at snapshot: 2,985.

## Segments (k=4, bootstrap ARI 0.927, silhouette 0.368)
| segment | customers | cust_share | hist_rev_share | future_buy_rate | future_rev_share | action |
|---|---|---|---|---|---|---|
| Recent light buyers | 410 | 0.137 | 0.066 | 0.568 | 0.094 | Second-purchase nudge within 30 days: bundle suggestion + small first-repeat incentive; capture order-gap data. |
| Lapsed / one-off | 1275 | 0.427 | 0.081 | 0.373 | 0.118 | Low-cost reactivation only (e-mail, seasonal catalogue); do not spend discount budget; sunset from paid channels after 2 attempts. |
| At-risk regulars | 848 | 0.284 | 0.240 | 0.643 | 0.203 | Win-back before they lapse: personalised 'we miss you' with their top products; limited-time incentive; ask for feedback. |
| Champions | 452 | 0.151 | 0.613 | 0.925 | 0.586 | VIP programme: early access to new ranges, dedicated account contact, free-shipping threshold; protect margin (no blanket discounts). |

## Rules
253 candidate rules, 159 colour/size variants, 0 redundant, 94 retained.
Retained rules with validation lift > 1: 99%; median validation confidence 0.59.

## Repurchase prediction (test period)
| model | ROC_AUC | PR_AUC | Lift_at_20 |
|---|---|---|---|
| Rule: recency only (recent = likely) | 0.682 | 0.702 | 1.358 |
| Rule: orders in last 90d | 0.688 | 0.761 | 1.513 |
| Logistic regression | 0.740 | 0.805 | 1.603 |
| Gradient boosting | 0.735 | 0.800 | 1.594 |

Paired bootstrap vs recency-only:

| model | mean_diff | lo | hi | CI_excludes_0 |
|---|---|---|---|---|
| Rule: orders in last 90d | 0.007 | -0.006 | 0.019 | False |
| Logistic regression | 0.058 | 0.042 | 0.075 | True |
| Gradient boosting | 0.053 | 0.038 | 0.068 | True |

## Checks
| goal | test | passed | evidence |
|---|---|---|---|
| G1 | k = 4 within 3..6 | True | k=4 |
| G1 | bootstrap ARI >= 0.75 | True | mean ARI 0.927 (min 0.837) |
| G1 | smallest segment >= 3% | True | 13.7% |
| G1 | segments differ in FUTURE purchase rate (spread >= 0.15) | True | 0.37 .. 0.92 |
| G2 | >= 5 non-trivial rules retained | True | 94 rules |
| G2 | validation lift > 1 for >= 70% of retained rules | True | 99% |
| G3 | gradient boosting AUC > recency-only AUC with CI excluding 0 | True | diff +0.0527 [+0.0382, +0.0677] |
| G3 | logistic AUC > recency-only AUC with CI excluding 0 | True | diff +0.0585 [+0.0421, +0.0754] |

Limitations: one retailer, 12 months, no campaign data (association != causation), December/seasonality not covered, fixed hyper-parameters.
