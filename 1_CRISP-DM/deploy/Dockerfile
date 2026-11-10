FROM python:3.11-slim
WORKDIR /app
COPY deploy/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY artifacts/churn_pipeline.joblib ./artifacts/churn_pipeline.joblib
COPY deploy/app.py ./deploy/app.py
EXPOSE 8000
CMD ["uvicorn", "deploy.app:app", "--host", "0.0.0.0", "--port", "8000"]
