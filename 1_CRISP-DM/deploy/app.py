import sys, os, joblib, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict
from features import feature_frame

ART = joblib.load(os.environ.get("MODEL_PATH", os.path.join(os.path.dirname(__file__), "..", "artifacts", "churn_pipeline.joblib")))
app = FastAPI(title="Telco churn scoring", version="1.0")

class Customer(BaseModel):
    model_config = ConfigDict(extra="allow")
    customerID: str = "unknown"
    gender: str; SeniorCitizen: int; Partner: str; Dependents: str; tenure: int; PhoneService: str; MultipleLines: str
    InternetService: str; OnlineSecurity: str; OnlineBackup: str; DeviceProtection: str; TechSupport: str
    StreamingTV: str; StreamingMovies: str; Contract: str; PaperlessBilling: str; PaymentMethod: str
    MonthlyCharges: float; TotalCharges: str

@app.get("/health")
def health(): return {"status": "ok", "model": ART["model"], "trained_at": ART["trained_at"], "threshold": ART["threshold"]}

@app.post("/predict")
def predict(c: Customer):
    df = pd.DataFrame([c.model_dump()])
    p = float(ART["pipeline"].predict_proba(feature_frame(df))[:, 1][0])
    return {"customerID": c.customerID, "churn_probability": round(p, 4), "flag_for_retention": p >= ART["threshold"]}
