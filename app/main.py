from fastapi import FastAPI, HTTPException
import pandas as pd
import os

app = FastAPI()

CSV_PATH = "data/users_data_2_test.csv"

# 📄 Endpoint para visualizar todos los datos del archivo users_data_2_test.csv
@app.get("/users", summary="Get all user data from users_data_2_test.csv")
def get_users():
    if not os.path.exists(CSV_PATH):
        raise HTTPException(status_code=404, detail="CSV file not found")
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {str(e)}")
    
    return df.to_dict(orient="records")
