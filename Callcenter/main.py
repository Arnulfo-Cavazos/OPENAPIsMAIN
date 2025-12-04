from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI(title="Customer Support Data API")

CSV_FILE = "RegistrosCall.csv"

# ---- cargamos el CSV una vez ----
dataframe = None

def load_csv():
    global dataframe
    try:
        df = pd.read_csv(
            CSV_FILE,
            sep=",",
            engine="python",
            encoding="utf-8",
            on_bad_lines="skip"
        )

        df = df.where(pd.notnull(df), None)  # quitar NaN
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
