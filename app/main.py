from fastapi import FastAPI
import pandas as pd

app = FastAPI()

@app.get("/llamadas", summary="Get call records from Excel")
def get_llamadas():
    df = pd.read_excel("data/BaseDeDatosUANLAGENT.xlsx")
    return df.to_dict(orient="records")
