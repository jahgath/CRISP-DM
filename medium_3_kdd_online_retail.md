# Mining 540,000 Retail Transactions with KDD: Segments, Rules, and a Prediction That Only Modestly Beats Common Sense

*The Fayyad–Piatetsky-Shapiro–Smyth KDD process, step by step, on the UCI/Kaggle Online Retail dataset. Code: [REPO_URL]/3_KDD*

---

KDD (Knowledge Discovery in Databases) is the older sibling of CRISP-DM. Its framing is different and worth taking seriously: the goal is not a model, it is **knowledge** a person can understand, trust and act on. Data mining is only one of five steps, and the process explicitly ends with interpreting and using what you found.

This project applies the full process to an online gift retailer's transactions and tries to report honestly which patterns turned out to be solid and which were weaker than they looked.

**Data:** 541,909 invoice lines, Dec 2010 – Dec 2011, UK-based online gift retailer (the dataset description says many customers are wholesalers).
**Three mining goals:** (1) segment customers, (2) find product association rules, (3) predict who buys again in the next 90 days.

## Pre-KDD: understand the domain and set goals

KDD starts before the data. I wrote down the domain context, defined the three goals, and defined pass/fail checks for each before running anything, for example "bootstrap cluster stability ARI ≥ 0.75" and "gradient boosting beats a recency-only rule with a bootstrap CI that excludes zero".

## Step 1: Selection

I selected UK sales only (about 91% of rows) because mixing countries conflates shipping, currency and wholesale behaviour. The period is split in time, not at random: customer features are built as of **1 September 2011**, and September–November 2011 is held out as the "future" used to validate all three goals. The outcome window stops at November, so December and the Christmas season are not covered (listed under limitations).

## Step 2: Preprocessing (and a row-count audit)

Every cleaning decision is recorded with the rows it removes:

| Step | Rows left |
|---|---|
| Raw file | 541,909 |
| UK only | 495,478 |
| Drop exact duplicate lines | 490,300 |
| Set aside cancellation invoices ("C…", 7,821 lines moved to a returns table) | 482,479 |
| Drop quantity ≤ 0 | 481,143 |
| Drop unit price ≤ 0 | 479,985 |
| Drop non-product codes (POST, BANK CHARGES, …) | 478,838 |
| Drop two mega-orders (74k and 81k units) | 478,836 |
| Customer-level table (drop missing CustomerID) | 348,870 |

27% of lines have no CustomerID. They can't be used for customer analysis, but they are still real baskets, so they're kept for association mining. Throwing them away would have silently cut the rule-mining data by a quarter.

## Step 3: Transformation

For segmentation I built **RFM** features (Recency, Frequency, Monetary), log-transformed the heavy-tailed ones and scaled them, and checked correlation and PCA to see how many real dimensions there are. For rule mining I built a binary basket-by-item matrix for the 200 most frequent items. For prediction, features computed as of the snapshot date only, including the number of orders in the last 90 days.

## Step 4: Data mining

**Goal 1, segmentation.** K-Means with k chosen by silhouette, elbow and bootstrap stability. Four segments:

| Segment | Customers | Share of historical revenue | Bought again in Sep–Nov |
|---|---|---|---|
| Champions | 452 (15%) | 61% | 92.5% |
| At-risk regulars | 848 (28%) | 24% | 64.3% |
| Recent light buyers | 410 (14%) | 7% | 56.8% |
| Lapsed / one-off | 1,275 (43%) | 8% | 37.3% |

Bootstrap stability is high (mean ARI 0.927, minimum 0.837), silhouette is 0.368, and the segments differ in *future* behaviour: from 37% to 92% repurchase. That last point matters more than any internal cluster metric, because it shows the segments predict something they weren't built on.

**Goal 2, association rules.** Frequent-itemset mining on 8,608 baskets (mining period; a further 4,654 baskets are held out for validation) gave 526 frequent itemsets and 253 rules at confidence ≥ 0.5 and lift ≥ 1.5. Then comes the part that tutorials skip: **253 rules is not 253 insights**. 159 were colour/size variants of the same product (red mug → blue mug). Removing them left 94 rules.

**Goal 3, repurchase prediction (temporal split).**

| Model | ROC-AUC | Lift@20% |
|---|---|---|
| Rule: recency only | 0.682 | 1.36 |
| Rule: orders in last 90 days | 0.688 | 1.51 |
| Logistic regression | 0.740 | 1.60 |
| Gradient boosting | 0.735 | 1.59 |

Both models beat the recency-only baseline with a paired-bootstrap CI that excludes zero (+0.059 [0.042, 0.075] and +0.053 [0.038, 0.068]). The "orders in last 90 days" rule is not distinguishable from recency alone. But note the size of the win: about 6 AUC points over a one-line rule, and logistic regression and gradient boosting are tied.

## Step 5: Interpretation and evaluation

This is where KDD earns its keep.

- **Clusters are a partition of a continuum.** A Gaussian-mixture BIC keeps improving up to k=8, and agreement with other clustering algorithms is only 0.45–0.67 ARI. The four segments are stable and useful for decisions, but they are not "natural" groups, and the names are my labels.
- **Rules validate on the later period.** 99% of the 94 retained rules have lift > 1 on September–November baskets, and their lift correlates 0.75 with the mining-period lift.
- **But most rules are shallow.** 85% (80 of 94) link products of the same range with a different design, for example *Small Marshmallows Pink Bowl → Small Dolly Mix Orange Bowl* (lift 21.6, validated 21.4). Only **14** rules cross product ranges. They also validate (lift > 1 for all 14), but they are the interesting ones, and the automatic redundancy filter removed nothing, so a human has to do the reading.
- **Prediction is weaker where it matters most.** Inside the Lapsed segment, AUC is about 0.55, close to a coin flip.

KDD draws loop-back arrows between steps; the redundancy problem above is exactly where you would loop back to preprocessing or transformation (for example, merging colour variants into product families), and I have not done that here.

## Using the knowledge

KDD ends with consolidating the knowledge:

- A segment playbook, e.g. Champions get a VIP programme and no blanket discounts; At-risk regulars get a personalised win-back; Lapsed customers get low-cost e-mail reactivation only, and are sunset from paid channels after two attempts.
- A saved segmentation model, 50 validated rules, and a small FastAPI service. Serving reproduced the training segment for all 300 randomly checked customers, and a basket recommendation returned the expected pair above.
- A knowledge report listing every pass/fail check and the limitations.

**The playbook actions are hypotheses.** There's no campaign data here, so nothing says the actions work. Association is not causation.

## KDD vs CRISP-DM, from doing both

| | KDD | CRISP-DM |
|---|---|---|
| Starts with | Domain understanding and goals | Business understanding (plus cost, risk, success criteria) |
| Data understanding | Folded into selection and preprocessing | A dedicated phase |
| Mining | One step of five | Modeling phase |
| Ends with | Interpretation and consolidating knowledge | Evaluation, then explicit deployment and monitoring |
| Feels best for | Exploratory discovery: segments, patterns, rules | Predictive projects with a business decision |

In practice KDD's Step 5 forced a more critical look at *patterns* (are these rules trivial? are the clusters real?), while CRISP-DM's phases forced a more critical look at the *business case* and deployment.

## Limitations

One retailer and 12 months of data; December and seasonality aren't covered; no campaign data; hyper-parameters were fixed, not tuned; the Docker image was not built here, only the API handlers were exercised directly.

## Takeaways

1. Log row counts at every cleaning step. The 27% of lines with no customer ID is a decision, not a detail.
2. Validate segments on **future behaviour**, not only on silhouette.
3. 253 rules is a quantity; 14 cross-range rules is the knowledge. Always count how many patterns are trivially explained.
4. Compare predictions against a one-line baseline with a confidence interval; here that turned "0.74 AUC" into "+0.06 over recency".
5. Say plainly which parts are hypotheses.

---
*Tags: kdd, data-mining, customer-segmentation, association-rules, python*
