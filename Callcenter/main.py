from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import ibm_boto3
from ibm_botocore.client import Config
import os

app = FastAPI(title="Customer Support Data API")

# ---- CONFIG IBM COS ----
COS_API_KEY = os.getenv("COS_API_KEY")
COS_SERVICE_CRN = os.getenv("COS_SERVICE_CRN")
COS_ENDPOINT = "https://s3.us-south.cloud-object-storage.appdomain.cloud"     # ejemplo: "https://s3.us-south.cloud-object-storage.appdomain.cloud"
COS_BUCKET = os.getenv("COS_BUCKET")
COS_CSV_KEY = "RegistrosEni.csv"    # archivo: "dataset/support_calls.csv"



# ---- cliente ----
cos = ibm_boto3.client(
    "s3",
    ibm_api_key_id=COS_API_KEY,
    ibm_service_instance_id=COS_SERVICE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

# ---- cargamos el CSV una vez ----
dataframe = None

def load_csv():
    global dataframe
    try:
        obj = cos.get_object(Bucket=COS_BUCKET, Key=COS_CSV_KEY)

        # ⚠ FIX: manejar CSV complejo
        df = pd.read_csv(
            obj["Body"],
            sep=",",
            engine="python",
            encoding="utf-8",
            on_bad_lines="skip"
        )

        # ⚠ FIX: convertir NaN → None
        df = df.where(pd.notnull(df), None)

        dataframe = df
        print("CSV loaded successfully.")

    except Exception as e:
        print("Error loading CSV:", str(e))


@app.on_event("startup")
def startup_event():
    load_csv()


class Query(BaseModel):
    field: str
    value: str


@app.get("/")
def root():
    return {"message": "Customer Support API running."}


@app.get("/all")
def get_all():
    if dataframe is None:
        raise HTTPException(500, "CSV not loaded")
    return dataframe.to_dict(orient="records")


@app.post("/search")
def search(query: Query):
    if dataframe is None:
        raise HTTPException(500, "CSV not loaded")

    if query.field not in dataframe.columns:
        raise HTTPException(400, f"Invalid field {query.field}")

    df_filtered = dataframe[
        dataframe[query.field].astype(str).str.contains(query.value, case=False, na=False)
    ]

    return {
        "count": len(df_filtered),
        "results": df_filtered.to_dict(orient="records")
    }


@app.get("/usuario/{usuario_id}")
def get_by_user(usuario_id: str):
    if dataframe is None:
        raise HTTPException(500, "CSV not loaded")

    df_u = dataframe[dataframe["Usuario"] == usuario_id]

    if df_u.empty:
        raise HTTPException(404, "Usuario no encontrado")

    return df_u.to_dict(orient="records")
