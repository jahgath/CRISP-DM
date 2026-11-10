import numpy as np
RFM = ["recency_days", "frequency", "monetary"]

def transform(recency_days, frequency, monetary):
    # identical to training: log1p of raw RFM (scaling is done by the saved StandardScaler)
    return np.log1p(np.array([[recency_days, frequency, monetary]], dtype=float))

def assign_segment(art, recency_days, frequency, monetary):
    x = art["scaler"].transform(transform(recency_days, frequency, monetary))
    c = int(art["kmeans"].predict(x)[0])
    return c, art["names"][c]
