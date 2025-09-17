from fastapi import FastAPI, HTTPException
import pandas as pd
import os

app = FastAPI()

CSV_PATH = "data/CONSUMO.csv"

# 📄 Endpoint para visualizar todos los datos
@app.get("/consumo", summary="Get all data from CONSUMO.csv")
def get_consumo():
    if not os.path.exists(CSV_PATH):
        raise HTTPException(status_code=404, detail="CSV file not found")
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {str(e)}")
    
    return df.to_dict(orient="records")


    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(EXCEL_PATH, index=False)
    return {"message": "User added successfully", "data": new_row}

