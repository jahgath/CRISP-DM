import sys, os, joblib, pandas as pd, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from student_features import select, SCENARIO_NAMES

ART = joblib.load(os.environ.get("MODEL_PATH", os.path.join(os.path.dirname(__file__), "..", "artifacts", "student_pipelines.joblib")))
app = FastAPI(title="Student grade early-warning", version="1.0")

class Student(BaseModel):
    school: str; sex: str; age: int; address: str; famsize: str; Pstatus: str; Medu: int; Fedu: int; Mjob: str; Fjob: str
    reason: str; guardian: str; traveltime: int; studytime: int; failures: int; schoolsup: str; famsup: str; paid: str
    activities: str; nursery: str; higher: str; internet: str; romantic: str; famrel: int; freetime: int; goout: int
    Dalc: int; Walc: int; health: int; absences: int
    G1: Optional[int] = None   # supply after period 1 to use scenario B
    G2: Optional[int] = None   # supply G1 and G2 after period 2 to use scenario C

@app.get("/health")
def health():
    return {"status": "ok", "trained_at": ART["trained_at"], "regressors": ART["reg_names"], "classifiers": ART["clf_names"]}

def _scenario(s: Student) -> str:
    if s.G2 is not None and s.G1 is None: raise HTTPException(422, "G2 given without G1")
    return "C" if s.G2 is not None else ("B" if s.G1 is not None else "A")

@app.post("/predict")
def predict(s: Student):
    scn = _scenario(s)
    df = pd.DataFrame([s.model_dump()])
    X = select(df, scn)
    g3 = float(np.clip(ART["regressors"][scn].predict(X)[0], 0, 20))
    pf = float(ART["classifiers"][scn].predict_proba(X)[0, 1])
    return {"scenario": SCENARIO_NAMES[scn], "predicted_G3": round(g3, 2), "p_fail": round(pf, 3), "model": ART["reg_names"][scn],
            "caveat": "Statistical estimate from n=316 students; use to prioritise support, not to decide outcomes."}
