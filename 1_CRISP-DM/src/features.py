import numpy as np, pandas as pd

ADDONS = ["OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies"]
NUM = ["tenure","MonthlyCharges","TotalCharges","n_addons","charge_drift","avg_monthly_paid","tenure_years"]
CAT = ["gender","SeniorCitizen","Partner","Dependents","PhoneService","MultipleLines","InternetService",
       "OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies",
       "Contract","PaperlessBilling","PaymentMethod","tenure_bucket","autopay","family"]

def clean_and_construct(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["TotalCharges"] = pd.to_numeric(d["TotalCharges"], errors="coerce").fillna(0.0)   # 11 new customers: billed nothing yet
    for c in ADDONS + ["MultipleLines"]:
        d[c] = d[c].replace({"No internet service": "No", "No phone service": "No"})
    d["SeniorCitizen"] = d["SeniorCitizen"].map({0: "No", 1: "Yes", "0": "No", "1": "Yes", "No": "No", "Yes": "Yes"})
    # construction
    d["n_addons"] = (d[ADDONS] == "Yes").sum(axis=1)
    d["tenure_years"] = d["tenure"] / 12
    d["avg_monthly_paid"] = np.where(d["tenure"] > 0, d["TotalCharges"] / d["tenure"].clip(lower=1), d["MonthlyCharges"])
    d["charge_drift"] = d["MonthlyCharges"] - d["avg_monthly_paid"]          # >0 : paying more now than historically
    d["tenure_bucket"] = pd.cut(d["tenure"], [-1, 6, 12, 24, 48, 100], labels=["0-6","7-12","13-24","25-48","49+"]).astype(str)
    d["autopay"] = d["PaymentMethod"].str.contains("automatic").map({True: "Yes", False: "No"})
    d["family"] = ((d["Partner"] == "Yes") | (d["Dependents"] == "Yes")).map({True: "Yes", False: "No"})
    return d

def feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    return clean_and_construct(df)[NUM + CAT]
