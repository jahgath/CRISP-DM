import os, json, sys, joblib
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from fastapi import FastAPI
from pydantic import BaseModel, Field
import rfm

ART = joblib.load(os.environ.get("SEG_PATH", os.path.join(HERE, "..", "artifacts", "segmentation.joblib")))
RULES = json.load(open(os.environ.get("RULES_PATH", os.path.join(HERE, "..", "artifacts", "rules.json"))))
app = FastAPI(title="Retail knowledge service", version="1.0")

class RFMIn(BaseModel):
    recency_days: float = Field(ge=0, description="days since last purchase at scoring date")
    frequency: int = Field(ge=1, description="number of invoices to date")
    monetary: float = Field(gt=0, description="total net spend to date (GBP)")

class BasketIn(BaseModel):
    stock_codes: list[str]
    top_n: int = Field(default=5, ge=1, le=20)

@app.get("/health")
def health(): return {"status": "ok", "k": ART["k"], "snapshot": ART["snapshot"], "n_rules": len(RULES)}

@app.post("/segment")
def segment(x: RFMIn):
    c, name = rfm.assign_segment(ART, x.recency_days, x.frequency, x.monetary)
    return {"segment_id": c, "segment": name, "recommended_action": ART["actions"][c]}

@app.post("/recommend")
def recommend(b: BasketIn):
    have = set(b.stock_codes); out = {}
    for r in RULES:
        if set(r["antecedent"]) <= have:
            for code, nm in zip(r["consequent"], r["consequent_names"]):
                if code not in have and (code not in out or r["lift"] > out[code]["lift"]):
                    out[code] = {"stock_code": code, "description": nm, "confidence": r["confidence"], "lift": r["lift"], "validated_lift": r["val_lift"]}
    return {"suggestions": sorted(out.values(), key=lambda d: -d["lift"])[: b.top_n]}
