import numpy as np, pandas as pd

CAT = ["school","sex","address","famsize","Pstatus","Mjob","Fjob","reason","guardian","schoolsup","famsup","paid",
       "activities","nursery","higher","internet","romantic"]
NUM_RAW = ["age","Medu","Fedu","traveltime","studytime","failures","famrel","freetime","goout","Dalc","Walc","health","absences"]
NUM = [c for c in NUM_RAW if c != "absences"] + ["log_absences","alc_avg","parent_edu","past_failure"]
BASE = NUM + CAT
SCENARIOS = {"A": BASE, "B": BASE + ["G1"], "C": BASE + ["G1", "G2"]}
SCENARIO_NAMES = {"A": "A: early warning (no grades)", "B": "B: after period 1 (+G1)", "C": "C: after period 2 (+G1,G2)"}
PASS_MARK = 10

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["log_absences"] = np.log1p(d["absences"])
    d["alc_avg"] = (d["Dalc"] + d["Walc"]) / 2
    d["parent_edu"] = (d["Medu"] + d["Fedu"]) / 2
    d["past_failure"] = (d["failures"] > 0).astype(int)
    return d

def select(df: pd.DataFrame, scn: str) -> pd.DataFrame:
    return build_features(df)[SCENARIOS[scn]]
